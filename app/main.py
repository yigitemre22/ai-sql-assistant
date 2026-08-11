from fastapi import FastAPI
from app.api.routes import router

#create the fastapi application

app=FastAPI(
    title="AI SQL Assistant",
    version="0.1.0"
)

# add api routes to the applicaton

app.include_router(router)

#simple api health check

@app.get("/")

def root():
    return{
        "message":"AI SQL Assistant api is running"
    }