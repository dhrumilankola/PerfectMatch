from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('resume-optimiser/', views.resume_optimiser, name='resume_optimiser'),
    path('jd-analysis/', views.jd_analysis, name='jd_analysis'),
    path('cover_letter/', views.cover_letter, name='cover_letter'),  # Ensure this line is present
    path('chatbot/', views.chatbot, name='chatbot'),
    path('chatbot_interact/', views.chatbot_interact, name='chatbot_interact'),

]
