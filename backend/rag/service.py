from pathlib import Path
from typing import Dict

from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains import RetrievalQA
from langchain_classic.prompts import PromptTemplate
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter

from backend.config import get_settings


def analyze_resume_with_job_description(
    resume_path: Path, job_description: str
) -> Dict[str, str]:
    """
    Run the RAG pipeline:
    - Load resume PDF
    - Chunk & embed
    - Build FAISS vectorstore
    - Query Gemini with custom prompt comparing to job description
    """
    settings = get_settings()
    if not settings.google_api_key:
        import os
        env_key = os.getenv("GOOGLE_API_KEY")
        raise RuntimeError(
            f"GOOGLE_API_KEY is not set. "
            f"Define it in your .env file at {Path(__file__).resolve().parent.parent.parent / '.env'}. "
            f"Current env value: {env_key[:10] + '...' if env_key else 'None'}"
        )

    # 1. Load and chunk resume
    loader = PyPDFLoader(str(resume_path))
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = text_splitter.split_documents(documents)

    # 2. Embeddings & vector store
    embeddings = HuggingFaceEmbeddings(model="all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(chunks, embeddings)

    # 3. Gemini LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        api_key=settings.google_api_key,
    )

    # 4. Prompt
    template = """
You are an expert HR Recruiter. Compare the provided Resume Context with the Job Description.

Resume Context: {context}
Job Description: {question}

Provide the output in this exact format:
1. Match Percentage: (0-100%)
2. Missing Keywords/Skills:
3. Experience Gap:
4. Verdict: (Shortlist or Reject)

Answer:
"""
    qa_prompt = PromptTemplate(template=template, input_variables=["context", "question"])

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
        chain_type_kwargs={"prompt": qa_prompt},
        return_source_documents=False,
    )

    result = qa_chain.invoke({"query": job_description})

    # LangChain RetrievalQA typically returns {"result": "...", "source_documents": [...]}
    if isinstance(result, dict) and "result" in result:
        return {"raw_result": result["result"]}

    # Fallback: return stringified result
    return {"raw_result": str(result)}

