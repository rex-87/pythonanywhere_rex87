from django.shortcuts import render, HttpResponse

def home(request):
	context = {}
	return render(request, 'pythonanywhere_rex87/home.html', context)