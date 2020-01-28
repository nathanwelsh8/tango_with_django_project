from django.urls import path
from rango import views

# defined in admin.py
app_name = 'rango'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
]