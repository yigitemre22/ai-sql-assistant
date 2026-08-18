#this service connects the ai,sql validator and database
#it controls the complete sql query flow

#import the function that generates sql from gemini
from app.ai.llm import generate_sql

#import our sql security validator
from app.sql_validator import validate_sql

#text() allows us to execute raw sql safely through sqlalchemy
from sqlalchemy import text

import re

# Words that indicate a write or destructive operation
FORBIDDEN_INTENT_WORDS = [
    "delete",
    "remove",
    "update",
    "change",
    "modify",
    "insert",
    "create",
    "drop",
    "alter",
    "truncate",
]

# Tables that are available in our database
ALLOWED_TABLES = [
    "customers"
]

# Words that refer to unsupported tables
UNSUPPORTED_TABLE_WORDS = [
    "user",
    "users"
]

# Columns that are available in each allowed table
ALLOWED_COLUMNS = {
    "customers": [
        "id",
        "name",
        "email",
        "city",
        "total_spent"
    ]
}

#check whether the user's question asks for a forbidden operation
def contains_forbidden_intent(question:str)->bool:

    #convert the question to lowercase
    lower_question=question.lower()

    #check each forbidden operation
    for word in FORBIDDEN_INTENT_WORDS:
        #look for the word as a seperate word
        pattern=rf"\b{word}\b"

        if re.search(pattern,lower_question):
            return True

    return False

# Check whether the question asks for an unsupported table
def contains_unsupported_table(question: str) -> bool:

    # Convert the question to lowercase
    lower_question = question.lower()

    # Check each unsupported table word
    for word in UNSUPPORTED_TABLE_WORDS:

        # Look for the word as a separate word
        pattern = rf"\b{word}\b"

        if re.search(pattern, lower_question):
            return True

    return False

#check whether the generated sql uses unsupported columns
def contains_unsupported_column(sql:str)->bool:
    #convert sql to lowercase
    lower_sql=sql.lower()

    #get allowed columns for the customers table
    allowed_columns=ALLOWED_COLUMNS['customers']

    #find column names after common sql keyword
    column_patterns=[
        r"\bwhere\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        r"\band\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        r"\bor\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        r"\border\s+by\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        r"\bgroup\s+by\s+([a-zA-Z_][a-zA-Z0-9_]*)"
    ]
    #check each sql pattern
    for pattern in column_patterns:
        matches=re.findall(pattern,lower_sql)

        for column in matches:
            #ignore sql keywords
            if column in ["select","from","where","and","or"]:
                continue
            #reject unsupported columns
            if column not in allowed_columns:
                return True

    return False

#process a user's natural language question
def process_question(question:str,db)->dict:

    #check the user's intent before generating sql
    if contains_forbidden_intent(question):
        return{
        "success":False,
        "question":question,
        "sql":None,
        "data":None,
        "message":"only read-only select request are allowed"
    }

    #check whether the question asks for an unsupported table
    if contains_unsupported_table(question):
        return{
            "success":False,
            "question":question,
            "sql":None,
            "data":None,
            "message":"only read-only select request are allowed"
        }

  
    #generate a sql query using gemini
    sql=generate_sql(question)

    #check if the generated sql is safe
    is_valid,message=validate_sql(sql)

      #check whether the generated sql uses unsupported columns
    if contains_unsupported_column(sql):
        return{
                "success":False,
                "question":question,
                "sql":sql,
                "data":None,
                "message":"the query uses a column that is not avaliable"
            }
    

    #stop the process if the sql is not safe
    if not is_valid:
        return{
            "success":False,
            "question":question,
            "sql":sql,
            "message":message
        }

    try:
        #convert the sql string into a sqlalchemy text object
        statement=text(sql)

        #execute the validated select query
        result=db.execute(statement)

        #get column names from the query result
        columns=result.keys()

        #convert every row into a dictionary
        rows=[
            dict(zip(columns,row))
            for row in result.fetchall()
        ]

        #return the database result
        return{
        "success":True,
        "question":question,
        "sql":sql,
        "data":rows,
        "message":"query executed successfully"
        }

    except Exception as e:
        #return a readble error if database execution fails
        return{
            "success":False,
            "question":question,
            "sql":sql,
            "message":f"database error:{str(e)}"
        }