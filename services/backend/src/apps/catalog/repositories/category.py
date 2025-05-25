from typing import Optional, List
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

    def __init__(self, dao: DAOInterface):
        self._dao = dao

    @alru_cache(maxsize=1, ttl=3600)
    async def get_category_menu(self) -> CategoryMenuDTO:
        """
        Get the complete category menu structure with all master categories,
        subcategories and article types.

        Returns:
            CategoryMenuDTO: The complete category hierarchy
        """
        master_categories_query = f"""
            SELECT master_category_id, name 
            FROM {self.APP_NAME}_master_category
            ORDER BY name
        """
        logger.info(f"Master categories query: {master_categories_query}")
        master_categories_result = await self._dao.execute(master_categories_query, [])

        if not master_categories_result:
            return CategoryMenuDTO(categories=[])

        categories = []

        for master_row in master_categories_result:
            master_id = int(master_row[0])
            master_name = master_row[1]

            master_category = await self._build_master_category(master_id, master_name)
            categories.append(master_category)

        return CategoryMenuDTO(categories=categories)

    async def get_master_category_by_id(self, master_category_id: int) -> Optional[MasterCategoryInfoDTO]:
        """
        Get a single master category with its subcategories and article types

        Args:
            master_category_id: The ID of the master category to retrieve

        Returns:
            Optional[MasterCategoryInfoDTO]: The master category with its hierarchy or None if not found
        """
        master_category_query = f"""
            SELECT master_category_id, name 
            FROM {self.APP_NAME}_master_category
            WHERE master_category_id = %s
        """
        logger.info(f"Master category by ID query: {master_category_query}")
        logger.info(f"Master category by ID params: [{master_category_id}]")

        master_category_result = await self._dao.execute(
            master_category_query, [master_category_id], fetch_one=True
        )

        if not master_category_result:
            return None

        master_id = master_category_result[0]
        master_name = master_category_result[1]

        return await self._build_master_category(master_id, master_name)

    async def _build_master_category(self, master_id: int, master_name: str) -> MasterCategoryInfoDTO:
        """
        Build a master category DTO with its subcategories and article types

        Args:
            master_id: ID of the master category
            master_name: Name of the master category

        Returns:
            MasterCategoryInfoDTO with populated subcategories and article types
        """
        master_category = MasterCategoryInfoDTO(
            master_category_id=int(master_id),
            name=master_name,
            sub_categories=[]
        )

        sub_categories = await self._get_subcategories_for_master(master_id)
        master_category.sub_categories = sub_categories

        return master_category

    async def _get_subcategories_for_master(self, master_id: int) -> List[SubCategoryInfoDTO]:
        """
        Get all subcategories for a master category with their article types

        Args:
            master_id: ID of the master category

        Returns:
            List of SubCategoryInfoDTO objects with populated article types
        """
        sub_categories_query = f"""
            SELECT sub_category_id, name 
            FROM {self.APP_NAME}_sub_category
            WHERE master_category_id = %s
            ORDER BY name
        """
        logger.info(f"Subcategories for master category query: {sub_categories_query}")
        logger.info(f"Subcategories for master category params: [{master_id}]")

        sub_categories_result = await self._dao.execute(
            sub_categories_query, [master_id]
        )

        if not sub_categories_result:
            return []

        sub_categories = []
        for sub_row in sub_categories_result:
            sub_id = int(sub_row[0])
            sub_name = sub_row[1]

            sub_category = await self._build_subcategory(sub_id, sub_name)
            sub_categories.append(sub_category)

        return sub_categories

    async def _build_subcategory(self, sub_id: int, sub_name: str) -> SubCategoryInfoDTO:
        """
        Build a subcategory DTO with its article types

        Args:
            sub_id: ID of the subcategory
            sub_name: Name of the subcategory

        Returns:
            SubCategoryInfoDTO with populated article types
        """
        sub_category = SubCategoryInfoDTO(
            sub_category_id=sub_id,
            name=sub_name,
            article_types=[]
        )

        article_types = await self._get_article_types_for_subcategory(sub_id)
        sub_category.article_types = article_types

        return sub_category

    async def _get_article_types_for_subcategory(self, sub_id: int) -> List[ArticleTypeInfoDTO]:
        """
        Get all article types for a subcategory

        Args:
            sub_id: ID of the subcategory

        Returns:
            List of ArticleTypeInfoDTO objects
        """
        article_types_query = f"""
            SELECT article_type_id, name 
            FROM {self.APP_NAME}_article_type
            WHERE sub_category_id = %s
            ORDER BY name
        """
        logger.info(f"Article types for subcategory query: {article_types_query}")
        logger.info(f"Article types for subcategory params: [{sub_id}]")

        article_types_result = await self._dao.execute(
            article_types_query, [sub_id]
        )

        if not article_types_result:
            return []

        return [
            ArticleTypeInfoDTO(
                article_type_id=int(article_row[0]),
                name=article_row[1]
            )
            for article_row in article_types_result
        ]
