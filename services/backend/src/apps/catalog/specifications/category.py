from typing import Optional, List, Any, Tuple

from apps.catalog.interfaces.specifications import CategorySpecificationInterface


class CategorySpecification(CategorySpecificationInterface):
    """Specification for filtering products by category hierarchy"""

    APP_NAME = "catalog"

    def __init__(
            self,
            master_category_id: int,
            sub_category_id: Optional[int] = None,
            article_type_id: Optional[int] = None
    ):
        self._master_id = master_category_id
        self._sub_id = sub_category_id
        self._article_id = article_type_id


    def is_empty(self) -> bool:
        """Check if specification is empty"""
        return self._master_id is None

    def to_sql(self) -> Tuple[str, List[Any]]:
        """
        Convert to SQL parts for joining and filtering by categories

        Returns:
            Tuple[str, List[Any]]: SQL part (joins + conditions), list of parameters
        """
        joins = []
        conditions = []
        params = []

        joins.append(
            f"JOIN {self.APP_NAME}_article_type at ON {self.APP_NAME}_products.article_type_id = at.article_type_id"
        )
        joins.append(f"JOIN {self.APP_NAME}_sub_category sc ON at.sub_category_id = sc.sub_category_id")
        joins.append(f"JOIN {self.APP_NAME}_master_category mc ON sc.master_category_id = mc.master_category_id")

        conditions.append("mc.master_category_id = %s")
        params.append(self._master_id)

        if self._sub_id is not None:
            conditions.append("sc.sub_category_id = %s")
            params.append(self._sub_id)

        if self._article_id is not None:
            conditions.append("at.article_type_id = %s")
            params.append(self._article_id)

        sql_part = " ".join(joins) + " WHERE " + " AND ".join(conditions)

        return sql_part, params
