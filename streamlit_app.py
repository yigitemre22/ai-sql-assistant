import requests
import streamlit as st

#fastapi backend url

API_URL="http://127.0.0.1:8000/ask"

#configure the streamlit page

st.set_page_config(
    page_title="AI SQL ASSISTANT",
    page_icon="🤖",
    layout="centered"
)

# Page title
st.title("🤖 AI SQL Assistant")

st.write(
    "Ask questions about your PostgreSQL database using natural language."
)

#store conversation id in the streamlit session
if "conversation_id" not in st.session_state:
    st.session_state["conversation_id"]=None

#store messages show in the ui
if "messages" not in st.session_state:
    st.session_state['messages']=[]

#display previous messages
for message in st.session_state['messages']:
    with st.chat_message(message['role']):
        st.write(message['content'])


#chat input
question=st.chat_input(
    "ask a question about your databse"
)

#handle a new question
if question:
    #display the user message
    st.session_state['messages'].append(
        {
            "role":"user",
            "content":question
        }
    )

    with st.chat_message("user"):
        st.write(question)

    #prepare the api reques
    payload={
        "question":question,
        "conversation_id":st.session_state['conversation_id']
    }

    try:
        #send the question to fastapi
        response=requests.post(
            API_URL,
            json=payload,
            timeout=60
        )

        #raise an exception for http errors
        response.raise_for_status()

        #convert api response to json

        data=response.json()

        #save the conversation_id
        st.session_state['conversation_id']=(
            data.get("conversation_id")
        )

        #get ai answer
        if data.get("success"):
            answer=data.get(
                "answer",
                "no answer returned"
            )
        else:
            answer=data.get(
                "message",
                "the request failed"
            )

    except requests.RequestException as error:
        answer=(
            "the backend could not be reached"
            f"Error:{error}"
        )

    #display the assistant response
    st.session_state['messages'].append(
        {
            "role":"assistant",
            "content":answer
        }
    )
    with st.chat_message("assistant"):
        st.write(answer)