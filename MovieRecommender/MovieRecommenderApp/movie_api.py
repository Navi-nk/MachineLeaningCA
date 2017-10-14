import requests
import json

api_key = '333a07756aaff60e9afcc29ec3b69215'

base_movie_url = r'https://api.themoviedb.org/3/movie/'
base_search_url = r'https://api.themoviedb.org/3/search/movie'
api_key_url = r'?api_key=%s&language=en-US'%(api_key)

def getMovieId(movie):
    search_append = r'&query=%s&page=1&include_adult=false'%(movie)
    url = base_search_url + api_key_url + search_append
    response = requests.get(url)
    movie_id = None
    data = json.loads(response.content)
    movie_id = data['results'][0]['id']
#    for i in range(len(data['results'])):
#        search_title = data['results'][i]['title'].lower()
#        if search_title == movie.lower():
#            movie_id = data['results'][i]['id']
#            print('Found: %s, Id: %s'%(movie, movie_id))
#            break
#    if not movie_id:
#        print('Movie %s not found. Please enter movie name correctly'%(movie))
    return movie_id

def getMovieDetails(movie):
    movie_id = getMovieId(movie)
    if not movie_id:
        print("No movie Id provided. Quitting!!")
        return
    url = base_movie_url + str(movie_id) + api_key_url
    response = requests.get(url)
    data = json.loads(response.content)
    print(data)
    with open('SearchMovieDetails.txt', 'w') as md:
        md.write(str(data))

if __name__ == '__main__':
    getMovieDetails('avatar')
