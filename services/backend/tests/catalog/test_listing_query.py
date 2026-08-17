from typing import Any, List, Optional

from apps.catalog.repositories.product import ProductRepository
from apps.catalog.specifications.category import CategorySpecification
from apps.catalog.specifications.filtering import ProductFilterSpecification
from apps.catalog.specifications.ordering import OrderingSpecification
from apps.catalog.specifications.pagination import PaginationSpecification
from apps.catalog.specifications.search import ProductSearchSpecification

PRICE = "COALESCE(i.sale_price, i.base_price)"


class RecordingDAO:
    """DAO recording statements and answering by the shape of the projection

    Aggregates are answered with as many values as they select, the way the database
    would: a stand-in that always returns one value hides a mismatch in unpacking.
    """

    def __init__(self, rows: Optional[List[Any]] = None):
        self.rows = rows
        self.queries: List[str] = []
        self.params: List[List[Any]] = []

    async def execute(self, query: str, params: Optional[List[Any]] = None, **kwargs: Any) -> Any:
        """Record the statement and answer in the shape it asked for"""
        self.queries.append(query)
        self.params.append(list(params or []))

        if self.rows is not None:
            return self.rows[0] if kwargs.get("fetch_one") and self.rows else self.rows

        answer = self._answer_for(query)
        return answer if kwargs.get("fetch_one") else [answer]

    @staticmethod
    def _answer_for(query: str) -> tuple:
        """
        Build an answer with one value per selected expression

        Args:
            query: Statement being answered

        Returns:
            Row shaped like the projection
        """
        projection = query.split("SELECT", 1)[1].split("FROM", 1)[0]
        return tuple(range(1, RecordingDAO._columns_in(projection) + 1))

    @staticmethod
    def _columns_in(projection: str) -> int:
        """
        Count the selected expressions, ignoring commas inside them

        Args:
            projection: Text between SELECT and FROM

        Returns:
            Number of columns the statement selects
        """
        depth = 0
        columns = 1

        for character in projection:
            if character == "(":
                depth += 1
            elif character == ")":
                depth -= 1
            elif character == "," and depth == 0:
                columns += 1

        return columns


def build_repository(rows: Optional[List[Any]] = None) -> tuple:
    """
    Assemble a product repository over a recording DAO

    Args:
        rows: Rows the DAO should answer with

    Returns:
        Repository and the DAO behind it
    """
    dao = RecordingDAO(rows)
    return ProductRepository(dao), dao


def price_filter(minimum: float = 10) -> ProductFilterSpecification:
    """Build a filter on the effective price"""
    specification = ProductFilterSpecification()
    specification.set_price_range(min_price=minimum)
    return specification


async def test_a_requested_sort_survives_a_search():
    """Sorting by price during a search sorts by price, with relevance behind it"""
    repository, dao = build_repository()

    await repository.get_products_with_specifications(
        pagination_spec=PaginationSpecification(1, 10),
        ordering_spec=OrderingSpecification("-price"),
        search_spec=ProductSearchSpecification("shirt")
    )

    order_by = dao.queries[0].split("ORDER BY", 1)[1]
    assert order_by.index(PRICE) < order_by.index("ts_rank")


async def test_relevance_leads_when_no_order_was_requested():
    """Without a requested sort a search is ranked by relevance first"""
    repository, dao = build_repository()

    await repository.get_products_with_specifications(
        pagination_spec=PaginationSpecification(1, 10),
        ordering_spec=OrderingSpecification(None),
        search_spec=ProductSearchSpecification("shirt")
    )

    order_by = dao.queries[0].split("ORDER BY", 1)[1]
    assert order_by.index("ts_rank") < order_by.index("p.product_id")


async def test_the_parameters_follow_the_order_of_the_placeholders():
    """Condition values come before the ordering value, as the statement reads them"""
    repository, dao = build_repository()

    await repository.get_products_with_specifications(
        pagination_spec=PaginationSpecification(2, 5),
        ordering_spec=OrderingSpecification("-price"),
        filter_spec=price_filter(minimum=42),
        search_spec=ProductSearchSpecification("shirt")
    )

    assert dao.params[0] == [42, "shirt", "shirt", 5, 5]


async def test_a_statement_carries_one_placeholder_per_parameter():
    """Every parameter has a placeholder, so psycopg is never handed a mismatch"""
    repository, dao = build_repository()

    await repository.get_products_with_specifications_by_categories(
        category_spec=CategorySpecification(1, 2, 3),
        pagination_spec=PaginationSpecification(1, 10),
        ordering_spec=OrderingSpecification("year"),
        filter_spec=price_filter(),
        search_spec=ProductSearchSpecification("shirt")
    )

    assert dao.queries[0].count("%s") == len(dao.params[0])


async def test_no_condition_names_a_table_that_is_not_joined():
    """Conditions are written against aliases the statement actually defines"""
    repository, dao = build_repository()

    await repository.get_products_with_specifications(
        pagination_spec=PaginationSpecification(1, 10),
        filter_spec=price_filter()
    )

    statement = dao.queries[0]
    assert "inventory." not in statement
    assert "catalog_product_inventory i" in statement


async def test_availability_counts_use_both_flags():
    """The count matches the filter: a deactivated product is not available"""
    repository, dao = build_repository()

    await repository.get_available_filters()

    availability_queries = [query for query in dao.queries if "is_active" in query]
    assert availability_queries
    for query in availability_queries:
        assert "is_in_stock" in query


async def test_the_available_count_and_the_filter_agree():
    """The condition counted as available is the one the filter applies"""
    repository, dao = build_repository()
    specification = ProductFilterSpecification()
    specification.set_availability(True)

    await repository.get_products_count(filter_spec=specification)
    filter_condition = dao.queries[0].split("WHERE", 1)[1].strip()

    dao.queries.clear()
    await repository.get_available_filters()
    counted = [query for query in dao.queries if filter_condition in query]

    assert counted
