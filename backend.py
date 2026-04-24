import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from crewai import Agent, Task, Crew
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up OpenAI LLM (you can replace with Ollama if needed)
try:
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.7,
        openai_api_key=os.getenv("OPENAI_API_KEY", "sk-test-key")
    )
except:
    # Fallback to a basic setup if OpenAI key is not available
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.7,
        openai_api_base="http://localhost:11434/v1",
        openai_api_key="ollama"
    )

# STEP 1: Load + Store Resume (LangChain + RAG)
def setup_resume_rag(pdf_path):
    try:
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )

        chunks = splitter.split_documents(docs)
        
        # Try to use OpenAI embeddings, fallback to simple approach
        try:
            vectorstore = Chroma.from_documents(
                chunks,
                OpenAIEmbeddings()
            )
            return vectorstore
        except:
            # If embeddings fail, return chunks directly
            return chunks
    except Exception as e:
        print(f"Error in setup_resume_rag: {e}")
        return None

# STEP 2: Retrieve Relevant Context
def get_resume_context(vectorstore, job_description):
    try:
        if hasattr(vectorstore, 'similarity_search'):
            results = vectorstore.similarity_search(job_description, k=4)
            return "\n".join([r.page_content for r in results])
        else:
            # If vectorstore is just chunks, return first few chunks
            return "\n".join([chunk.page_content for chunk in vectorstore[:4]])
    except Exception as e:
        print(f"Error in get_resume_context: {e}")
        return "Resume content could not be processed."

# STEP 3: Analyze Resume using CrewAI (3 Agents ONLY)
def analyze_resume(pdf_path, job_description):
    try:
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
    except Exception as e:
        # Fallback analysis if CrewAI fails
        return fallback_analysis(pdf_path, job_description)

def fallback_analysis(pdf_path, job_description):
    """Simple fallback analysis when CrewAI fails"""
    try:
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        resume_text = "\n".join([doc.page_content for doc in docs])
        
        # Simple keyword-based analysis
        resume_text_lower = resume_text.lower()
        job_text_lower = job_description.lower()
        
        # Extract common skills
        common_skills = ["python", "java", "javascript", "sql", "aws", "docker", "machine learning", "data analysis"]
        found_skills = [skill for skill in common_skills if skill in resume_text_lower]
        required_skills = [skill for skill in common_skills if skill in job_text_lower]
        matching_skills = [skill for skill in found_skills if skill in required_skills]
        
        # Calculate simple score
        if len(required_skills) > 0:
            score = (len(matching_skills) / len(required_skills)) * 100
        else:
            score = 50  # Default score
        
        # Generate suggestions
        suggestions = []
        if len(matching_skills) < len(required_skills):
            missing_skills = [skill for skill in required_skills if skill not in matching_skills]
            suggestions.append(f"Consider adding these skills: {', '.join(missing_skills)}")
        
        suggestions.append("Add quantifiable achievements to your resume")
        suggestions.append("Tailor your resume to the specific job description")
        
        return f"""
# Resume Analysis Report

## Score: {score:.1f}/100

## Found Skills:
{', '.join(found_skills)}

## Matching Skills:
{', '.join(matching_skills)}

## Suggestions:
{chr(10).join([f'- {suggestion}' for suggestion in suggestions])}

## Note:
This is a basic analysis. For more detailed analysis, please ensure OpenAI API key is properly configured.
        """
    except Exception as e:
        return f"Error analyzing resume: {str(e)}. Please check your resume file and try again."
