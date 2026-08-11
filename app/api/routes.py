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
    db:Session=Depends(get_db)
):
    #get all customers from the database
    customers=db.query(Customer).all()

    return customers