import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from crewai import Agent, Task, Crew

# API Key
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OLLAMA")  

BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

def chat_with_ollama(prompt):
    url = f"{BASE_URL}/api/generate"

    headers = {
        "Content-Type": "application/json",
    }

    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"

    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()["response"]
    else:
        return f"Error: {response.text}"


if __name__ == "__main__":
    user_input = input("Ask something: ")
    reply = chat_with_ollama(user_input)
    print("\nOllama Response:\n", reply)


def setup_resume_rag(pdf_path):
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = splitter.split_documents(docs)

    vectorstore = Chroma.from_documents(
        chunks,
        OpenAIEmbeddings()
    )

    return vectorstore


def get_resume_context(vectorstore, job_description):
    results = vectorstore.similarity_search(job_description, k=4)
    return "\n".join([r.page_content for r in results])


def analyze_resume(pdf_path, job_description):

    vectorstore = setup_resume_rag(pdf_path)
    resume_context = get_resume_context(vectorstore, job_description)

    # Agent 1: Extractor
    extractor = Agent(
        role="Resume Extractor",
        goal="Extract skills, experience, education",
        backstory="Expert in reading resumes and extracting key info.",
        llm=llm,
        verbose=False
    )

    # Agent 2: Matcher
    matcher = Agent(
        role="Job Matcher",
        goal="Compare resume with job description and find gaps",
        backstory="Recruiter who understands hiring requirements.",
        llm=llm,
        verbose=False
    )

    # Agent 3: Career Coach
    coach = Agent(
        role="Career Coach",
        goal="Give score out of 100 and suggest improvements",
        backstory="Helps candidates improve resumes.",
        llm=llm,
        verbose=False
    )

    # Tasks
    task1 = Task(
        description=f"Extract skills, experience, education from:\n{resume_context}",
        agent=extractor,
        expected_output="Bulleted list of skills, experience, education"
    )

    task2 = Task(
        description=f"Compare the extracted info with this job:\n{job_description}",
        agent=matcher,
        expected_output="Matching skills and missing skills"
    )

    task3 = Task(
        description="Give a match score out of 100 and 3-5 improvement tips",
        agent=coach,
        expected_output="Score and suggestions"
    )

    # Crew
    crew = Crew(
        agents=[extractor, matcher, coach],
        tasks=[task1, task2, task3],
        verbose=False
    )

    result = crew.kickoff()
    return result