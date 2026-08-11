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