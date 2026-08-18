#import the sql validation function
from app.sql_validator import validate_sql

#test a valid select query
def test_valid_select():
    valid,message=validate_sql(
        "select * from customers"
    )

    assert valid is True

#test a forbidden drop command
def test_drop_command():
    valid,message=validate_sql(
        "drop table customers"
    )

    assert valid is False

#test a forbiddden delete command

def test_delete_command():
    valid,message=validate_sql(
        "delete from customer"
    )

    assert valid is False

# test an empty command
def test_empty_command():
    valid,message=validate_sql(
        ""
    )
    assert valid is False

#test an unkown table
def test_unkown_table():
    valid,message=validate_sql(
        "SELECT * FROM users"
    )
    assert valid is False

#test a valid row limit
def test_valid_limit():
    valid,message=validate_sql(
        "SELECT * FROM customers LIMIT 50"
    )
    assert valid is True

#test a row limit that is too high
def test_high_limit():
    valid,message=validate_sql(
        "SELECT * FROM customers LIMIT 500"
    )
    assert valid is False

#test a query that uses a forbidden table with join
def test_forbidden_join_table():
    valid,message=validate_sql(
        "SELECT * FROM customers JOIN users ON customers.id = users.customer_id"
    )
    assert valid is False

#test a join with an allowed table
def test_allowed_join_table():
    valid,message=validate_sql(
        "SELECT * FROM customers JOIN customers ON customers.id = customers.id"
    )
    assert valid is True

#test multiple sql statements
def test_multiple_statements():
    valid,messagae=validate_sql(
        "SELECT * FROM customers;DROP TABLE customers"
    )
    assert valid is False