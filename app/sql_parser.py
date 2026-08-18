#sqlglot helps us understand the structure of sql queries
import sqlglot

#import the sql select expression type
from sqlglot import exp

#parse a sql query and return its structure
def parse_sql(query:str):
    #try to parse the sql query
    try:
        parsed_query=sqlglot.parse_one(query)

        return True,parsed_query

    #return an error if the sql syntax is invalid
    except sqlglot.errors.ParseError as error:
        return False,str(error)

#get all table names used in a sql query
def get_tables(query):
    #finf all table expressions
    tables=query.find_all(exp.Table)

    #return table names as a list
    return [table.name for table in tables]

#check how many sql statements exit in a query
def get_statement_count(query:str):
    #parse all sql statements in the query
    statements=sqlglot.parse(query)

    #return the number of statements
    return len(statements)