#import sqlalchemy tools
from sqlalchemy import String,Numeric,ForeignKey,DateTime
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column,relationship

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

    #total aomunt spent by the customer

    total_spent:Mapped[float |None]=mapped_column(
        Numeric(10,2),
        nullable=True
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