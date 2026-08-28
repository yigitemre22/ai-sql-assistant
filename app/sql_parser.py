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

#get all functions used in sql query
def get_functions(query):
    #find all sql function expressions
    functions=query.find_all(exp.Func)

    #return function names as as list
    return [
        function.sql_name().lower()
        for function in functions
    ]

#get all columns names used in a aql query
def get_columns(query):
    #find all column expressions in the sql structure
    columns=query.find_all(exp.Column)

    #return column names as a list
    return [column.name for column in columns]
    
#check how many sql statements exit in a query
def get_statement_count(query:str):
    #parse all sql statements in the query
    statements=sqlglot.parse(query)

    #return the number of statements
    return len(statements)