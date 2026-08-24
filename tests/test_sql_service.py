#test the security functions of the sql service
from app.services.sql_service import(
    contains_forbidden_intent,
    contains_unsupported_table,
    contains_unsupported_column
)
#import sql parser
from app.sql_parser import parse_sql

#import conversation model and context builder
from app.models.database import Message
from app.services.conversation_service import build_conversation_context

#test forbidden operations
def test_delete_intent():
    assert contains_forbidden_intent(
        "delete all customers"
    ) is True

def test_update_intent():
    assert contains_forbidden_intent(
        "update customers all"
    ) is True

#test supported request
def test_safe_question():
    assert contains_forbidden_intent(
        "how many customers do we have?"
    ) is False

#test unsupported tables
def test_unsupported_users_table():
    assert contains_unsupported_table(
        "show me users"
    ) is True

def test_supported_customers_table():
    assert contains_unsupported_table(
        "show me customers"
    ) is False

#test a valid database column

def test_valid_column():
    is_valid,parsed_query=parse_sql("SELECT name FROM customers")
    assert is_valid is True
    assert contains_unsupported_column(parsed_query) is False

#test an invalid database column
def test_unsupported_column():
    is_valid,parsed_query=parse_sql(
        "SELECT salary FROM customers"
    )
    assert is_valid is True
    assert contains_unsupported_column(parsed_query) is True
#test a valid where column
def test_valid_where_column():
    is_valid,parsed_query=parse_sql(
        "SELECT * FROM customers WHERE total_spent>5000"
    )
    assert is_valid is True
    assert contains_unsupported_column(parsed_query) is False

#test an invalid where column
def test_unsupported_where_column():
    is_valid,parsed_query=parse_sql(
        "SELECT * FROM customers WHERE salary >5000"
    )
    assert is_valid is True
    assert contains_unsupported_column(parsed_query) is True

#test building conversation context
def test_conversation_context():
    messages=[
        Message(
            role="user",
            content="which customers live in Istanbul?"
        ),
        Message(
            role="assistant",
            content="the customers who live in Istanbul are Ali Yılmaz and Zeynep Çelik."
        ),
        Message(
            role="user",
            content="which one spent more?"
        )
    ]

    context=build_conversation_context(messages)

    assert "user: which customers live in Istanbul?" in context
    assert "assistant: the customers who live in Istanbul are Ali Yılmaz and Zeynep Çelik." in context
    assert "user: which one spent more?" in context

#test conversation message order
def test_conversation_context_order():
    messages=[
        Message(
            role="user",
            content="first question"
        ),
        Message(
            role="assistant",
            content="first answer"
        ),
        Message(
            role="user",
            content="second question"
        )
    ]
    context=build_conversation_context(messages)

    first_position=context.index("first question")
    answer_position=context.index("first answer")
    second_position=context.index("second question")

    assert first_position<answer_position
    assert answer_position<second_position