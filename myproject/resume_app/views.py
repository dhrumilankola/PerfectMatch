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

# Define the fixed prompt
fixed_prompt = "Tailor these points in my resume for Software Engineer role, 1 out of 3 points in an input should be quantified: "

# Function to get gemini response
def get_gemini_response(user_input):
    full_prompt = fixed_prompt + user_input
    response = model.generate_content(full_prompt)
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
        response = get_gemini_response(user_input)
        response = mark_safe(response)
        return render(request, 'home.html', {'response': response, 'input': user_input})
    return render(request, 'resume_optimiser.html')

def jd_analysis(request):
    if request.method == 'POST':
        user_input = request.POST.get('input', '')
        # Assume get_jd_analysis_response is a function you'll implement
        response = get_jd_analysis_response(user_input)
        # Ensure the HTML is safe to render
        safe_response = mark_safe(response)
        return render(request, 'jd_analysis.html', {'response': safe_response, 'input': user_input})
    return render(request, 'jd_analysis.html')
