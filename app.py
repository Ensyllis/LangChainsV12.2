from flask import Flask, request, jsonify, render_template
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain_openai import OpenAIEmbeddings, OpenAI
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from flask_cors import CORS


load_dotenv()

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

# Flask app setup
app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

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

if __name__ == '__main__':
    app.run(debug=True)


