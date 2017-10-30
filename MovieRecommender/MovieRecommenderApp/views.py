from django.shortcuts import render
from movie_api import call_recommend
from movie_api import getMovieImage

from django.http import HttpResponse

def hello(request):
    text = """<h1>Apptesting !</h1>"""
    return HttpResponse(text)
   
def getmoviehomepage(request):
    return render(request, "./MovieRecommender/views/home.html", {"myvalue":"somevalue"})


def getresults(request):
    if request.method=="GET":
        data =  request.GET.get('search')
        movieresultString = "Search For Similar Movies like "+data+" is Done!!!!"
        recommended = call_recommend(data)
        movieStr = str(recommended)
        movieStr = movieStr.replace("[","")
        movieStr = movieStr.replace("]","")
        print('hello#######################')
        print(movieStr)
        movieArr = movieStr.split(',')
        imageurl = ''
        imgarray = []
        for movie in movieArr:
            print(movie)
            imgarray.append(getMovieImage(movie))
            imageurl = getMovieImage(movie)
    return render(request, "./MovieRecommender/views/home.html", {"output":str(recommended),"img":imgarray,"movieresult":movieresultString} )
   
   
