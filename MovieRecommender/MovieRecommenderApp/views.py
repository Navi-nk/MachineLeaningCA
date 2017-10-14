from django.shortcuts import render
from MovieRecommenderApp.movie_api import getMovieDetails

# Create your views here.
from django.http import HttpResponse

def hello(request):
    text = """<h1>Apptesting !</h1>"""
    return HttpResponse(text)
   
def getmoviehomepage(request):
    return render(request, "./MovieRecommender/views/home.html", {"myvalue":"somevalue"})


def getresults(request):
    if request.method=="GET":
        data =  request.GET.get('search')
        getMovieDetails(data)
    return render(request, "./MovieRecommender/views/home.html", {"output":"Movie successfully saved in SearchMovieDetails.txt(under django project parent directory)"})
   
   