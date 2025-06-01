from typing import Optional, ClassVar, Dict, Tuple

from async_lru import alru_cache

from apps.catalog.dto.category import (
    CategoryMenuDTO,
    MasterCategoryInfoDTO,
    SubCategoryInfoDTO,
    ArticleTypeInfoDTO
)
from apps.catalog.interfaces.repositories import CategoryRepositoryInterface
from db.interfaces import DAOInterface
from settings.logging_config import get_logger

logger = get_logger(__name__, "app")


class CategoryRepository(CategoryRepositoryInterface):
    APP_NAME = "catalog"
    _instances: ClassVar[Dict[str, 'CategoryRepository']] = {}

    def __init__(self, dao: DAOInterface):
        self._dao = dao

    @classmethod
    def get_instance(cls, dao: DAOInterface) -> 'CategoryRepository':
        """
        Get or create a singleton instance of the repository

        Args:
            dao: Data Access Object

        Returns:
            Repository instance
        """
        key = str(id(dao))
        if key not in cls._instances:
            cls._instances[key] = cls(dao)
        return cls._instances[key]

    @alru_cache(maxsize=1, ttl=3600)
    async def get_category_menu(self) -> CategoryMenuDTO:
        """
        Get the complete category menu structure with all master categories,
        subcategories and article types.

        Returns:
            CategoryMenuDTO: The complete category hierarchy
        """
        menu_query = self._get_category_query()
        logger.info(f"Complete menu query: {menu_query}")

        menu_result = await self._dao.execute(menu_query, [])

        if not menu_result:
            return CategoryMenuDTO(categories=[])

        master_categories = {}

        for row in menu_result:
            master_id, master_name, sub_id, sub_name, article_id, article_name = self._extract_row_data(row)

            if master_id not in master_categories:
                master_categories[master_id] = MasterCategoryInfoDTO(
                    master_category_id=master_id,
                    name=master_name,
                    sub_categories=[]
                )

            if sub_id is not None:
                master_category = master_categories[master_id]
                subcategory = self._find_subcategory_in_master(master_category, sub_id)

                if subcategory is None:
                    subcategory = self._add_subcategory_to_master(master_category, sub_id, sub_name)

                if article_id is not None:
                    self._add_article_type_to_subcategory(subcategory, article_id, article_name)

        categories = list(master_categories.values())
        return CategoryMenuDTO(categories=categories)

    async def get_master_category_by_id(self, master_category_id: int) -> Optional[MasterCategoryInfoDTO]:
        """
        Get a single master category with its subcategories and article types

        Args:
            master_category_id: The ID of the master category to retrieve

        Returns:
            Optional[MasterCategoryInfoDTO]: The master category with its hierarchy or None if not found
        """
        category_query = self._get_category_query(master_category_id)

        logger.info(f"Master category by ID query: {category_query}")
        logger.info(f"Master category by ID params: [{master_category_id}]")

        category_result = await self._dao.execute(category_query, [master_category_id])

        if not category_result:
            return None

        master_id, master_name, _, _, _, _ = self._extract_row_data(category_result[0])

        master_category = MasterCategoryInfoDTO(
            master_category_id=master_id,
            name=master_name,
            sub_categories=[]
        )

        subcategories = {}

        for row in category_result:
            _, _, sub_id, sub_name, article_id, article_name = self._extract_row_data(row)

            if sub_id is not None:
                if sub_id not in subcategories:
                    subcategory = self._add_subcategory_to_master(master_category, sub_id, sub_name)
                    subcategories[sub_id] = subcategory

                if article_id is not None:
                    self._add_article_type_to_subcategory(subcategories[sub_id], article_id, article_name)

        return master_category

    def _get_category_query(self, master_category_id: Optional[int] = None) -> str:
        """
        Generate SQL query for retrieving category data

        Args:
            master_category_id: Optional master category ID to filter by

        Returns:
            SQL query string
        """
        query = f"""
            SELECT 
                mc.master_category_id,
                mc.name as master_name,
                sc.sub_category_id,
                sc.name as sub_name,
                at.article_type_id,
                at.name as article_name
            FROM 
                {self.APP_NAME}_master_category mc
            LEFT JOIN 
                {self.APP_NAME}_sub_category sc ON mc.master_category_id = sc.master_category_id
            LEFT JOIN 
                {self.APP_NAME}_article_type at ON sc.sub_category_id = at.sub_category_id
        """

        if master_category_id is not None:
            query += f" WHERE mc.master_category_id = %s"

        query += " ORDER BY mc.name, sc.name, at.name"

        return query

    def _extract_row_data(self, row: Tuple) -> Tuple[
        int, str, Optional[int], Optional[str], Optional[int], Optional[str]]:
        """
        Extract and normalize data from a database row

        Args:
            row: Database result row

        Returns:
            Tuple of (master_id, master_name, sub_id, sub_name, article_id, article_name)
        """
        master_id = int(row[0])
        master_name = row[1]
        sub_id = int(row[2]) if row[2] is not None else None
        sub_name = row[3]
        article_id = int(row[4]) if row[4] is not None else None
        article_name = row[5]

        return master_id, master_name, sub_id, sub_name, article_id, article_name

    def _add_article_type_to_subcategory(
            self,
            subcategory: SubCategoryInfoDTO,
            article_id: int,
            article_name: str
    ) -> None:
        """
        Add article type to subcategory if it doesn't exist

        Args:
            subcategory: Subcategory to add article type to
            article_id: Article type ID
            article_name: Article type name
        """
        article_type = ArticleTypeInfoDTO(
            article_type_id=article_id,
            name=article_name
        )

        if not any(at.id == article_id for at in subcategory.article_types):
            subcategory.article_types.append(article_type)

    def _find_subcategory_in_master(
            self,
            master_category: MasterCategoryInfoDTO,
            sub_id: int
    ) -> Optional[SubCategoryInfoDTO]:
        """
        Find subcategory in master category by ID

        Args:
            master_category: Master category to search in
            sub_id: Subcategory ID to find

        Returns:
            Subcategory if found, None otherwise
        """
        return next(
            (sc for sc in master_category.sub_categories if sc.id == sub_id),
            None
        )

    def _add_subcategory_to_master(
            self,
            master_category: MasterCategoryInfoDTO,
            sub_id: int,
            sub_name: str
    ) -> SubCategoryInfoDTO:
        """
        Add new subcategory to master category

        Args:
            master_category: Master category to add subcategory to
            sub_id: Subcategory ID
            sub_name: Subcategory name

        Returns:
            Created subcategory
        """
        subcategory = SubCategoryInfoDTO(
            sub_category_id=sub_id,
            name=sub_name,
            article_types=[]
        )
        master_category.sub_categories.append(subcategory)
        return subcategory
