from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('exam/<int:exam_id>/', views.start_exam, name='start_exam'),
    path('submit_exam/', views.submit_exam, name='submit_exam'),  # ✅ Add this
]
