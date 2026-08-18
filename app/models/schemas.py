#import basemodel from pydantic
from pydantic import BaseModel

# this schema represents a customer returned by the api

class CustomerResponse(BaseModel):
    id:int
    name:str
    email:str | None=None
    city:str | None =None
    total_spent: float | None=None

    #allow pydantic to read data from sqlalchemy objects

    model_config={
        "from_attributes":True
    }

#schema for incoming sql request

class QueryRequest(BaseModel):
    #sql aurey sent by the user
    query:str

#schema for sql query responses
class QueryResponse(BaseModel):
    #indicates whether the query was successful
    success:bool

    #result message
    message:str

    #query results
    data:list[dict] | None=None

#schema for natural language questions
class AskRequest(BaseModel):
    #question sent by the user
    question:str