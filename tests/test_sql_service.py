#test the security functions of the sql service
from app.services.sql_service import(
    contains_forbidden_intent,
    contains_unsupported_table,
    contains_unsupported_column
)
from app.sql_parser import parse_sql
#test forbidden operations

def test_delete_intent():
    assert contains_forbidden_intent(
        "delete all customers"
    ) is True

def test_update_intent():
    assert contains_forbidden_intent(
        "update customers all"
    ) is True

#test supported request
def test_safe_question():
    assert contains_forbidden_intent(
        "how many customers do we have?"
    ) is False

#test unsupported tables
def test_unsupported_users_table():
    assert contains_unsupported_table(
        "show me users"
    ) is True

def test_supported_customers_table():
    assert contains_unsupported_table(
        "show me customers"
    ) is False

#test a valid database column

def test_valid_column():
    is_valid,parsed_query=parse_sql("SELECT name FROM customers")
    assert is_valid is True
    assert contains_unsupported_column(parsed_query) is False

#test an invalid database column
def test_unsupported_column():
    is_valid,parsed_query=parse_sql(
        "SELECT salary FROM customers"
    )
    assert is_valid is True
    assert contains_unsupported_column(parsed_query) is True
#test a valid where column
def test_valid_where_column():
    is_valid,parsed_query=parse_sql(
        "SELECT * FROM customers WHERE total_spent>5000"
    )
    assert is_valid is True
    assert contains_unsupported_column(parsed_query) is False

#test an invalid where column
def test_unsupported_where_column():
    is_valid,parsed_query=parse_sql(
        "SELECT * FROM customers WHERE salary >5000"
    )
    assert is_valid is True
    assert contains_unsupported_column(parsed_query) is True