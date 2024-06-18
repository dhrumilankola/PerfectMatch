from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai
import os
from dotenv import load_dotenv
import markdown
import fitz
import logging 

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configure the generative AI with the API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load the generative model
model = genai.GenerativeModel("gemini-1.5-flash")

# Fixed prompts
fixed_prompt_resume = "Tailor these points in my resume for {role}, 1 of the points in an input should be quantified: "
fixed_prompt_jd = "Extract important keywords and required skills from the following job description: "

# Fixed prompt for cover letter generation
fixed_prompt_cover_letter = (
    "Generate a professional cover letter for the following job description and resume details. "
    "The cover letter should:\n"
    "1. Automatically fill in placeholders such as [Hiring Manager name], [Your previous role title], [Previous company], [list your proficient programming languages from resume], "
    "[Briefly mention relevant responsibilities from your resume], [Project name], [Relevant programming languages], [Quantifiable result], [Skill mentioned in the job description], "
    "[Mention relevant coding challenge platforms], and [Your Name] with appropriate details extracted from the resume.\n"
    "2. Highlight relevant skills, work experience, and projects from the resume that match the job description.\n"
    "3. Be concise, with a clear structure that includes an introduction, body paragraphs, and a conclusion.\n"
    "4. Use a human and engaging tone to appeal to the reader.\n"
    "5. Emphasize the candidate's fit for the role and enthusiasm for the position.\n"
    "6. Include specific examples from the resume that demonstrate the candidate's qualifications and achievements.\n"
    "7. Avoid generic statements and focus on how the candidate can add value to the company.\n"
    "Here are the details:\n\n"
    "Job Description: {job_description}\n\n"
    "Resume Details:\n"
    "Work Experience: {work_experience}\n"
    "Projects: {projects}\n"
    "Skills: {skills}\n"
    "Certifications: {certifications}\n"
    "Coding Challenges: {coding_challenges}\n"
    "Personal Information: {personal_information}"
)

# Function to get gemini response for resume optimization
def get_gemini_response(user_input, role):
    full_prompt = fixed_prompt_resume.format(role=role) + user_input
    response = model.generate_content(full_prompt)
    if hasattr(response, 'text'):
        return markdown.markdown(response.text)
    elif hasattr(response, 'content'):
        return markdown.markdown(response.content)
    else:
        return "Unexpected response structure."

# Function to get gemini response for general queries
def get_general_gemini_response(question):
    try:
        chat = model.start_chat(history=[])
        response = chat.send_message(question, stream=True)
        response_text = ''.join(chunk.text for chunk in response)
        return markdown.markdown(response_text)
    except Exception as e:
        logger.error(f"Error in get_general_gemini_response: {str(e)}")
        return None


# Function to handle chatbot interaction
@csrf_exempt
def chatbot_interact(request):
    if request.method == 'POST':
        try:
            user_input = request.POST.get('user_input')
            logger.debug(f"User input: {user_input}")
            response_text = get_general_gemini_response(user_input)
            if response_text:
                return JsonResponse({'bot_response': response_text})
            else:
                return JsonResponse({'bot_response': 'Sorry, an error occurred while processing your request.'}, status=500)
        except Exception as e:
            logger.error(f"Error in chatbot_interact: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    return render(request, 'chatbot.html')

# Function to analyze job description
def analyze_job_description(job_description):
    full_prompt = fixed_prompt_jd + job_description
    response = model.generate_content(full_prompt)
    if hasattr(response, 'text'):
        return markdown.markdown(response.text)
    elif hasattr(response, 'content'):
        return markdown.markdown(response.content)
    else:
        return "Unexpected response structure."

# Function to generate cover letter
def generate_cover_letter(job_description, resume_details):
    work_experience = resume_details.get("work_experience", "N/A")
    projects = resume_details.get("projects", "N/A")
    skills = resume_details.get("skills", "N/A")
    certifications = resume_details.get("certifications", "N/A")
    coding_challenges = resume_details.get("coding_challenges", "N/A")
    personal_information = resume_details.get("personal_information", "N/A")

    full_prompt = fixed_prompt_cover_letter.format(
        job_description=job_description,
        work_experience=work_experience,
        projects=projects,
        skills=skills,
        certifications=certifications,
        coding_challenges=coding_challenges,
        personal_information=personal_information
    )
    response = model.generate_content(full_prompt)
    if hasattr(response, 'text'):
        return markdown.markdown(response.text)
    elif hasattr(response, 'content'):
        return markdown.markdown(response.content)
    else:
        return "Unexpected response structure."

# Helper function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    import fitz  # PyMuPDF
    text = ""
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    for page in doc:
        text += page.get_text()
    
    # Here we can use simple string operations to extract structured data
    # For demonstration purposes, this is simplified and should be improved with proper NLP techniques
    resume_details = {
        "work_experience": extract_section(text, "Work Experience"),
        "projects": extract_section(text, "Projects"),
        "skills": extract_section(text, "Skills"),
        "certifications": extract_section(text, "Certifications"),
        "coding_challenges": extract_section(text, "Coding Challenges"),
        "personal_information": extract_section(text, "Personal Information")
    }
    
    return resume_details

def extract_section(text, section_title):
    # A simple way to extract sections based on title
    start = text.find(section_title)
    if start == -1:
        return "N/A"
    
    end = text.find("\n\n", start)
    if end == -1:
        end = len(text)
    
    section_text = text[start:end].strip()
    return section_text


# Home view
def home(request):
    return render(request, 'index.html')

def chatbot(request):
    return render(request, 'chatbot.html')

# Resume Optimiser view with AJAX handling
@csrf_exempt
def resume_optimiser(request):
    if request.method == 'POST':
        user_input = request.POST.get('input')
        role = request.POST.get('role')
        response = get_gemini_response(user_input, role)
        return JsonResponse({'response': response})
    return render(request, 'resume_optimiser.html')

# JD Analysis view with AJAX handling
@csrf_exempt
def jd_analysis(request):
    if request.method == 'POST':
        job_description = request.POST.get('input')
        response = analyze_job_description(job_description)
        return JsonResponse({'response': response})
    return render(request, 'jd_analysis.html')

# Cover Letter Generator view to extract resume text
@csrf_exempt
def extract_resume_text(request):
    if request.method == 'POST':
        resume_pdf = request.FILES.get('resume_pdf')
        if not resume_pdf:
            return JsonResponse({'error': 'Resume PDF file is required.'}, status=400)
        
        try:
            resume_text = extract_text_from_pdf(resume_pdf)
            return JsonResponse({'resume_text': resume_text})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)


# Cover Letter Generator view
@csrf_exempt
def cover_letter(request):
    if request.method == 'POST':
        job_description = request.POST.get('job_description')
        resume_pdf = request.FILES.get('resume_pdf')
        
        if not resume_pdf:
            return JsonResponse({'error': 'Resume PDF file is required.'}, status=400)
        
        try:
            # Extract text from PDF and structure it into relevant sections
            resume_details = extract_text_from_pdf(resume_pdf)
            
            # Generate cover letter
            response = generate_cover_letter(job_description, resume_details)
            
            return JsonResponse({'cover_letter': response, 'resume_text': resume_details})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return render(request, 'cover_letter.html')
