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

    #query passed all basic checks

    return True,"sql query is valid"

        