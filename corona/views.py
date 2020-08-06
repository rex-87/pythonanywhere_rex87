from django.shortcuts import render, HttpResponse
from django.http import JsonResponse

# Create your views here.

def home(request):
    context = {}
    return render(request, 'corona/home.html', context)

def data(request):

    chart = {
        'chart': {
            'type': 'column',
            # 'width': '100%',
            # 'height': '100%',
        },
        'title': {
            'text': 'Historic World Population by Region',
        },
        'xAxis': {
            'categories': ['Africa', 'America', 'Asia', 'Europe', 'Oceania'],
        },
        'series': [
            {
                'name': 'Year 1800',
                'data': [107, 31, 635, 203, 2],
            }, 
            {
                'name': 'Year 1900',
                'data': [133, 156, 947, 408, 6],
            }, 
            {
                'name': 'Year 2012',
                'data': [1052, 954, 4250, 740, 38],
            },
        ],
    }

    return JsonResponse(chart)
