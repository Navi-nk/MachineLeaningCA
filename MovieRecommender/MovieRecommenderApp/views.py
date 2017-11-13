from django.shortcuts import render
from movie_api import call_recommend
from movie_api import get_movie_image
from django.http import HttpResponse


def get_movie_poster(request):
    movie_name = request.GET.get('moviename')
    movie_name = r'%s' % movie_name
    image_url = get_movie_image(movie_name)
    return HttpResponse(image_url)


def get_movie_homepage(request):
    return render(request, "./MovieRecommender/views/home.html", {"myvalue": "somevalue"})


def get_results(request):
    if request.method == "GET":
        data = request.GET.get('search')
        delete_sequels = string2bool(request.GET.get('deletesequel'))
        print("Delete Sequel: ", delete_sequels)
        recommended = call_recommend(data, delete_sequels)
        img_array = []
        for movie in recommended:
            img_array.append(get_movie_image(movie))
        return HttpResponse(img_array)


def string2bool(v):
    return v.lower() in "true"
