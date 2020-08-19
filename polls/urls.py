from django.urls import path, include
from . import views

urlpatterns = [
  path('', views.button, name="home"),
  path('run-script/', views.add_task, name="script")
]