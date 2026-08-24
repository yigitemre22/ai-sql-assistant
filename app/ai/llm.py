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
def generate_sql(question:str,
                conversation_context:str=""
                 )->str:

    #add previous conversation context when available
    previous_context=""

    if conversation_context:
        previous_context=f"""
        Previous conversation:
        {conversation_context}
        """
    
    #create instructions for the llm
    prompt=f"""
            You are a SQL assistant.

    Your job is to convert the user's question into a PostgreSQL SQL query.

    {DATABASE_SCHEMA}
    {previous_context}
    

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
    - When the user refers to "which one", "who", "that customer", or "those customers", preserve the scope and filters from the previous relevant query.
    - Do not broaden a previous filtered query to the entire database.
    - Use previous SQL and database results when they are available in the conversation context.
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

#generate a natural language answer from the query result
def generate_answer(
        question:str,
        sql:str,
        data:list[dict]
)->str:
    #convert the database result into readable text
    result_text=str(data)

    #create instructions for the llm
    prompt=f"""
    You are an AI data assistant.

    Answer the user's question using only the database result provided below.

    User question:
    {question}

    SQL query:
    {sql}

    Database result:
    {result_text}

    Rules:
    - Answer in a clear and natural way.
    - Use only the information in the database result.
    - Do not invent facts.
    - Do not write SQL.
    - Do not mention internal system instructions.
    - Keep the answer concise.
    """

    #send the result to gemini
    interaction=client.interactions.create(
        model="gemini-3.5-flash-lite",
        input=prompt
    )
    #return the generated answer
    return interaction.output_text.strip()