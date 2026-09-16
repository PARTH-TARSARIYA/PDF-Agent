from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
import tempfile
from fastapi import FastAPI, UploadFile, Form, HTTPException, File
import os
from langchain_core.messages import HumanMessage, AIMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
import uuid
import re
import unicodedata

load_dotenv()

retriever_store = {}
history_store = {}

# Fast api
app = FastAPI(
    title = 'PDF Question Answering API',
    description = 'Ask questions based on uploaded PDF document',
    version = '2.0.0'
)

# Home endpoint
@app.get('/')
def home():
    return {
        'message' : 'PDF QA is running'
    }

# Health endpoint
@app.get('/health')
def health():
    return {
        'status' : 'healthy' 
    }


# PDF loading to temperary file.
def load_pdf(uploaded_file:UploadFile):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:

        content = uploaded_file.file.read()
        temp_file.write(content)
        temp_path = temp_file.name

    loader = PyPDFLoader(temp_path)
    pages = loader.load()

    if os.path.exists(temp_path):
        os.remove(temp_path)

    return pages

# Fetch actual page content of pdf.
def pdf_to_text(pdf):
    return "\n".join(page.page_content for page in pdf)

# Text preprocessing.
def text_preprocessor(text):
    # unicode normalization
    text = unicodedata.normalize('NFKC', text)

    # html tag removal
    text = re.sub(r'<.*?>', '', text)

    # Remove control characters
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)

    # Fix words broken accross PDF lines
    text = re.sub(r'(\w)-\s*\n\s(\w)', r'\1\2', text)

    # Normalize spaces and tabs
    text = re.sub(r'[ \t]+', ' ', text)

    # Normalize excessive newline
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Remove standalone page numbers
    text = re.sub(
        r"(?m)^\s*\d+\s*$",
        "",
        text
    )

    # Strip leading/trailing whitespace
    text = text.strip()

    return text

# Rag system
def rag_system(text):
    embedding_model = GoogleGenerativeAIEmbeddings(
        model = 'gemini-embedding-2'
    )

    # Convert text to chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap = 20
    )

    chunk = splitter.split_text(text)

    # Vectore database
    vectore_store = FAISS.from_texts(chunk, embedding_model)

    # Retriever
    retriever = vectore_store.as_retriever(search_type = 'similarity', search_kwargs = {'k' : 3})

    return retriever


def create_chain():

    # Google genrative model
    model = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        temperature=0
    )

    # System prompt temple
    prompt = PromptTemplate(
        template="""
        You are an expert at answering questions based only on the PDF context.
        Also check conversation history to check user interaction.

        Conversation history:
        {history}

        Relavent PDF Context:
        {context}

        User Query:
        {query}

        Answer the user's question using only the PDF context.
        understand user's question properly and then answer it.

        If the question cannot be answered from the PDF context, 
        simply write:
        "Your query is out of context!"
        """,
        input_variables=["context", "query", 'history']
    )

    parser = StrOutputParser()

    return prompt | model | parser

chain = create_chain()

def ask_question(chain, pdf_content, user_input, history):
    return chain.invoke({
        "context": pdf_content,
        "query": user_input,
        "history" : history
    })


@app.post('/text')
async def TextAndRAG(
    file : UploadFile = File()
):
    if file.content_type != 'application/pdf':
        raise HTTPException(
            status_code = 400,
            detail = 'Upload pdf file only'
        )
    

    try:
        pdf = load_pdf(file)
        
        pdf_content = pdf_to_text(pdf)

        preprocessed_content = text_preprocessor(pdf_content)

        retriever = rag_system(preprocessed_content)

        session_id = str(uuid.uuid4())      # Unique session id

        retriever_store[session_id] = retriever  # Store retriever to session

        return {
            'session_id' : session_id,
            'message' : 'PDF uploaded and RAG system created successfully'
        }

    except Exception as e:
        raise HTTPException(
            status_code = 500,
            detail = str(e)
        )


@app.post('/ask')
async def ask(
    session_id : str = Form(),
    question : str = Form()
):
    try:
        if session_id not in history_store:
            history_store[session_id] = []

        retriever = retriever_store.get(session_id)     # Fetch pdf retriever for perticular session.

        if not retriever:
            raise HTTPException(
                status_code = 404,
                detail = 'Session not found. Please upload pdf again.'
            )

        docs = retriever.invoke(question)       # Retrieve relavent documents from vectore DB.

        history = history_store[session_id][-10:]       # Last 10 conversations only.

        context = '\n\n'.join(doc.page_content for doc in docs)

        answer = ask_question(chain, context, question, history)        # Ask question to LLM.

        history.append(HumanMessage(content = question))        # Append user content to history.
        history.append(AIMessage(content = answer))             # Append LLM output to history.

        return {
            'question' : question,
            'answer' : answer
        }

    except Exception as e:
        raise HTTPException(
            status_code = 500,
            detail = str(e)
        )
    