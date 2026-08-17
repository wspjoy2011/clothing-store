import pytest

from apps.catalog.specifications.ordering import OrderingSpecification

PRICE = "COALESCE(i.sale_price, i.base_price)"


@pytest.mark.parametrize("ordering", ["---id", "--id", "----price", "-----year"])
def test_extra_leading_dashes_never_reach_the_sql(ordering):
    """Repeated dashes are not a direction: they would comment out the statement"""
    sql, _ = OrderingSpecification(ordering).to_sql()

    assert "--" not in sql
    assert sql == "ORDER BY id DESC"


@pytest.mark.parametrize("ordering", ["year; DROP TABLE catalog_products", "password", "1=1", "id)"])
def test_anything_off_the_allowlist_falls_back_to_the_default(ordering):
    """A field nobody allowed cannot influence the clause at all"""
    sql, params = OrderingSpecification(ordering).to_sql()

    assert sql == "ORDER BY id DESC"
    assert params == []


def test_the_requested_order_of_fields_is_kept():
    """Fields are applied in the order the client asked for"""
    sql, _ = OrderingSpecification("price,-year").to_sql()

    assert sql == f"ORDER BY {PRICE} ASC, year DESC, product_id ASC"


def test_a_descending_field_keeps_its_direction():
    """One leading minus means descending, and the direction survives the parse"""
    sql, _ = OrderingSpecification("-price").to_sql()

    assert sql == f"ORDER BY {PRICE} DESC, product_id ASC"


def test_the_tiebreaker_is_appended_for_stable_pagination():
    """Ordering that could tie gets product_id appended so pages do not repeat rows"""
    sql, _ = OrderingSpecification("year").to_sql()

    assert sql.endswith("product_id ASC")


def test_the_tiebreaker_is_not_duplicated():
    """Asking for the tiebreaker itself does not append it twice"""
    sql, _ = OrderingSpecification("-product_id").to_sql()

    assert sql == "ORDER BY product_id DESC"


def test_a_valid_field_is_kept_when_an_invalid_one_travels_with_it():
    """One bad field does not discard the whole request, only itself"""
    sql, _ = OrderingSpecification("price,evil").to_sql()

    assert sql == f"ORDER BY {PRICE} ASC, product_id ASC"
