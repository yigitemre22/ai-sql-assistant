#import fastapi tools , sqlalichemy session, database dependency, database model, api response scheme
from fastapi import APIRouter,Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.database import Customer
from app.models.schemas import *
from app.sql_validator import validate_sql

#create an api router

router=APIRouter()


#get all customers

@router.get(
    "/customers",
    response_model=list[CustomerResponse]
)

def get_customers(
    city:str | None=None,
    db:Session=Depends(get_db)
):
    #start a query for all customer
    query=db.query(Customer)

    #filter customers by city if a city is provided

    if city:
        query=query.filter(Customer.city==city)

    #get the final results from the database

    customers=query.all()
    
    return customers

#execute a validated sql quert

@router.post(
    "/query",
    response_model=QueryResponse
)
def execute_query(
    request:QueryRequest,
    db:Session=Depends(get_db)
):
    #validate the sql query before executing it
    is_valid,message=validate_sql(request.query)

    #stop the request if the query is not safe
    if not is_valid:
        return QueryResponse(
            success=False,
            message=message,
            data=None
        )

    #execute the validated sql query
    result=db.execute(text(request.query))

    #get column names from the result
    columns=result.keys()

    #convert database rows into dictionaries
    data=[
        dict(zip(columns,row))
        for row in result.fetchall()
    ]

    #return the query results
    return QueryResponse(
        success=True,
        message="Query executed successfully",
        data=data
    )