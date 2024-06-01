from django.shortcuts import render
from django.utils.safestring import mark_safe
import google.generativeai as genai
import os
from dotenv import load_dotenv
import markdown

# Load environment variables
load_dotenv()

# Configure the generative AI with the API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load the generative model
model = genai.GenerativeModel("gemini-1.5-flash")

fixed_prompt = "Tailor these points in my resume for {role}, 1 of the points in an input should be quantified: "

# Function to get gemini response
def get_gemini_response(user_input, role):
    full_prompt = fixed_prompt.format(role=role) + user_input
    response = genai.GenerativeModel("gemini-1.5-flash").generate_content(full_prompt)
    if hasattr(response, 'text'):
        return markdown.markdown(response.text)
    elif hasattr(response, 'content'):
        return markdown.markdown(response.content)
    else:
        return "Unexpected response structure."
    

fixed_prompt_jd = "Extract important keywords and required skills from the following job description: "

def analyze_job_description(job_description):
    full_prompt = fixed_prompt_jd + job_description
    response = genai.GenerativeModel("gemini-1.5-flash").generate_content(full_prompt)
    if hasattr(response, 'text'):
        return markdown.markdown(response.text)
    elif hasattr(response, 'content'):
        return markdown.markdown(response.content)
    else:
        return "Unexpected response structure."
        
def home(request):
    return render(request, 'index.html')

def resume_optimiser(request):
    if request.method == 'POST':
        user_input = request.POST.get('input')
        role = request.POST.get('role')
        response = get_gemini_response(user_input, role)
        return render(request, 'resume_optimiser.html', {'response': response, 'input': user_input})
    return render(request, 'resume_optimiser.html')


def jd_analysis(request):
    if request.method == 'POST':
        job_description = request.POST.get('input')
        response = analyze_job_description(job_description)
        return render(request, 'jd_analysis.html', {'response': response, 'input': job_description})
    return render(request, 'jd_analysis.html')