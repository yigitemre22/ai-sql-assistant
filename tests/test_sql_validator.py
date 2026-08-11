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