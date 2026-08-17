from typing import Self, Tuple, List, Any

from db.interfaces import SQLQueryBuilderInterface


class SQLQueryBuilder(SQLQueryBuilderInterface):
    """Builder for SQL queries with different parts"""

    def __init__(self, base_table: str):
        """Initialize with base table name"""
        self._base_table = base_table
        self._from_table = None
        self._select_fields = []
        self._join_clauses = []
        self._where_conditions = []
        self._order_by_clauses = []
        self._where_params = []
        self._order_by_params = []
        self._offset_value = None
        self._limit_value = None

    def select(self, *fields) -> Self:
        """Add fields to SELECT clause"""
        self._select_fields.extend(fields)
        return self

    def from_table(self, table_name: str) -> Self:
        """Set FROM table with optional alias"""
        self._from_table = table_name
        return self

    def where(self, condition: str, *params) -> Self:
        """
        Add condition to WHERE clause with params

        Args:
            condition: Condition text with placeholders
            params: Values the condition binds

        Returns:
            The builder, for chaining
        """
        if condition and condition.strip():
            self._where_conditions.append(condition)

        if params:
            self._where_params.extend(params)

        return self

    def order_by(self, clause: str, *params) -> Self:
        """
        Add clause to ORDER BY section with params

        Ordering parameters are kept apart from the conditions': they bind
        placeholders that appear later in the statement, and a count query drops
        the ordering entirely.

        Args:
            clause: Ordering expression with placeholders
            params: Values the expression binds

        Returns:
            The builder, for chaining
        """
        if clause and clause.strip():
            self._order_by_clauses.append(clause)

        if params:
            self._order_by_params.extend(params)

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
        table_name = self._from_table or self._base_table
        query = f"SELECT {', '.join(self._select_fields) or '*'} FROM {table_name}"

        if self._join_clauses:
            query += f" {' '.join(self._join_clauses)}"

        if self._where_conditions:
            query += f" WHERE {' AND '.join(self._where_conditions)}"

        if self._order_by_clauses:
            query += f" ORDER BY {', '.join(self._order_by_clauses)}"

        params = [*self._where_params, *self._order_by_params]

        if self._limit_value is not None:
            query += f" LIMIT %s"
            params.append(self._limit_value)

        if self._offset_value is not None:
            query += f" OFFSET %s"
            params.append(self._offset_value)

        return query, params

    def build_count(self) -> Tuple[str, List[Any]]:
        """
        Build COUNT query with the same conditions

        The ordering is dropped, and so are its parameters: keeping them would hand
        the driver more values than the statement has placeholders.

        Returns:
            Statement and the parameters its conditions bind
        """
        table_name = self._from_table or self._base_table
        query = f"SELECT COUNT(*) FROM {table_name}"

        if self._join_clauses:
            query += f" {' '.join(self._join_clauses)}"

        if self._where_conditions:
            query += f" WHERE {' AND '.join(self._where_conditions)}"

        return query, list(self._where_params)

    def get_where_conditions(self) -> List[str]:
        """Get current WHERE conditions"""
        return self._where_conditions.copy()

    def get_params(self) -> List[Any]:
        """Get the parameters the current conditions bind"""
        return list(self._where_params)

    def reset(self) -> Self:
        """
        Reset the builder state to initial values

        The table is reset too: a builder that keeps the previous FROM silently
        produces a statement whose columns reference an alias nothing defines.

        Returns:
            The builder, for chaining
        """
        self._select_fields = []
        self._where_conditions = []
        self._join_clauses = []
        self._order_by_clauses = []
        self._from_table = None
        self._where_params = []
        self._order_by_params = []
        self._offset_value = None
        self._limit_value = None
        return self

    def join(self, join_clause: str) -> Self:
        """Add JOIN clause to query"""
        if join_clause and join_clause.strip():
            self._join_clauses.append(join_clause)
        return self
