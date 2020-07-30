from django.urls import path

from . import views

app_name = 'covid19_plots'
urlpatterns = [
    path('', views.index, name='index'),
    path('edit', views.edit, name='edit'),
]