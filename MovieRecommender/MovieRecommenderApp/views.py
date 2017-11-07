from django.shortcuts import render
from movie_api import call_recommend
from movie_api import getMovieImage

from django.http import HttpResponse

def getMoviePoster(request):
    moviename =  request.GET.get('moviename')
    moviename = r'%s'%(moviename)
    imageurl = getMovieImage(moviename)
    return HttpResponse(imageurl)
   
def getmoviehomepage(request):
    return render(request, "./MovieRecommender/views/home.html", {"myvalue":"somevalue"})


def getresults(request):
    if request.method=="GET":
        data =  request.GET.get('search')
        deleteSequels = request.GET.get('deletesequel')
        deleteSequels = string2bool(deleteSequels)
        print("value of deletesequel")
        print(deleteSequels)
        movieresultString = r'Search For Similar Movies like %s is Done!!!!'%(data)
        recommended = call_recommend(data, deleteSequels)
        movieStr = str(recommended)
        movieStr = movieStr.replace("[","")
        movieStr = movieStr.replace("]","")
        movieStr = movieStr.replace("\"","\'")
        print(movieStr)
        movieArr = movieStr.split('\',')
        imageurl = ''
        imgarray = []
        for movie in movieArr:
            print(movie)
            imgarray.append(getMovieImage(movie))
        return HttpResponse(imgarray)
def string2bool(v):
  return v.lower() in ("true")
   
   
