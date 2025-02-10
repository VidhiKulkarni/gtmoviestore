import requests
from django.conf import settings

def fetch_movie_from_omdb(movie_name):
    api_key = settings.OMDB_API_KEY
    url = f"http://www.omdbapi.com/?t={movie_name}&apikey={api_key}"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data['Response'] == 'True':
            return {
                'name': data.get('Title', 'Unknown'),
                'description': data.get('Plot', 'No description available'),
                'image': data.get('Poster', ''),  # Map OMDb poster to image
                'price': 15.00
            }
        else:
            return None
    else:
        raise Exception("Error fetching data from OMDb API")


import requests
from django.conf import settings


def fetch_movies_list(search_term):
    api_key = settings.OMDB_API_KEY
    url = f"http://www.omdbapi.com/?s={search_term}&apikey={api_key}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['Response'] == 'True':
            return data['Search']  # Return a list of movie search results
    return []

def fetch_movie_details(movie_title):
    api_key = settings.OMDB_API_KEY
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={api_key}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['Response'] == 'True':
            return {
                'name': data.get('Title', 'Unknown'),
                'description': data.get('Plot', 'No description available'),
                'image': data.get('Poster', ''),
                'price': 15.00  # Default price
            }
    return None