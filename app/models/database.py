#import sqlalchemy tools
from sqlalchemy import (
    String,
    Numeric,
    ForeignKey,
    DateTime,
    Integer
    )

from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship
    )

from decimal import Decimal

#import datetime tools
from datetime import datetime,UTC

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

    #city id
    city_id:Mapped[int|None]=mapped_column(
        ForeignKey("cities.id"),
        nullable=True
    )

    #city relationship
    city_relation:Mapped["City"]=relationship(
        "City",
        back_populates="customers"
    )

    #orders
    orders:Mapped[list["Order"]]=relationship(
        "Order",
        back_populates="customer"
    )

    #total aomunt spent by the customer

    total_spent:Mapped[Decimal |None]=mapped_column(
        Numeric(12,2),
        nullable=True
    )

#city table model
class City(Base):
    __tablename__="cities"


    id:Mapped[int]=mapped_column(
        primary_key=True
    )

    name:Mapped[str]=mapped_column(
        String(100),
        nullable=False,
        unique=True
    )

    country:Mapped[str]=mapped_column(
        String(100),
        nullable=False,
        default="Türkiye"
    )

    customers:Mapped[list["Customer"]]=relationship(
        "Customer",
        back_populates="city_relation"
    )

#product table model
class Product(Base):
    __tablename__="products"

    id:Mapped[int]=mapped_column(
        primary_key=True
    )

    name:Mapped[str]=mapped_column(
        String(100),
        nullable=False
    )
    category:Mapped[str]=mapped_column(
        String(100),
        nullable=False
        )
    price:Mapped[Decimal]=mapped_column(
        Numeric(12,2),
        nullable=False
    )
    order_items:Mapped[list["OrderItem"]]=relationship(
        "OrderItem",
        back_populates="product"
    )

#order table model
class Order(Base):
    __tablename__="orders"

    id:Mapped[int]=mapped_column(
        primary_key=True
    )
    customer_id:Mapped[int]=mapped_column(
        ForeignKey("customers.id"),
        nullable=False
    )
    order_date:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    status:Mapped[str]=mapped_column(
        String(30),
        nullable=False
    )
    customer:Mapped["Customer"]=relationship(
        "Customer",
        back_populates="orders"
    )
    order_items:Mapped[list["OrderItem"]]=relationship(
        "OrderItem",
        back_populates="order"
    )

#orderitem table model
class OrderItem(Base):
    __tablename__="order_items"

    id:Mapped[int]=mapped_column(
        primary_key=True
    )
    order_id:Mapped[int]=mapped_column(
        ForeignKey("orders.id"),
        nullable=False
    )
    product_id:Mapped[int]=mapped_column(
        ForeignKey("products.id"),
        nullable=False
    )
    quantity:Mapped[int]=mapped_column(
        nullable=False
    )
    unit_price:Mapped[float]=mapped_column(
        Numeric(12,2),
        nullable=False
    )
    order:Mapped["Order"]=relationship(
        "Order",
        back_populates="order_items"
    )
    product:Mapped["Product"]=relationship(
        "Product",
        back_populates="order_items"
    )
#conversation table model
class Conversation(Base):
    __tablename__="conversations"

    #primary key
    id:Mapped[int]=mapped_column(
        primary_key=True
    )

    #conversation title
    title:Mapped[str|None]=mapped_column(
        String(200),
        nullable=True
    )
    #conversation creation time
    created_at:Mapped[datetime]=mapped_column(
        DateTime,
        default=lambda:datetime.now(UTC)
    )
    #messages that belong to this conversation
    messages:Mapped[list['Message']]=relationship(
        back_populates="conversation",
        cascade="all, delete-orphan"
    )

#message table model
class Message(Base):
    __tablename__="messages"

    #primary key
    id:Mapped[int]=mapped_column(
        primary_key=True
    )

    #id of the related conversation
    conversation_id:Mapped[int]=mapped_column(
        ForeignKey("conversations.id"),
        nullable=False
    )
    #message role:user or assistant
    role:Mapped[str]=mapped_column(
        String(20),
        nullable=False
    )
    #message content
    content:Mapped[str]=mapped_column(
        String,
        nullable=False
    )
    #message creation time
    created_at:Mapped[datetime]=mapped_column(
        DateTime,
        default=lambda:datetime.now(UTC)
    )
    #related conversation
    conversation:Mapped["Conversation"]=relationship(
        back_populates="messages"
    )