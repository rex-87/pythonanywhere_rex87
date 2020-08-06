from django.urls import path

from . import views

app_name = 'corona'
urlpatterns = [
    path('', views.home, name='home'),
    path('data/', views.data, name='data'),
]