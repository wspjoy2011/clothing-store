from typing import Self, Tuple, List, Any

from db.interfaces import SQLQueryBuilderInterface


class SQLQueryBuilder(SQLQueryBuilderInterface):
    """Builder for SQL queries with different parts"""

    def __init__(self, base_table: str):
        """Initialize with base table name"""
        self._base_table = base_table
        self._select_fields = []
        self._join_clauses = []
        self._where_conditions = []
        self._order_by_clauses = []
        self._params = []
        self._offset_value = None
        self._limit_value = None

    def select(self, *fields) -> Self:
        """Add fields to SELECT clause"""
        self._select_fields.extend(fields)
        return self

    def where(self, condition: str, *params) -> Self:
        """Add condition to WHERE clause with params"""
        if condition and condition.strip():
            self._where_conditions.append(condition)

        if params:
            self._params.extend(params)

        return self

    def order_by(self, clause: str, *params) -> Self:
        """Add clause to ORDER BY section with params"""
        if clause and clause.strip():
            self._order_by_clauses.append(clause)

        if params:
            self._params.extend(params)

        return self

    def limit(self, limit_value: int) -> Self:
        """Set LIMIT value"""
        self._limit_value = limit_value
        return self

    def offset(self, offset_value: int) -> Self:
        """Set OFFSET value"""
        self._offset_value = offset_value
        return self

    def build(self) -> Tuple[str, List[Any]]:
        """Build the final SQL query and params list"""
        query = f"SELECT {', '.join(self._select_fields) or '*'} FROM {self._base_table}"

        if self._join_clauses:
            query += f" {' '.join(self._join_clauses)}"

        if self._where_conditions:
            query += f" WHERE {' AND '.join(self._where_conditions)}"

        if self._order_by_clauses:
            query += f" ORDER BY {', '.join(self._order_by_clauses)}"

        params = self._params.copy()

        if self._limit_value is not None:
            query += f" LIMIT %s"
            params.append(self._limit_value)

        if self._offset_value is not None:
            query += f" OFFSET %s"
            params.append(self._offset_value)

        return query, params

    def build_count(self) -> Tuple[str, List[Any]]:
        """Build COUNT query with the same conditions"""
        query = f"SELECT COUNT(*) FROM {self._base_table}"

        if self._join_clauses:
            query += f" {' '.join(self._join_clauses)}"

        if self._where_conditions:
            query += f" WHERE {' AND '.join(self._where_conditions)}"

        return query, self._params.copy()

    def get_where_conditions(self) -> List[str]:
        """Get current WHERE conditions"""
        return self._where_conditions.copy()

    def get_params(self) -> List[Any]:
        """Get current parameters"""
        return self._params.copy()

    def reset(self) -> Self:
        """Reset the builder state to initial values"""
        self._select_fields = []
        self._where_conditions = []
        self._join_clauses = []
        self._order_by_clauses = []
        self._params = []
        self._offset_value = None
        self._limit_value = None
        return self

    def join(self, join_clause: str) -> Self:
        """Add JOIN clause to query"""
        if join_clause and join_clause.strip():
            self._join_clauses.append(join_clause)
        return self
