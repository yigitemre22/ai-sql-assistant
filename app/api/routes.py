#import fastapi tools , sqlalichemy session, database dependency, database model, api response scheme
from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.database import Customer
from app.models.schemas import CustomerResponse


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