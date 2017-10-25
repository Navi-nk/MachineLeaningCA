from django.shortcuts import render
from movie_api import call_recommend

from django.http import HttpResponse

def hello(request):
    text = """<h1>Apptesting !</h1>"""
    return HttpResponse(text)
   
def getmoviehomepage(request):
    return render(request, "./MovieRecommender/views/home.html", {"myvalue":"somevalue"})


def getresults(request):
    if request.method=="GET":
        data =  request.GET.get('search')
        recommended = call_recommend(data)
    return render(request, "./MovieRecommender/views/home.html", {"output":str(recommended)})
   
   