from django.urls import path
from . import views

urlpatterns = [
  path('', views.button, name="home"),
  path('output/', views.output, name="script")
]