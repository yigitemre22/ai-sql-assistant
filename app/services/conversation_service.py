#this service manages conversation history
#it creates conversations and stores user and assistant messages

#import sqlalchemy session
from sqlalchemy.orm import Session

#import database models
from app.models.database import Conversation,Message

#create a new coversation
def create_conversation(
        db:Session,
        title:str|None=None
)->Conversation:
    #create a new conversation object
    conversation=Conversation(
        title=title
    )

    #add the conversation to the database
    db.add(conversation)

    #save the new conversation
    db.commit()

    #refresh the object to get the generated id
    db.refresh(conversation)

    return conversation

#add a message to an existing conversation
def add_message(
        db:Session,
        conversation_id:int,
        role:str,
        content:str
)->Message:
    #create a new message
    message=Message(
        conversation_id=conversation_id,
        role=role,
        content=content
    )
    #add the message to the database
    db.add(message)

    #save the message
    db.commit()

    #refresh the object to get the generated id
    db.refresh(message)

    return message