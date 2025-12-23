from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('<slug:slug>/', views.course_detail, name='course_detail'),
    path('<slug:slug>/enroll/', views.enroll_course, name='enroll_course'),
    path('payment/<int:enrollment_id>/', views.payment, name='payment'),
    path('registration/<int:enrollment_id>/', views.course_registration, name='course_registration'),
]