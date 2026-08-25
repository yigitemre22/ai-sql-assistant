#test fastapi api endpoints
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.main import app
from app.database.connection import get_app_db,get_db

#create a test client for the fastapi application
client=TestClient(app)

#fake application database used for api error tests
class FakeAppDb:
    def get(self,model,object_id):
        #return none to simulate a missing conversation
        return None
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