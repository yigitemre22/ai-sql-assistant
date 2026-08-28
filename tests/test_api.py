#test fastapi api endpoints
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.main import app
from app.database.connection import get_app_db,get_db
from unittest.mock import patch
from types import SimpleNamespace

#create a test client for the fastapi application
client=TestClient(app)

#fake application database used for api error tests
class FakeAppDb:
    def __init__(self):
        #store a fake conversation id
        self.conversation_id=999
    def get(self,model,object_id):
        #return none to simulate a missing conversation
        return None
    def add(self,obj):
        #give new objects a fake id
        if hasattr(obj,"id"):
            obj.id=self.conversation_id
    def commit(self):
        #nothing to commit in the fake database
        pass
    def refresh(self,obj):
        #give the object a fake id after refresh
        obj.id=self.conversation_id
    def rollback(self):
        #nothing to roll back in the fake database
        pass

#fake database used to simulate database errors
class FakeDb:
    def execute(self,statement):
        #simulate a database failure
        raise SQLAlchemyError("test database error")
    def rollback(self):
        #nothing to roll back in the fake database
        pass
#test the api health endpoint
def test_root_endpoint():
    response=client.get("/")
    assert response.status_code==200
    assert response.json()['message']=="AI SQL Assistant api is running"

#test an invalid conversation id
def test_conversation_not_found():
    #override the application database dependency
    app.dependency_overrides[get_app_db]=(
        lambda:FakeAppDb()
    )
    response=client.post(
        "/ask",
        json={
            "question":"how man customers do we have?",
            "conversation_id":9999
        }
    )
    assert response.status_code==200

    data=response.json()

    assert data['success'] is False
    assert data['message'] =="conversation not found"

    #remove the dependency override
    app.dependency_overrides.clear()

#test database error handling
def test_query_database_error():
    #override the database dependency
    app.dependency_overrides[get_db]=(
        lambda:FakeDb()
        )
    response=client.post(
        "/query",
        json={
            "query":"select * from customers"
        }
    )
    assert response.status_code ==503

    data=response.json()

    assert data['detail']==(
        "database service is temporarily unavailable"
    )
    #remove the dependecny override
    app.dependency_overrides.clear()

#test sql validation failure
def test_query_validation_error():
    response=client.post(
        "/query",
        json={
            "query":"delete from customers"
        }
    )
    assert response.status_code==200

    data=response.json()

    assert data['success'] is False

#test an unexpected error in the /ask endpoint
def test_ask_unexpected_error():
    #override the application database dependency
    app.dependency_overrides[get_app_db]=(
        lambda:FakeAppDb()
    )

    #patch the question processor to simulate an unexpected error
    with patch(
        "app.api.routes.process_question",
        side_effect=Exception("test unexpected error")
    ):
        response=client.post(
            "/ask",
            json={
                "question":"how many customers do we have?"
            }
        )
    assert response.status_code==500

    data=response.json()

    assert data['detail']=="an unexpected error occured"

    #remove dependency overrides
    app.dependency_overrides.clear()

#test a database error in the /ask endpoint
def test_ask_database_error():
    #create a fake conversation object
    fake_conversation=type(
        "FakeConversation",
        (),
        {"id":1}
    )()

    #override the application database dependency
    app.dependency_overrides[get_app_db]=(
        lambda:FakeAppDb()
    )

    #override the sql database dependency
    app.dependency_overrides[get_db]=(
        lambda:FakeDb()
    )
    #mock conversation operations because this test
    #is only checking process_question error handling

    with patch(
        "app.api.routes.create_conversation",
        return_value=fake_conversation
        ),patch(
            "app.api.routes.get_conversation_messages",
            return_value=[]
        ),patch(
            "app.api.routes.add_message"
        ),patch(
            "app.api.routes.process_question",
            side_effect=SQLAlchemyError("test database error")
        ):
            response=client.post(
                "/ask",
                json={
                    "question":"how many customers do we have?"
                }
            )

    assert response.status_code==503

    data=response.json()

    assert data['detail']==(
        "database service is temporarily unavailable"
    )

    #remove dependency overrides
    app.dependency_overrides.clear()

#test the complete /ask flow
def test_ask_full_flow():
    #storage fake conversation data in memory
    messages=[]

    #fake conversation object 
    conversation=SimpleNamespace(
        id=100,
        title="integration test"
    )

    #fake application database
    class IntegrationAppDb:
        def get(self,model,object_id):
            #return the fake conversation for the requested id
            if object_id==100:
                return conversation
            return None
        def add(self,obj):
            #store the message object
            if hasattr(obj,"role"):
                messages.append(obj)
        def commit(self):
            pass
        def refresh(self,obj):
            pass
        def rollback(self):
            pass
        def query(self,model):
            #return a fake query object
            return self
        def filter(self,condition):
            return self
        def order_by(self,condition):
            return self
        def all(self):
            return messages

    #fake ai sql database
    class IntegrationDb:
        def rollback(self):
            pass
    fake_app_db=IntegrationAppDb()
    fake_db=IntegrationDb()

    #override fastapi dependencies
    app.dependency_overrides[get_app_db]=(
        lambda:fake_app_db
    )
    app.dependency_overrides[get_app_db]=(
        lambda:fake_app_db
    )
    #fake sql service result
    fake_result={
        "success":True,
        "question":"how many customers do we have?",
        "sql":"select count(*) from customer",
        "data":[
            {"count":5}
        ],
        "answer":"you have 5 customers",
        "message":"query executed successfully"
    }

    #mock the sql service
    with patch(
        "app.api.routes.process_question",
        return_value=fake_result
    ):
        response=client.post(
            "/ask",
            json={
                "question":"how many customers do we have?",
                "conversation_id":100
            }
        )

    assert response.status_code==200

    data=response.json()

    assert data["success"] is True
    assert data["conversation_id"]==100
    assert data['answer']=="you have 5 customers"

    #check that both user and assistant messages were stored
    assert len(messages)==2
    assert messages[0].role=="user"
    assert messages[1].role=="assistant"

    #remove dependency overrides
    app.dependency_overrides.clear()

#test that previous conversation messages are passed to the sql service
def test_ask_conversation_context():
    #fake conversation
    conversation=SimpleNamespace(
        id=200,
        title="context integration test"
    )
    #fake previous messages
    previous_messages=[
        SimpleNamespace(
            role="user",
            content="which customers live in Istanbul?"
        ),
        SimpleNamespace(
            role="assistant",
            content="Ali Yılmaz and Zeynep Çelik live in Istanbul."
        )
    ]
    #fake application database
    class ContextAppDb:
        def get(self,model,object_id):
            if object_id==200:
                return conversation
            return None
        def add(self,obj):
            pass
        def commit(self):
            pass
        def refresh(self,obj):
            pass
        def rollback(self):
            pass
        def query(self,model):
            return self
        def filter(self,condition):
            return self
        def order_by(self,condition):
            return self
        def all(self):
            return previous_messages

    #fake ai sql database
    class ContextDb:
        def rollback(self):
            pass

    fake_app_db=ContextAppDb()
    fake_db=ContextDb()

    #store the context passed to process_question
    captured_context={}

    #fake sql service result
    fake_result={
        "success":True,
        "question":"which one spent more?",
        "sql":"select name,total_spent from customers where city='Istanbul'  order by total_spent desc limit 1",
        "data":[
            {
                "name":"Ali Yılmaz",
                "total_spent":"12500.50"
            }
        ],
        "answer":"Ali Yılmaz spent the most in Istanbul.",
        "message":"query executed successfully"
    }

    #fake process_question function
    def fake_process_question(
            question,
            db,
            conversation_context
    ):
        captured_context['value']=conversation_context

        return fake_result

    #override database dependencies
    app.dependency_overrides[get_app_db]=(
        lambda:fake_app_db
    )
    app.dependency_overrides[get_db]=(
        lambda:fake_db
    )
    #mock the sql service
    with patch(
        "app.api.routes.process_question",
        side_effect=fake_process_question
    ):
        response=client.post(
            "/ask",
            json={
                "question":"which one spent more?",
                "conversation_id":200
            }
        )

        assert response.status_code==200

        data=response.json()

        assert data['success'] is True
        assert data['conversation_id']==200

        #verify that previous conversation was passed to the sql service 
        context=captured_context["value"]

        assert "user: which customers live in Istanbul?" in context
        assert(
            "assistant: Ali Yılmaz and Zeynep Çelik live in Istanbul." in context
        )

        #remove dependenct overrides
        app.dependency_overrides.clear()