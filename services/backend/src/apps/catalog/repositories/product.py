from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from apps.catalog.dto.filters import (
    AvailabilityFilterDTO,
    CheckboxFilterDTO,
    FiltersDTO,
    PriceRangeFilterDTO,
    RangeFilterDTO,
)
from apps.catalog.dto.products import InventoryDTO, InventoryHoldDTO, ProductDTO
from apps.catalog.interfaces.repositories import ProductRepositoryInterface
from apps.catalog.interfaces.specifications import (
    CategorySpecificationInterface,
    FilterSpecificationInterface,
    OrderingSpecificationInterface,
    PaginationSpecificationInterface,
    SearchSpecificationInterface,
)
from apps.catalog.specifications.clauses import EFFECTIVE_PRICE, INVENTORY_ALIAS, PRODUCT_ALIAS, SqlClause
from db.interfaces import DAOInterface
from db.transaction import NoActiveTransactionError, get_current_transaction
from settings.logging_config import get_logger

logger = get_logger(__name__, "app")

# Projection
PRODUCT_COLUMNS = (
    f"{PRODUCT_ALIAS}.product_id",
    f"{PRODUCT_ALIAS}.gender",
    f"{PRODUCT_ALIAS}.year",
    f"{PRODUCT_ALIAS}.product_display_name",
    f"{PRODUCT_ALIAS}.image_url",
    f"{PRODUCT_ALIAS}.slug",
    f"{INVENTORY_ALIAS}.id",
    f"{INVENTORY_ALIAS}.base_price",
    f"{INVENTORY_ALIAS}.sale_price",
    f"{INVENTORY_ALIAS}.currency",
    f"{INVENTORY_ALIAS}.stock_quantity",
    f"{INVENTORY_ALIAS}.reserved_quantity",
    f"{INVENTORY_ALIAS}.available_quantity",
    f"{INVENTORY_ALIAS}.is_active",
    f"{INVENTORY_ALIAS}.is_in_stock",
    f"{INVENTORY_ALIAS}.created_at",
    f"{INVENTORY_ALIAS}.updated_at"
)

AVAILABLE_CONDITION = f"({INVENTORY_ALIAS}.is_active AND {INVENTORY_ALIAS}.is_in_stock)"
UNAVAILABLE_CONDITION = (
    f"(NOT {INVENTORY_ALIAS}.is_active OR NOT {INVENTORY_ALIAS}.is_in_stock "
    f"OR {INVENTORY_ALIAS}.id IS NULL)"
)


class ProductRepository(ProductRepositoryInterface):
    """Repository implementation for product operations using SQL database

    Every read is rendered from one template: a projection, the product table with
    its inventory, the joins and conditions the specifications contributed, and the
    ordering. Specifications hand over predicates with their parameters, so no step
    has to take a fragment apart or rewrite its column names.
    """

    APP_NAME = "catalog"

    def __init__(self, dao: DAOInterface):
        """
        Initialize product repository

        Args:
            dao: Data Access Object for database operations
        """
        self._dao = dao

    @property
    def _products_table(self) -> str:
        """Products table with the alias every condition is written against"""
        return f"{self.APP_NAME}_products {PRODUCT_ALIAS}"

    @property
    def _inventory_join(self) -> str:
        """Join bringing in the inventory row of a product"""
        return (
            f"LEFT JOIN {self.APP_NAME}_product_inventory {INVENTORY_ALIAS} "
            f"ON {PRODUCT_ALIAS}.product_id = {INVENTORY_ALIAS}.product_id"
        )

    async def lock_inventory(self, product_id: int) -> Optional[InventoryHoldDTO]:
        """
        Read the inventory row of a product and hold it for the current transaction

        Only the single row is locked, found through the unique index on product_id,
        so concurrent work on other products is unaffected. Outside a transaction the
        lock is released as soon as the statement returns.

        Args:
            product_id: The ID of the product whose inventory is needed

        Returns:
            State of the held row, or None when the product has no inventory row

        Raises:
            NoActiveTransactionError: If called outside a transaction
        """
        if get_current_transaction() is None:
            raise NoActiveTransactionError(
                "lock_inventory must run inside a transaction: outside one the lock is "
                "released as soon as the statement returns, and the answer goes stale "
                "before the caller can act on it"
            )

        query = f"""
            SELECT is_active, is_in_stock, available_quantity
            FROM {self.APP_NAME}_product_inventory
            WHERE product_id = %s
            FOR UPDATE
        """

        result = await self._dao.execute(query, [product_id], fetch_one=True)

        if not result:
            logger.info(f"No inventory row to lock for product {product_id}")
            return None

        is_active, is_in_stock, available_quantity = tuple(result)
        return InventoryHoldDTO(
            is_active=is_active,
            is_in_stock=is_in_stock,
            available_quantity=available_quantity
        )

    async def get_product_by_id(self, product_id: int) -> Optional[ProductDTO]:
        """
        Get a single product by its ID

        Args:
            product_id: The ID of the product to retrieve

        Returns:
            ProductDTO if found, None otherwise
        """
        return await self._get_one_product(f"{PRODUCT_ALIAS}.product_id = %s", product_id)

    async def get_product_by_slug(self, slug: str) -> Optional[ProductDTO]:
        """
        Get a single product by its slug

        Args:
            slug: The slug of the product to retrieve

        Returns:
            ProductDTO if found, None otherwise
        """
        return await self._get_one_product(f"{PRODUCT_ALIAS}.slug = %s", slug)

    async def get_products_with_specifications(
            self,
            pagination_spec: PaginationSpecificationInterface,
            ordering_spec: Optional[OrderingSpecificationInterface] = None,
            filter_spec: Optional[FilterSpecificationInterface] = None,
            search_spec: Optional[SearchSpecificationInterface] = None
    ) -> List[ProductDTO]:
        """
        Get products using pagination, ordering, and filtering specifications

        Args:
            pagination_spec: Specification for pagination
            ordering_spec: Optional specification for ordering results
            filter_spec: Optional specification for filtering results
            search_spec: Optional specification for search

        Returns:
            List of product DTOs
        """
        return await self._list_products(pagination_spec, ordering_spec, filter_spec, search_spec)

    async def get_products_with_specifications_by_categories(
            self,
            category_spec: CategorySpecificationInterface,
            pagination_spec: PaginationSpecificationInterface,
            ordering_spec: Optional[OrderingSpecificationInterface] = None,
            filter_spec: Optional[FilterSpecificationInterface] = None,
            search_spec: Optional[SearchSpecificationInterface] = None
    ) -> List[ProductDTO]:
        """
        Get products filtered by category and other specifications

        Args:
            category_spec: Specification for category filtering
            pagination_spec: Specification for pagination
            ordering_spec: Optional specification for ordering results
            filter_spec: Optional specification for filtering results
            search_spec: Optional specification for search

        Returns:
            List of product DTOs
        """
        return await self._list_products(
            pagination_spec, ordering_spec, filter_spec, search_spec, category_spec
        )

    async def get_products_count(
            self,
            filter_spec: Optional[FilterSpecificationInterface] = None,
            search_spec: Optional[SearchSpecificationInterface] = None
    ) -> int:
        """
        Get total count of products, optionally filtered and searched

        Args:
            filter_spec: Optional specification for filtering results
            search_spec: Optional specification for search

        Returns:
            Number of products in the database
        """
        return await self._count_products(filter_spec, search_spec)

    async def get_products_count_by_categories(
            self,
            category_spec: CategorySpecificationInterface,
            filter_spec: Optional[FilterSpecificationInterface] = None,
            search_spec: Optional[SearchSpecificationInterface] = None
    ) -> int:
        """
        Get count of products filtered by category and other specifications

        Args:
            category_spec: Specification for category filtering
            filter_spec: Optional specification for filtering results
            search_spec: Optional specification for search

        Returns:
            Number of products matching the criteria
        """
        return await self._count_products(filter_spec, search_spec, category_spec)

    async def get_available_filters(
            self,
            search_spec: Optional[SearchSpecificationInterface] = None
    ) -> Optional[FiltersDTO]:
        """
        Get available filters and their ranges, optionally limited to a search

        Args:
            search_spec: Optional search specification narrowing the options

        Returns:
            FiltersDTO with the available options, or None when nothing matches
        """
        return await self._describe_filters(search_spec=search_spec)

    async def get_available_filters_by_categories(
            self,
            category_spec: CategorySpecificationInterface
    ) -> Optional[FiltersDTO]:
        """
        Get available filters and their ranges within one category branch

        Args:
            category_spec: Specification for category filtering

        Returns:
            FiltersDTO with the available options, or None when nothing matches
        """
        return await self._describe_filters(category_spec=category_spec)

    def _collect_clause(
            self,
            filter_spec: Optional[FilterSpecificationInterface] = None,
            search_spec: Optional[SearchSpecificationInterface] = None,
            category_spec: Optional[CategorySpecificationInterface] = None
    ) -> SqlClause:
        """
        Gather the conditions of every specification that narrows the result

        Args:
            filter_spec: Optional specification for filtering results
            search_spec: Optional specification for search
            category_spec: Optional specification for category filtering

        Returns:
            Combined joins, conditions and parameters
        """
        clause = SqlClause()

        for specification in (category_spec, filter_spec, search_spec):
            if specification is not None and not specification.is_empty():
                clause = clause.merge(specification.to_clause())

        return clause

    @staticmethod
    def _order_by(
            ordering_spec: Optional[OrderingSpecificationInterface],
            search_spec: Optional[SearchSpecificationInterface]
    ) -> Tuple[List[str], List[Any]]:
        """
        Decide the order of results and the parameters it binds

        Relevance leads only when the client asked for no particular order.
        Ranking first regardless would make a requested sort a no-op, because a
        relevance score almost never ties.

        Args:
            ordering_spec: Optional specification for ordering results
            search_spec: Optional specification for search

        Returns:
            Ordering expressions and their parameters
        """
        requested = ordering_spec.to_order_by() if ordering_spec is not None else []
        relevance, relevance_params = (
            search_spec.relevance_order() if search_spec is not None and not search_spec.is_empty()
            else ("", [])
        )

        if not relevance:
            return requested, []

        if ordering_spec is None or ordering_spec.is_default:
            return [relevance, *requested], relevance_params

        return [*requested, relevance], relevance_params

    def _render(
            self,
            projection: str,
            clause: SqlClause,
            order_by: Optional[List[str]] = None,
            group_by: Optional[str] = None,
            join_inventory: bool = True
    ) -> str:
        """
        Render one statement from the template every read shares

        Args:
            projection: Columns or aggregates to select
            clause: Joins and conditions to apply
            order_by: Optional ordering expressions
            group_by: Optional grouping expression
            join_inventory: Whether the inventory row is needed

        Returns:
            Complete statement without its pagination
        """
        parts = [f"SELECT {projection}", f"FROM {self._products_table}"]

        if join_inventory:
            parts.append(self._inventory_join)

        parts.extend(clause.joins)

        if clause.conditions:
            parts.append(f"WHERE {' AND '.join(clause.conditions)}")

        if group_by:
            parts.append(f"GROUP BY {group_by}")

        if order_by:
            parts.append(f"ORDER BY {', '.join(order_by)}")

        return "\n".join(parts)

    async def _get_one_product(self, condition: str, value: Any) -> Optional[ProductDTO]:
        """
        Read one product by a single condition

        Args:
            condition: Condition selecting the product
            value: Value the condition binds

        Returns:
            ProductDTO if found, None otherwise
        """
        query = self._render(", ".join(PRODUCT_COLUMNS), SqlClause(conditions=[condition]))
        result = await self._dao.execute(query, [value], fetch_one=True)

        if not result:
            return None

        return self._build_product_dto_from_row(tuple(result))

    async def _list_products(
            self,
            pagination_spec: PaginationSpecificationInterface,
            ordering_spec: Optional[OrderingSpecificationInterface] = None,
            filter_spec: Optional[FilterSpecificationInterface] = None,
            search_spec: Optional[SearchSpecificationInterface] = None,
            category_spec: Optional[CategorySpecificationInterface] = None
    ) -> List[ProductDTO]:
        """
        Read one page of products matching the specifications

        Args:
            pagination_spec: Specification for pagination
            ordering_spec: Optional specification for ordering results
            filter_spec: Optional specification for filtering results
            search_spec: Optional specification for search
            category_spec: Optional specification for category filtering

        Returns:
            List of product DTOs
        """
        clause = self._collect_clause(filter_spec, search_spec, category_spec)
        order_by, order_params = self._order_by(ordering_spec, search_spec)

        query = f"{self._render(', '.join(PRODUCT_COLUMNS), clause, order_by)}\nLIMIT %s OFFSET %s"
        params = [*clause.params, *order_params, pagination_spec.get_limit(), pagination_spec.get_offset()]

        logger.info(f"Products query: {query}")

        result = await self._dao.execute(query, params)

        if not result:
            return []

        return [self._build_product_dto_from_row(tuple(row)) for row in result]

    async def _count_products(
            self,
            filter_spec: Optional[FilterSpecificationInterface] = None,
            search_spec: Optional[SearchSpecificationInterface] = None,
            category_spec: Optional[CategorySpecificationInterface] = None
    ) -> int:
        """
        Count the products matching the specifications

        The inventory row is unique per product, so joining it cannot change the
        count: it is joined only when a condition reads its columns.

        Args:
            filter_spec: Optional specification for filtering results
            search_spec: Optional specification for search
            category_spec: Optional specification for category filtering

        Returns:
            Number of products matching the criteria
        """
        clause = self._collect_clause(filter_spec, search_spec, category_spec)
        query = self._render(
            "COUNT(*)",
            clause,
            join_inventory=self._reads_inventory(clause)
        )

        result = await self._dao.execute(query, clause.params, fetch_one=True)
        return result[0] if result else 0

    @staticmethod
    def _reads_inventory(clause: SqlClause) -> bool:
        """
        Report whether any condition reads inventory columns

        Args:
            clause: Conditions gathered from the specifications

        Returns:
            True when the inventory row has to be joined
        """
        return any(f"{INVENTORY_ALIAS}." in condition for condition in clause.conditions)

    async def _describe_filters(
            self,
            search_spec: Optional[SearchSpecificationInterface] = None,
            category_spec: Optional[CategorySpecificationInterface] = None
    ) -> Optional[FiltersDTO]:
        """
        Describe the filter options available within a scope

        The counts are computed against the same conditions the listing applies, so
        a figure shown next to a filter matches what selecting it returns.

        Args:
            search_spec: Optional search specification narrowing the scope
            category_spec: Optional category specification narrowing the scope

        Returns:
            FiltersDTO with the available options, or None when nothing matches
        """
        scope = self._collect_clause(search_spec=search_spec, category_spec=category_spec)

        if await self._count_in_scope(scope) == 0:
            return None

        gender_counts = await self._gender_counts(scope)
        min_year, max_year = await self._year_range(scope)
        min_price, max_price = await self._price_range(scope)
        available_count, unavailable_count = await self._availability_counts(scope)

        return FiltersDTO(
            gender=CheckboxFilterDTO(
                values=list(gender_counts.keys()),
                count=gender_counts
            ) if gender_counts else None,
            year=RangeFilterDTO(min=min_year, max=max_year) if min_year and max_year else None,
            price=PriceRangeFilterDTO(
                min=float(min_price),
                max=float(max_price)
            ) if min_price and max_price else None,
            is_available=AvailabilityFilterDTO(
                available_count=available_count,
                unavailable_count=unavailable_count
            )
        )

    async def _count_in_scope(self, scope: SqlClause) -> int:
        """
        Count the products inside a scope

        Args:
            scope: Conditions defining the scope

        Returns:
            Number of products in the scope
        """
        query = self._render("COUNT(*)", scope, join_inventory=self._reads_inventory(scope))
        result = await self._dao.execute(query, scope.params, fetch_one=True)
        return result[0] if result else 0

    async def _gender_counts(self, scope: SqlClause) -> Dict[str, int]:
        """
        Count the products of each gender inside a scope

        Args:
            scope: Conditions defining the scope

        Returns:
            Count per gender value
        """
        clause = scope.merge(SqlClause(conditions=[f"{PRODUCT_ALIAS}.gender IS NOT NULL"]))
        query = self._render(
            f"{PRODUCT_ALIAS}.gender, COUNT(*)",
            clause,
            group_by=f"{PRODUCT_ALIAS}.gender",
            join_inventory=self._reads_inventory(clause)
        )

        result = await self._dao.execute(query, clause.params)
        return {row[0]: row[1] for row in result} if result else {}

    async def _year_range(self, scope: SqlClause) -> Tuple[Optional[int], Optional[int]]:
        """
        Find the year range of the products inside a scope

        Args:
            scope: Conditions defining the scope

        Returns:
            Lowest and highest year, or None when no product carries one
        """
        clause = scope.merge(SqlClause(conditions=[f"{PRODUCT_ALIAS}.year IS NOT NULL"]))
        query = self._render(
            f"MIN({PRODUCT_ALIAS}.year), MAX({PRODUCT_ALIAS}.year)",
            clause,
            join_inventory=self._reads_inventory(clause)
        )

        result = await self._dao.execute(query, clause.params, fetch_one=True)
        return tuple(result) if result else (None, None)

    async def _price_range(self, scope: SqlClause) -> Tuple[Optional[Decimal], Optional[Decimal]]:
        """
        Find the price range of the products inside a scope

        Args:
            scope: Conditions defining the scope

        Returns:
            Lowest and highest effective price, or None when nothing is priced
        """
        clause = scope.merge(SqlClause(conditions=[f"{INVENTORY_ALIAS}.id IS NOT NULL"]))
        query = self._render(f"MIN({EFFECTIVE_PRICE}), MAX({EFFECTIVE_PRICE})", clause)

        result = await self._dao.execute(query, clause.params, fetch_one=True)
        return tuple(result) if result else (None, None)

    async def _availability_counts(self, scope: SqlClause) -> Tuple[int, int]:
        """
        Count the available and unavailable products inside a scope

        Availability is both flags at once, exactly as the listing filter defines
        it: counting on stock alone reported deactivated products as available and
        then returned fewer rows than the figure promised.

        Args:
            scope: Conditions defining the scope

        Returns:
            Available and unavailable counts
        """
        available = scope.merge(SqlClause(conditions=[AVAILABLE_CONDITION]))
        unavailable = scope.merge(SqlClause(conditions=[UNAVAILABLE_CONDITION]))

        return (
            await self._count_in_scope_with_inventory(available),
            await self._count_in_scope_with_inventory(unavailable)
        )

    async def _count_in_scope_with_inventory(self, clause: SqlClause) -> int:
        """
        Count products whose condition reads the inventory row

        Args:
            clause: Conditions including inventory columns

        Returns:
            Number of products matching
        """
        query = self._render("COUNT(*)", clause)
        result = await self._dao.execute(query, clause.params, fetch_one=True)
        return result[0] if result else 0

    def _build_product_dto_from_row(self, row: tuple) -> ProductDTO:
        """
        Build ProductDTO from database row including inventory data

        Args:
            row: Database result row, in the order of PRODUCT_COLUMNS

        Returns:
            ProductDTO with inventory data if available
        """
        product_id = int(row[0])

        inventory = None
        if row[6] is not None:
            inventory = InventoryDTO(
                id=int(row[6]),
                product_id=product_id,
                base_price=Decimal(str(row[7])),
                sale_price=Decimal(str(row[8])) if row[8] is not None else None,
                currency=row[9],
                stock_quantity=int(row[10]),
                reserved_quantity=int(row[11]),
                available_quantity=int(row[12]),
                is_active=bool(row[13]),
                is_in_stock=bool(row[14]),
                created_at=row[15],
                updated_at=row[16]
            )

        return ProductDTO(
            product_id=product_id,
            gender=row[1],
            year=int(row[2]) if row[2] is not None else None,
            product_display_name=row[3],
            image_url=row[4],
            slug=row[5],
            inventory=inventory
        )
