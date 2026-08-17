from typing import Optional, List, Any, Tuple

from apps.catalog.interfaces.specifications import CategorySpecificationInterface
from apps.catalog.specifications.clauses import PRODUCT_ALIAS, SqlClause


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

    def to_clause(self) -> SqlClause:
        """
        Build the joins and predicates selecting one branch of the category tree

        Returns:
            Joins and conditions with the identifiers they bind
        """
        joins = [
            f"JOIN {self.APP_NAME}_article_type at "
            f"ON {PRODUCT_ALIAS}.article_type_id = at.article_type_id",
            f"JOIN {self.APP_NAME}_sub_category sc ON at.sub_category_id = sc.sub_category_id",
            f"JOIN {self.APP_NAME}_master_category mc ON sc.master_category_id = mc.master_category_id"
        ]

        conditions = ["mc.master_category_id = %s"]
        params: List[Any] = [self._master_id]

        if self._sub_id is not None:
            conditions.append("sc.sub_category_id = %s")
            params.append(self._sub_id)

        if self._article_id is not None:
            conditions.append("at.article_type_id = %s")
            params.append(self._article_id)

        return SqlClause(conditions=conditions, params=params, joins=joins)
