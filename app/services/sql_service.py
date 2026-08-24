#this service connects the ai,sql validator and database
#it controls the complete sql query flow

#import the function that generates sql from gemini
from app.ai.llm import generate_sql

#import our sql security validator
from app.sql_validator import validate_sql

#text() allows us to execute raw sql safely through sqlalchemy
from sqlalchemy import text

from app.sql_parser import get_columns,parse_sql

from app.ai.llm import generate_sql,generate_answer

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
    "customers": {
        "id",
        "name",
        "email",
        "city",
        "total_spent"
    }
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
def contains_unsupported_column(parsed_query)->bool:
    #get all columns used in the sql query
    columns=get_columns(parsed_query)

    #get allowed columns for the customers table
    allowed_columns=ALLOWED_COLUMNS['customers']

    #check every columns used in the query
    for column in columns:
        #ignore wildcard selections such as select *
        if column=="*":
            continue
        #reject columns that are not in our schema
        if column.lower() not in allowed_columns:
            return True
   
    return False

#process a user's natural language question
def process_question(question:str,
                     db,
                    conversation_context:str=""
                     )->dict:

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
    sql=generate_sql(question,
                     conversation_context
                     )

    #parse the generated sql
    is_parsed,parsed_query=parse_sql(sql)

    #stop if the generated sql has invalid syntax
    if not is_parsed:
        return{
            "success":False,
            "question":question,
            "sql":sql,
            "data":None,
            "message":f"invalid sql syntax:{parsed_query}"
        }

    #check if the generated sql is safe
    is_valid,message=validate_sql(sql)

    #stop the process if the sql is not safe
    if not is_valid:
        return{
            "success":False,
            "question":question,
            "sql":sql,
            "message":message
        }
    
    #check whether the generated sql uses unsupported columns
    if contains_unsupported_column(parsed_query):
        return{
                "success":False,
                "question":question,
                "sql":sql,
                "data":None,
                "message":"the query uses a column that is not avaliable"
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

        #generate a natural language answer from the database result
        answer=generate_answer(
            question=question,
            sql=sql,
            data=rows
        )

        #return the database result
        return{
        "success":True,
        "question":question,
        "sql":sql,
        "data":rows,
        "answer":answer,
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