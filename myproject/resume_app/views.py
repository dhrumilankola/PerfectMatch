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
    "Resume Text: {resume_text}"
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
def generate_cover_letter(job_description, resume_text):
    full_prompt = fixed_prompt_cover_letter.format(
        job_description=job_description,
        resume_text=resume_text
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
    return text
# Home view
def home(request):
    return render(request, 'index.html')

# Function to stream the response
def stream_response(response):
    for chunk in response:
        yield f"data: {markdown.markdown(chunk.text)}\n\n"

# Resume Optimiser view with AJAX handling and streaming response
@csrf_exempt
def resume_optimiser(request):
    if request.method == 'POST':
        user_input = request.POST.get('input')
        role = request.POST.get('role')
        full_prompt = fixed_prompt_resume.format(role=role) + user_input
        response = model.generate_content(full_prompt, stream=True)
        return StreamingHttpResponse(stream_response(response), content_type='text/event-stream')
    return render(request, 'resume_optimiser.html')

# Home view
def home(request):
    return render(request, 'index.html')

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

# Cover Letter Generator view with AJAX handling
@csrf_exempt
def cover_letter(request):
    if request.method == 'POST':
        job_description = request.POST.get('job_description')
        resume_pdf = request.FILES.get('resume_pdf')
        
        if not resume_pdf:
            return JsonResponse({'error': 'Resume PDF file is required.'}, status=400)
        
        try:
            # Convert the uploaded PDF to text
            resume_text = extract_text_from_pdf(resume_pdf)
            response = generate_cover_letter(job_description, resume_text)
            return JsonResponse({'cover_letter': response})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return render(request, 'cover_letter.html')
