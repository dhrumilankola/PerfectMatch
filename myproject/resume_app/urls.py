from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('resume-optimiser/', views.resume_optimiser, name='resume_optimiser'),
    path('jd-analysis/', views.jd_analysis, name='jd_analysis'),
    path('cover-letter/', views.cover_letter, name='cover_letter'),

]
