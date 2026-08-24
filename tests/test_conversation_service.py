#test the conversation service

#import sqlalchemy tools for the temporary test database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#import the appliaction database models
from app.models.database import Base

#import conversation service functions
from app.services.conversation_service import(
    create_conversation,
    add_message,
    get_conversation_messages,
    build_conversation_context
)

#create a temporary sqlite database for test
engine=create_engine(
    "sqlite:///:memory:",
    echo=False
)

#create a session factory for the test database
TestingSessionLocal=sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

#create all database tables before tests
Base.metadata.create_all(bind=engine)

#test conversation creation
def test_create_conversation():
    db=TestingSessionLocal()

    conversation=create_conversation(
        db,
        title="test conversation"
    )

    assert conversation.id is not None
    assert conversation.title =="test conversation"

    db.close()

#test adding a message
def test_add_message():
    db=TestingSessionLocal()

    conversation=create_conversation(
        db,
        title="message test"
    )

    message=add_message(
        db,conversation.id,
        "user",
        "how many customers do we have?"
    )

    assert message.id is not None
    assert message.conversation_id == conversation.id
    assert message.role == "user"
    assert message.content == "how many customers do we have?"

    db.close()


#test retrieving conversation messages
def test_get_conversation_messages():
    db=TestingSessionLocal()

    conversation=create_conversation(
        db,
        title="history test"
    )

    add_message(
        db,
        conversation.id,
        "user",
        "first question"
    )

    add_message(
        db,
        conversation.id,
        "assistant",
        "first answer"
    )

    messages=get_conversation_messages(
        db,
        conversation.id
    )

    assert len(messages)==2
    assert messages[0].role=="user"
    assert messages[0].content=="first question"
    assert messages[1].role =="assistant"
    assert messages[1].content =="first answer"

    db.close()

#test building conversation context
def test_build_conversation_context_from_database():
    db=TestingSessionLocal()

    conversation=create_conversation(
        db,
        title="context test"
    )

    add_message(
        db,
        conversation.id,
        "user",
        "which customers live in Istanbul?"
    )
    add_message(
        db,
        conversation.id,
        "assistant",
        "Ali Yılmaz and Zeynep Çelik live in Istanbul."
    )
    messages=get_conversation_messages(
        db,
        conversation.id
    )

    context=build_conversation_context(messages)

    assert "user: which customers live in Istanbul?"in context
    assert "assistant: Ali Yılmaz and Zeynep Çelik live in Istanbul" in context

    db.close()
