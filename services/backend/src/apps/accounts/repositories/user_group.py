from typing import Optional, List

from apps.accounts.dto.users import UserGroupDTO
from apps.accounts.interfaces.repositories import UserGroupRepositoryInterface
from apps.accounts.repositories.base import BaseRepository
from db.interfaces import DAOInterface, SQLQueryBuilderInterface


class UserGroupRepository(BaseRepository, UserGroupRepositoryInterface):
    """Repository implementation for user group operations using SQL database"""

    def __init__(self, dao: DAOInterface, query_builder: SQLQueryBuilderInterface):
        super().__init__(dao, query_builder)

    async def get_all_groups(self) -> List[UserGroupDTO]:
        """Get all user groups"""
        self._build_group_query()
        self._query_builder.order_by("id")

        results = await self._execute_query_multiple("Get all groups")
        return [self.map_to_group_dto(row) for row in results]

    async def get_group_by_id(self, group_id: int) -> Optional[UserGroupDTO]:
        """Get user group by ID"""
        self._build_group_query()
        self._query_builder.where("id = %s", group_id)

        result = await self._execute_query_single("Get group by ID")
        return self.map_to_group_dto(result) if result else None

    async def get_group_by_name(self, name: str) -> Optional[UserGroupDTO]:
        """Get user group by name"""
        self._build_group_query()
        self._query_builder.where("name = %s", name)

        result = await self._execute_query_single("Get group by name")
        return self.map_to_group_dto(result) if result else None

    def _build_group_query(self) -> None:
        """Build base group query"""
        self._query_builder.reset().select("id", "name")
