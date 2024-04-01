from flask import Flask, request, jsonify, render_template, Blueprint, flash
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain_openai import OpenAIEmbeddings, OpenAI
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from flask_cors import CORS
from flask_login import login_required, current_user
from . import create_app

load_dotenv()

main = Blueprint('app', __name__)

# Environment variables and MongoDB setup
MONGODB_ATLAS_CLUSTER_URI = os.getenv("MONGODB_ATLAS_CLUSTER_URI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_NAME = "Anchor"
COLLECTION_NAME = "ResearchV1"
ATLAS_VECTOR_SEARCH_INDEX_NAME = "vector_index"


client = MongoClient(MONGODB_ATLAS_CLUSTER_URI)
mongodb_collection = client[DB_NAME][COLLECTION_NAME]


vector_search = MongoDBAtlasVectorSearch.from_connection_string(
    MONGODB_ATLAS_CLUSTER_URI,
    DB_NAME + "." + COLLECTION_NAME,
    OpenAIEmbeddings(model="text-embedding-3-small",disallowed_special=()),
    index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
)

qa_retriever = vector_search.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 4},
)

prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

{context}

Question: {question}
"""

PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)


qa = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    chain_type="stuff",
    retriever=qa_retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": PROMPT},
)

def get_answer(question):
    """
    Takes a user question and returns the answer along with the source documents.
    
    :param question: str
    :return: dict
    """
    try:
        # Retrieve documents and answer
        docs = qa({"query": question})
        
        result = docs.get("result")
        
        return {
            "result": result,
        }
    except Exception as e:
        return {"error": str(e)}

def soteriology_query(question):
    DB_NAME_SOT = "TimeManagement"
    COLLECTION_NAME_SOT = "TimeManagement"
    ATLAS_VECTOR_SEARCH_INDEX_NAME_SOT = "vector_index"

    client = MongoClient(MONGODB_ATLAS_CLUSTER_URI)
    mongodb_collection = client[DB_NAME_SOT][COLLECTION_NAME_SOT]

    vector_search = MongoDBAtlasVectorSearch.from_connection_string(
        MONGODB_ATLAS_CLUSTER_URI,
        DB_NAME_SOT + "." + COLLECTION_NAME_SOT,
        OpenAIEmbeddings(model="text-embedding-3-small",disallowed_special=()),
        index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME_SOT,
    )

    qa_retriever = vector_search.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 25},
    )

    prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

    {context}

    Question: {question}
    """

    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    qa = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    chain_type="stuff",
    retriever=qa_retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": PROMPT},
    )

    def get_answer_sot(question):
        try:
            # Retrieve documents and answer
            docs = qa({"query": question})

            result = docs.get("result")
            page_contents = [doc.page_content for doc in docs.get("source_documents", [])]

            return {
                "result": result,
                "source_documents": page_contents
            }
        except Exception as e:
            return {"error": str(e)}

    return get_answer_sot(question)







# Flask app setup
app = create_app()
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/guide')
def guide():
    return render_template('guide.html')

@app.route('/soteriology_query', methods=['POST'])
def soteriology():
    # Get data
    data = request.json
    user_prompt = data.get('prompt', '')
    
    # Use the LLM RAG to process the prompt
    response = soteriology_query(user_prompt)
    
    return jsonify(response)

@app.route('/query', methods=['POST'])
def query():
    # Get data
    data = request.json
    user_prompt = data.get('prompt', '')
    
    # Use the LLM RAG to process the prompt
    response = get_answer(user_prompt)
    
    return jsonify(response)

@app.route('/elements')
def elements():
    return render_template('elements.html')

@app.route('/generic')
def generic():
    return render_template('generic.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/profile') # profile page that return 'profile'
def profile():
    return render_template('profile.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

if __name__ == '__main__':
    db.create_all(app=create_app()) # create the SQLite database
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True) # run the flask app on debug mode