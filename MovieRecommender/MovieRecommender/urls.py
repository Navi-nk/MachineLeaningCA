"""MovieRecommender URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URL conf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from MovieRecommenderApp.views import get_movie_homepage, get_results, get_movie_poster


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^movies/', get_movie_homepage),
    url(r'^result/', get_results),
    url(r'^movieposter/', get_movie_poster)
]
