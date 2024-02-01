from django.urls import path
from . import views

urlpatterns = [
   path('', views.index),

   path('listings/', views.listings),
   path('listings/<slug:slug>/', views.listing),

   path('auth/', views.profile),
   path('auth/signup/', views.signup),
   path('auth/login/', views.login)
]
