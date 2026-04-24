import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def analyze_resume(pdf_path, job_description):
    """Simple resume analysis without complex dependencies"""
    try:
        # Load PDF
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        resume_text = "\n".join([doc.page_content for doc in docs])
        
        # Simple keyword-based analysis
        resume_text_lower = resume_text.lower()
        job_text_lower = job_description.lower()
        
        # Extract common skills
        common_skills = [
            "python", "java", "javascript", "react", "node.js", "sql", "mongodb",
            "aws", "docker", "kubernetes", "git", "machine learning", "data analysis",
            "tensorflow", "pytorch", "flask", "django", "html", "css", "typescript",
            "angular", "vue.js", "postgresql", "mysql", "redis", "nginx", "linux",
            "ci/cd", "agile", "scrum", "testing", "unit testing", "integration testing",
            "c++", "c#", ".net", "azure", "gcp", "firebase", "rest api", "graphql",
            "microservices", "devops", "jira", "confluence", "slack", "office 365",
            "excel", "powerpoint", "word", "project management", "leadership"
        ]
        
        found_skills = [skill for skill in common_skills if skill in resume_text_lower]
        required_skills = [skill for skill in common_skills if skill in job_text_lower]
        matching_skills = [skill for skill in found_skills if skill in required_skills]
        
        # Extract experience indicators
        experience_years = []
        year_patterns = [
            r'(\d+)\s*years?',
            r'(\d+)\s*year',
            r'(\d+)\s+yrs?',
        ]
        
        import re
        for pattern in year_patterns:
            matches = re.findall(pattern, resume_text_lower)
            experience_years.extend([int(match) for match in matches])
        
        total_experience = max(experience_years) if experience_years else 0
        
        # Extract education keywords
        education_keywords = [
            "bachelor", "master", "phd", "doctorate", "degree", "university",
            "college", "institute", "academy", "school", "b.sc", "m.sc", "mba",
            "computer science", "engineering", "business", "arts", "science"
        ]
        
        education_found = [keyword for keyword in education_keywords if keyword in resume_text_lower]
        
        # Calculate score based on multiple factors
        score = 0
        
        # Skills matching (40% of score)
        if len(required_skills) > 0:
            skill_score = (len(matching_skills) / len(required_skills)) * 40
        else:
            skill_score = min(len(found_skills) * 2, 40)
        score += skill_score
        
        # Experience score (30% of score)
        experience_score = min(total_experience * 3, 30)
        score += experience_score
        
        # Education score (20% of score)
        education_score = min(len(education_found) * 4, 20)
        score += education_score
        
        # Resume quality score (10% of score)
        resume_length_score = min(len(resume_text) / 100, 10)
        score += resume_length_score
        
        # Generate suggestions
        suggestions = []
        
        if len(matching_skills) < len(required_skills):
            missing_skills = [skill for skill in required_skills if skill not in matching_skills]
            if missing_skills:
                suggestions.append(f"Consider adding these skills: {', '.join(missing_skills[:5])}")
        
        if total_experience < 2:
            suggestions.append("Add more detailed work experience with specific years")
        
        if len(education_found) == 0:
            suggestions.append("Include your education details in the resume")
        
        if len(resume_text) < 500:
            suggestions.append("Your resume seems too short - add more details about your experience")
        elif len(resume_text) > 3000:
            suggestions.append("Consider shortening your resume to highlight key achievements")
        
        suggestions.append("Add quantifiable achievements (e.g., 'increased efficiency by 30%')")
        suggestions.append("Tailor your resume to the specific job description")
        
        # Extract contact information
        contact_info = {}
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, resume_text)
        if emails:
            contact_info['email'] = emails[0]
        
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        phones = re.findall(phone_pattern, resume_text)
        if phones:
            contact_info['phone'] = phones[0]
        
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin_matches = re.findall(linkedin_pattern, resume_text, re.IGNORECASE)
        if linkedin_matches:
            contact_info['linkedin'] = "https://" + linkedin_matches[0]
        
        return f"""
# 📊 Resume Analysis Report

## 🎯 Overall Score: {score:.1f}/100

### 📋 Score Breakdown:
- **Skills Matching**: {skill_score:.1f}/40
- **Experience**: {experience_score:.1f}/30  
- **Education**: {education_score:.1f}/20
- **Resume Quality**: {resume_length_score:.1f}/10

## 👤 Contact Information Found:
{chr(10).join([f'- {k}: {v}' for k, v in contact_info.items()]) if contact_info else '- No contact information found'}

## 💡 Skills Found ({len(found_skills)}):
{', '.join(found_skills) if found_skills else 'No specific skills detected'}

## 🎯 Skills Matching Job Description ({len(matching_skills)}/{len(required_skills)}):
{', '.join(matching_skills) if matching_skills else 'No matching skills found'}

## 📚 Education Indicators:
{', '.join(education_found) if education_found else 'No education keywords found'}

## 💼 Experience:
- **Total Years**: {total_experience} years
- **Resume Length**: {len(resume_text)} characters

## 🚀 Recommendations:
{chr(10).join([f'{i+1}. {suggestion}' for i, suggestion in enumerate(suggestions)])}

---
*This analysis is based on keyword matching and pattern recognition. For more detailed analysis, consider adding specific metrics and achievements to your resume.*
        """
    except Exception as e:
        return f"❌ Error analyzing resume: {str(e)}. Please check your resume file and try again."


# Keep the original function name for compatibility
def analyze_resume_simple(pdf_path, job_description):
    return analyze_resume(pdf_path, job_description)
