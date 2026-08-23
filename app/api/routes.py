#import fastapi tools , sqlalichemy session, database dependency, database model, api response scheme
from fastapi import APIRouter,Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database.connection import get_db,get_app_db
from app.models.database import Customer,Conversation
from app.models.schemas import *
from app.sql_validator import validate_sql
from app.services.sql_service import process_question
from app.services.conversation_service import(
    create_conversation,
    add_message
)

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

#generate and execute sql from a natural language questions
@router.post(
    "/ask",
    response_model=QueryResponse
)
def ask_question(
    request:AskRequest,
    db:Session=Depends(get_db),
    app_db:Session=Depends(get_app_db)
):
    #create a new conversation if no valid id is provided
    if request.conversation_id is None or request.conversation_id<=0:
        conversation=create_conversation(
            app_db,
            title=request.question[:50]
        )
        conversation_id=conversation.id

    else:
        #check whether the conversation exist
        conversation=app_db.get(
            Conversation,
            request.conversation_id
        )
        #return an error if the conversation does no exist
        if conversation is None:
            return QueryResponse(
                success=False,
                message="conversation not found",
                data=None,
                answer=None,
                conversation_id=None
            )
        
        conversation_id=request.conversation_id

    #save the user's message
    add_message(
        app_db,
        conversation_id,
        'user',
        request.question
    )

    #process the question with gemini and the database
    result=process_question(
        request.question,
        db
    )
    #stop if the request failed
    if not result['success']:
        return QueryResponse(
            success=False,
            message=result['message'],
            data=result.get('data'),
            answer=result.get('answer'),
            conversation_id=conversation_id
        )

    #save the assistant's answer
    add_message(
        app_db,
        conversation_id,
        'assistant',
        result['answer']
    )

    #return the result
    return QueryResponse(
        success=True,
        message=result['message'],
        data=result.get('data'),
        answer=result.get('answer'),
        conversation_id=conversation_id
    )
