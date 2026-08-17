from db.query_builder import SQLQueryBuilder


def build() -> SQLQueryBuilder:
    """
    Build a query builder over a known table

    Returns:
        Builder ready for a statement
    """
    return SQLQueryBuilder("accounts_users")


def test_a_count_query_binds_only_what_it_asks_for():
    """Dropping the ordering drops its parameters, so the driver gets a match"""
    builder = build()
    builder.select("id").where("email = %s", "user@example.com").order_by("rank(%s) DESC", "term")

    query, params = builder.build_count()

    assert query.count("%s") == len(params)
    assert params == ["user@example.com"]


def test_a_full_query_binds_conditions_before_ordering():
    """Parameters follow the order the placeholders appear in the statement"""
    builder = build()
    builder.select("id").where("email = %s", "user@example.com").order_by("rank(%s) DESC", "term")

    query, params = builder.build()

    assert query.index("WHERE") < query.index("ORDER BY")
    assert params == ["user@example.com", "term"]


def test_the_order_of_the_calls_does_not_change_the_bindings():
    """Adding the ordering first still binds the condition value to the condition"""
    builder = build()
    builder.select("id").order_by("rank(%s) DESC", "term").where("email = %s", "user@example.com")

    _, params = builder.build()

    assert params == ["user@example.com", "term"]


def test_a_reset_forgets_the_previous_table():
    """A reused builder cannot inherit a FROM its columns do not match"""
    builder = build()
    builder.from_table("accounts_users u").select("u.id").where("u.id = %s", 1)
    builder.build()

    builder.reset().select("id").where("id = %s", 1)
    query, _ = builder.build()

    assert "accounts_users u" not in query
    assert "FROM accounts_users" in query


def test_a_reset_forgets_the_previous_parameters():
    """Nothing from an earlier statement is bound into the next one"""
    builder = build()
    builder.select("id").where("email = %s", "first@example.com").order_by("id ASC")
    builder.build()

    builder.reset().select("id").where("email = %s", "second@example.com")
    _, params = builder.build()

    assert params == ["second@example.com"]
