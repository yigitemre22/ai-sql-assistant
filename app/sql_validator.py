#reguler expressions help us chech sql queries
import re

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

    #convert the query to uppercase for easier checking
    upper_query=query.upper()

    #check for forbidden sql commands
    for command in FORBIDDEN_COMMANDS:

        #look for the command as a seperate sql work
        pattern=  rf"\b{command}\b"

        if re.search(pattern,upper_query):
            return False, f"sql command '{command}' is not allowed"

    #only allow select queries fow now
    if not upper_query.startswith("SELECT"):
        return False,"only select queries are allowed"

    #check if the query uses an allowed table
    allowed_table_found=False

    for table in ALLOWED_TABLES:
        #convert the table name to uppercase for comparison
        table_pattern=rf"\bFROM\s+{table.upper()}\b"

        if re.search(table_pattern,upper_query):
            allowed_table_found=True
            break

    #reject the query if no allowed table was found
    if not allowed_table_found:
        return False,"the query uses a table that is not allowed"

    #find tables used in join statements
    join_tables=re.findall(
        r"\bJOIN\s+([A-Z_][A-Z0-9_]*)\b",
        upper_query
    )

    #check every join table
    for table in join_tables:
        #check if the join table is allowed
        if table not in [item.upper() for item in ALLOWED_TABLES]:
            return False,f"the join table'{table} is not allowed"

    #check if the query already contains a limit clause
    limit_match=re.search(r"\bLIMIT\s+(\d+)",upper_query)

    if limit_match:
        requested_limit=int(limit_match.group(1))
        #prevent queries from requesting too many rows
        if requested_limit>MAX_ROWS:
            return False,f"maximum row limit is {MAX_ROWS}"

    #query passed all basic checks
    return True,"sql query is valid"

        