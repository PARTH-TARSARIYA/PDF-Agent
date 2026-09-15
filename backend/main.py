from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
import tempfile
from fastapi import FastAPI, UploadFile, Form, HTTPException, File
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
import uuid

load_dotenv()

retriever_store = {}

app = FastAPI(
    title = 'PDF Question Answering API',
    description = 'Ask questions based on uploaded PDF document',
    version = '2.0.0'
)

@app.get('/')
def home():
    return {
        'message' : 'PDF QA is running'
    }

@app.get('/health')
def health():
    return {
        'status' : 'healthy' 
    }


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


def pdf_to_text(pdf):
    return "\n".join(page.page_content for page in pdf)

def rag_system(text):
    embedding_model = GoogleGenerativeAIEmbeddings(
        model = 'gemini-embedding-2'
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap = 20
    )

    chunk = splitter.split_text(text)

    vectore_store = FAISS.from_texts(chunk, embedding_model)

    retriever = vectore_store.as_retriever(search_type = 'similarity', search_kwargs = {'k' : 3})

    return retriever


def create_chain():
    model = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        temperature=0
    )

    prompt = PromptTemplate(
        template="""
        You are an expert at answering questions based only on the PDF context.

        Relavent PDF Context:
        {context}

        User Query:
        {query}

        Answer the user's question using only the PDF context.

        If the question cannot be answered from the PDF context, 
        simply write:
        "Your query is out of context!"
        """,
        input_variables=["context", "query"]
    )

    parser = StrOutputParser()

    return prompt | model | parser

chain = create_chain()

def ask_question(chain, pdf_content, user_input):
    return chain.invoke({
        "context": pdf_content,
        "query": user_input
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

        retriever = rag_system(pdf_content)

        session_id = str(uuid.uuid4())

        retriever_store[session_id] = retriever

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
        retriever = retriever_store.get(session_id)

        if not retriever:
            raise HTTPException(
                status_code = 404,
                detail = 'Session not found. Please upload pdf again.'
            )

        docs = retriever.invoke(question)

        context = '\n\n'.join(doc.page_content for doc in docs)

        answer = ask_question(chain, context, question)

        return {
            'question' : question,
            'answer' : answer
        }

    except Exception as e:
        raise HTTPException(
            status_code = 500,
            detail = str(e)
        )
    