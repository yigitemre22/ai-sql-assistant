#import pytest for parametrized tests
import pytest
#import the sql validation function
from app.sql_validator import validate_sql

#load sql queries from a text file
def load_queries(filename:str)->list[str]:
    #open the file using utf-8 encoding
    with open(filename,"r",encoding="utf-8") as file:
        #read non-empty lines
        return[
            line.strip()
            for line in file
            if line.strip()
        ]

ALLOWED_QUERIES=load_queries(
    "tests/security/allowed_queries.txt"
)

MALICIOUS_QUERIES=load_queries(
    "tests/security/malicious_queries.txt"
)

#test all allowed queries
@pytest.mark.parametrize(
    "query",ALLOWED_QUERIES
)
def test_allowed_queries(query):
    valid,message=validate_sql(query)
    assert valid is True,message

@pytest.mark.parametrize(
    "query",MALICIOUS_QUERIES
)
#test all malicious queries
def test_malicious_queries(query):
    valid,message=validate_sql(query)

    assert valid is False,(
        f"Security test failed"
        f"The query was accepted:{query}"
    )

#test an empty query
def test_empty_query():
    valid,message=validate_sql("")
    assert valid is False
#test an unknown table
def test_unknown_table():
    valid,message=validate_sql(
        "select * from users"
    )
    assert valid is False