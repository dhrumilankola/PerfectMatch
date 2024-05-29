from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='index'),
    path('resume-optimiser/', views.resume_optimiser, name='resume-optimiser'),  
    path('jd-analysis/', views.jd_analysis, name='jd-analysis'),  
]