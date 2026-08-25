#import fastapi tools , sqlalichemy session, database dependency, database model, api response scheme
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.database.connection import get_db,get_app_db
from app.models.database import Customer,Conversation
from app.models.schemas import *
from app.sql_validator import validate_sql
from app.services.sql_service import process_question
from app.services.conversation_service import(
    create_conversation,
    add_message,
    get_conversation_messages,
    build_conversation_context
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
    try:
        #start a query for all customer
        query=db.query(Customer)

        #filter customers by city if a city is provided

        if city:
            query=query.filter(Customer.city==city)

        #get the final results from the database

        customers=query.all()

        return customers
    
    except SQLAlchemyError:
        #roll back the failed transaction
        db.rollback()

        #return a safe error message to the client
        raise HTTPException(
            status_code=503,
            detail="database service is temporarily unavailable"
        )

#execute a validated sql quert

@router.post(
    "/query",
    response_model=QueryResponse
)
def execute_query(
    request:QueryRequest,
    db:Session=Depends(get_db)
):
    try:
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

    except SQLAlchemyError:
        #roll back the failed database transaction
        db.rollback()

        #do not expose internl database errors
        raise HTTPException(
            status_code=503,
            detail="database service is temporarily unavailable"
        )
    except Exception:
        #handle unexpected application errors
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="an unexpected error occurred"
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
    try:
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

        #get previous messages before adding the current question
        previous_messages=get_conversation_messages(
            app_db,
            conversation_id
        )

        #build context for gemini
        conversation_context=build_conversation_context(
            previous_messages
        )

        #process the question with gemini and the database
        result=process_question(
            request.question,
            db,
            conversation_context
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

        #save the user's message
        add_message(
            app_db,
            conversation_id,
            'user',
            request.question
        )

        #save the assistant's answer and query context
        assistant_memory=(
            f"Answer:{result['answer']}\n"
            f"SQL:{result['sql']}\n"
            f"Data:{result['data']}"
        )

        add_message(
            app_db,
            conversation_id,
            'assistant',
            assistant_memory
        )

        #return the result
        return QueryResponse(
            success=True,
            message=result['message'],
            data=result.get('data'),
            answer=result.get('answer'),
            conversation_id=conversation_id
        )

    except SQLAlchemyError:
        #roll back application database errors
        app_db.rollback()
        db.rollback()

        raise HTTPException(
            status_code=503,
            detail="database service is temporarily unavailable"
        )

    except Exception:
        #roll back any unexpected database state
        app_db.rollback()
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="an unexpected error occured"
        )