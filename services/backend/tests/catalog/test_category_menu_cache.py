from typing import Any, List, Optional

import pytest

from apps.catalog.repositories.category import CategoryRepository

MENU_ROW = (1, "Apparel", 10, "Topwear", 100, "Shirts")


class CountingDAO:
    """DAO counting how many times the menu was actually read"""

    def __init__(self):
        self.reads = 0

    async def execute(self, query: str, params: Optional[List[Any]] = None, **kwargs: Any) -> List[tuple]:
        """Count the read and return one menu row"""
        self.reads += 1
        return [MENU_ROW]


@pytest.fixture(autouse=True)
def clean_cache():
    """Keep the process-wide menu cache out of neighbouring tests"""
    CategoryRepository.reset_menu_cache()
    yield
    CategoryRepository.reset_menu_cache()


async def test_the_menu_is_read_once_for_the_whole_process():
    """A second request reuses the cached menu instead of querying again"""
    first_dao, second_dao = CountingDAO(), CountingDAO()

    first_menu = await CategoryRepository(first_dao).get_category_menu()
    second_menu = await CategoryRepository(second_dao).get_category_menu()

    assert first_dao.reads == 1
    assert second_dao.reads == 0
    assert second_menu == first_menu


async def test_an_expired_cache_is_read_again(monkeypatch):
    """Once the entry is older than its lifetime the menu is fetched again"""
    monkeypatch.setattr(CategoryRepository, "MENU_CACHE_TTL_SECONDS", 0)
    dao = CountingDAO()
    repository = CategoryRepository(dao)

    await repository.get_category_menu()
    await repository.get_category_menu()

    assert dao.reads == 2


async def test_the_cache_survives_a_new_repository_for_each_request():
    """Ten requests, each with its own repository and DAO, read the menu once"""
    daos = [CountingDAO() for _ in range(10)]

    for dao in daos:
        await CategoryRepository(dao).get_category_menu()

    assert sum(dao.reads for dao in daos) == 1


async def test_repositories_are_not_retained_between_requests():
    """The class keeps no registry of repositories, so none of them leak"""
    assert not [
        attribute for attribute, value in vars(CategoryRepository).items()
        if isinstance(value, dict) and any(isinstance(item, CategoryRepository) for item in value.values())
    ]
