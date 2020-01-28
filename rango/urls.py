from django.urls import path
from rango import views

# from admin.py
app_name = 'rango'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
]