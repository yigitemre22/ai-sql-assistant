#reguler expressions help us chech sql queries
import re

#import sql parser functions
from app.sql_parser import parse_sql,get_tables,get_statement_count

#sql commands that our application does not allow
FORBIDDEN_COMMANDS=[
    "DROP",
    "DELETE",
    "UPDATE",
    "INSERT",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "GRANT",
    "REVOKE"
]

#tables that the ai is allowed to query
ALLOWED_TABLES=["customers"]

#maximum number of rows that a query can return
MAX_ROWS=100

#check if a sql query is safe to exccute
def validate_sql(query:str)->tuple[bool,str]:
    #remove extra spaces from the query
    query=query.strip()

    #check if the query is empty
    if not query:
        return False,"Sql query can not be empty"

    #parse the sql query before checking security rules
    is_valid_sql,parsed_query=parse_sql(query)

    #reject the query if the sql syntax is invalid
    if not is_valid_sql:
        return False,f"invalid sql syntax{parsed_query}"

    #convert the query to uppercase for easier checking
    upper_query=query.upper()

    #check if the query contains multiple sql statements
    statement_count=get_statement_count(query)

    if statement_count!=1:
        return False,"only one sql statement is allowed"

    #check for forbidden sql commands
    for command in FORBIDDEN_COMMANDS:

        #look for the command as a seperate sql work
        pattern=  rf"\b{command}\b"

        if re.search(pattern,upper_query):
            return False, f"sql command '{command}' is not allowed"

    #only allow select queries fow now
    if not upper_query.startswith("SELECT"):
        return False,"only select queries are allowed"

    #get all tables used in the sql query
    tables=get_tables(parsed_query)

    #convert allowed table names to lowercase
    allowed_tables=[
        table.lower()
        for table in ALLOWED_TABLES
    ]

    #check every table used in the query
    for table in tables:
        #reject the query if the table is not allowed
        if table.lower() not in allowed_tables:
            return False,f"the table'{table} is not allowed"

    #check if the query already contains a limit clause
    limit_match=re.search(r"\bLIMIT\s+(\d+)",upper_query)

    if limit_match:
        requested_limit=int(limit_match.group(1))
        #prevent queries from requesting too many rows
        if requested_limit>MAX_ROWS:
            return False,f"maximum row limit is {MAX_ROWS}"

    #query passed all basic checks
    return True,"sql query is valid"

        