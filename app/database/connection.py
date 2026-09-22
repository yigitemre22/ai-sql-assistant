# Import SQLAlchemy tools for database connection
from sqlalchemy.orm import sessionmaker

#import centralized database engines
from app.database.engines import(
    readonly_engine,
    app_engine
) 

#keep the old engine name for existing application imports
engine=readonly_engine

# Create a session factory for database operations
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
)

#create a session factory for application data
#this connection is used for conversation history
AppSessionLocal=sessionmaker(
    bind=app_engine,
    autoflush=False,
)

#create a databese session for api request
def get_db():
    db=SessionLocal()

    try:
    #give the database session to the api
        yield db

    finally:
        #close the session after the request
        db.close()

#create a database session for application data
def get_app_db():
    db=AppSessionLocal()

    try:
        #give the application session to the api
        yield db
    finally:
        #close the application session after the request
        db.close()
    