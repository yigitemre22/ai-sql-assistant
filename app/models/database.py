#import sqlalchemy tools
from sqlalchemy import String,Numeric
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column

#base class for all database models

class Base(DeclarativeBase):
    pass

#customer table model

class Customer(Base):
    __tablename__="customers"

    #primary key

    id:Mapped[int]=mapped_column(
        primary_key=True
    )

    #customer name

    name:Mapped[str]=mapped_column(
        String(100),
        nullable=False
    )
    #customer mail
    
    email:Mapped[str | None]=mapped_column(
        String(150),
        nullable=True
    )

    #customer city

    city:Mapped[str | None]=mapped_column(
        String(100),
        nullable=True
    )

    #total aomunt spent by the customer

    total_spent:Mapped[float |None]=mapped_column(
        Numeric(10,2),
        nullable=True
    )