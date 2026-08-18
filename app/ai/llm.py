#google genai provides the gemini api client
from google import genai

#import out application settings
from app.config import settings

#import our database schema
from app.ai.schema import DATABASE_SCHEMA

#create the gemini client
client=genai.Client(
    api_key=settings.GEMINI_API_KEY
)


#generate sql from a natural language question
def generate_sql(question:str)->str:
    #create instructions for the llm
    prompt=f"""
            You are a SQL assistant.

    Your job is to convert the user's question into a PostgreSQL SQL query.

    {DATABASE_SCHEMA}

    Rules:
    - Generate SELECT queries only.
    - Use only the tables and columns provided above.
    - Never generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE or other write operations.
    - Generate only one SQL statement.
    - Do not use tables that are not listed in the schema.
    - Return only the SQL query.
    - Do not use markdown code blocks.
    - Do not add explanations.
    - If the user asks for a table that does not exist in the schema, do not guess another table.
    - If the requested table does not exist, return exactly: INVALID_REQUEST
    - If the question cannot be answered using the provided schema, return exactly: INVALID_REQUEST

    User question:
    {question}
    """
    #send the promt to gemini
    interaction=client.interactions.create(
        model="gemini-3.5-flash-lite",
        input=prompt
    )

    #return the generated sql
    return interaction.output_text.strip()

#send a question to gemini
def ask_llm(question:str)->str:
    #send the user's question to the gemini model
    response=client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=question
    )
    #return the generated text
    return response.text