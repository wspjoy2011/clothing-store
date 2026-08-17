from dataclasses import dataclass, field
from typing import Any, List

PRODUCT_ALIAS = "p"
INVENTORY_ALIAS = "i"
EFFECTIVE_PRICE = f"COALESCE({INVENTORY_ALIAS}.sale_price, {INVENTORY_ALIAS}.base_price)"


@dataclass(frozen=True)
class SqlClause:
    """Conditions a specification contributes, with the values they bind

    A specification returns predicates and parameters, never SQL keywords: the
    repository owns the shape of the statement. Fragments carrying their own WHERE
    and ORDER BY have to be taken apart again by whoever assembles them, and that
    string surgery is where wrong queries come from.
    """

    conditions: List[str] = field(default_factory=list)
    params: List[Any] = field(default_factory=list)
    joins: List[str] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        """Report whether the clause contributes nothing"""
        return not self.conditions and not self.joins

    def merge(self, other: "SqlClause") -> "SqlClause":
        """
        Combine two clauses, keeping the order of conditions and parameters aligned

        Args:
            other: Clause applied after this one

        Returns:
            Clause carrying both sets of joins, conditions and parameters
        """
        return SqlClause(
            conditions=[*self.conditions, *other.conditions],
            params=[*self.params, *other.params],
            joins=[*self.joins, *other.joins]
        )
