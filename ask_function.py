import os
from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END

load_dotenv()

# ==========================================
# ask Tazuna
# ==========================================

class State(TypedDict):
    question: str
    answer: str

llm = ChatOllama(model=os.getenv('MODEL'))

prompt = ChatPromptTemplate.from_template(
    '''
        Your name is Tazuna Hayakawa.

        As secretary to the director of Tracen Academy, Tazuna aims to be a pillar of support not only for students, but also for trainers. 
        She handles a wide range of administrative and managerial tasks in hopes of making campus life comfortable for all. 
        That said, if you break curfew, you'd better hope you can outrun her.

        You are also a helpful guide who answers every question in a clear and concise way.
        Do not answer anything that is not related to the question.
        Do not add follow-up question to your answer.
        Your answer must be under 2000 characters long.
        However when the answer is unknown, you must be honest and tell them that you do not know.

        Question: {question}
    '''

)


def call_tazuna(state: State):
    user_prompt = state["question"]
    
    message = prompt.invoke(user_prompt)

    response = llm.invoke(message)

    return {"answer": response.content}


workflow = StateGraph(State)
workflow.add_node("tazuna", call_tazuna)

workflow.add_edge(START, "tazuna")
workflow.add_edge("tazuna", END)

app = workflow.compile()

def ask(user_input):
    inputs = {"question": user_input}
    result = app.invoke(inputs)

    output_text = result["answer"]

    return output_text

if __name__ == "__main__":
    print(ask("Who are you?"))