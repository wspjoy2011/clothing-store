from typing import Any, List, Optional

from apps.catalog.repositories.product import ProductRepository
from apps.catalog.specifications.filtering import ProductFilterSpecification
from apps.catalog.specifications.search import ProductSearchSpecification
from db.query_builder import SQLQueryBuilder

COUNT = 42


class RecordingDAO:
    """DAO recording the statements it was asked to run"""

    def __init__(self):
        self.queries: List[str] = []

    async def execute(self, query: str, params: Optional[List[Any]] = None, **kwargs: Any) -> List[int]:
        """Record the statement and report a count"""
        self.queries.append(query)
        return [COUNT]


def build_repository() -> tuple:
    """
    Assemble a product repository over a recording DAO

    Returns:
        Repository and the DAO behind it
    """
    dao = RecordingDAO()
    return ProductRepository(dao, SQLQueryBuilder("catalog_products")), dao


def price_filter() -> ProductFilterSpecification:
    """Build a filter that reads inventory columns"""
    specification = ProductFilterSpecification()
    specification.set_price_range(min_price=10)
    return specification


def gender_filter() -> ProductFilterSpecification:
    """Build a filter that reads product columns only"""
    specification = ProductFilterSpecification()
    specification.set_genders("Men")
    return specification


async def test_an_unfiltered_count_does_not_join_the_inventory():
    """The inventory row is unique per product, so the join cannot change the count"""
    repository, dao = build_repository()

    await repository.get_products_count()

    assert "JOIN" not in dao.queries[0]


async def test_a_count_filtered_on_price_joins_the_inventory():
    """A filter reading inventory columns still gets its join"""
    repository, dao = build_repository()

    await repository.get_products_count(filter_spec=price_filter())

    assert "JOIN catalog_product_inventory" in dao.queries[0]


async def test_a_count_filtered_on_gender_does_not_join_the_inventory():
    """Filtering on product columns alone needs no second table"""
    repository, dao = build_repository()

    await repository.get_products_count(filter_spec=gender_filter())

    assert "JOIN" not in dao.queries[0]
    assert "p.gender" in dao.queries[0]


async def test_a_searched_count_does_not_join_the_inventory():
    """Search reads product columns, so counting matches needs no join"""
    repository, dao = build_repository()

    await repository.get_products_count(search_spec=ProductSearchSpecification("shirt"))

    assert "JOIN" not in dao.queries[0]


async def test_the_count_is_the_number_the_database_reported():
    """The repository reports the count it read, not a derived value"""
    repository, _ = build_repository()

    assert await repository.get_products_count() == COUNT
