import pytest

from apps.catalog.specifications.ordering import OrderingSpecification

PRICE = "COALESCE(i.sale_price, i.base_price)"
PRODUCT_ID = "p.product_id"
YEAR = "p.year"


@pytest.mark.parametrize("ordering", ["---id", "--id", "----price", "-----year"])
def test_extra_leading_dashes_never_reach_the_sql(ordering):
    """Repeated dashes are not a direction: they would comment out the statement"""
    expressions = OrderingSpecification(ordering).to_order_by()

    assert not any("--" in expression for expression in expressions)
    assert expressions == [f"{PRODUCT_ID} DESC"]


@pytest.mark.parametrize("ordering", ["year; DROP TABLE catalog_products", "password", "1=1", "id)"])
def test_anything_off_the_allowlist_falls_back_to_the_default(ordering):
    """A field nobody allowed cannot influence the clause at all"""
    expressions = OrderingSpecification(ordering).to_order_by()

    assert expressions == [f"{PRODUCT_ID} DESC"]


def test_the_requested_order_of_fields_is_kept():
    """Fields are applied in the order the client asked for"""
    expressions = OrderingSpecification("price,-year").to_order_by()

    assert expressions == [f"{PRICE} ASC", f"{YEAR} DESC", f"{PRODUCT_ID} ASC"]


def test_a_descending_field_keeps_its_direction():
    """One leading minus means descending, and the direction survives the parse"""
    expressions = OrderingSpecification("-price").to_order_by()

    assert expressions == [f"{PRICE} DESC", f"{PRODUCT_ID} ASC"]


def test_the_tiebreaker_is_appended_for_stable_pagination():
    """Ordering that could tie gets product_id appended so pages do not repeat rows"""
    expressions = OrderingSpecification("year").to_order_by()

    assert expressions[-1] == f"{PRODUCT_ID} ASC"


def test_the_tiebreaker_is_not_duplicated():
    """Asking for the tiebreaker itself does not append it twice"""
    expressions = OrderingSpecification("-product_id").to_order_by()

    assert expressions == [f"{PRODUCT_ID} DESC"]


def test_a_valid_field_is_kept_when_an_invalid_one_travels_with_it():
    """One bad field does not discard the whole request, only itself"""
    expressions = OrderingSpecification("price,evil").to_order_by()

    assert expressions == [f"{PRICE} ASC", f"{PRODUCT_ID} ASC"]
