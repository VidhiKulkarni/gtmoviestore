from django.shortcuts import render, get_object_or_404
from .models import Movie
from .utils import fetch_movie_from_omdb
from .utils import fetch_movies_list


def load_default_movies():
    # List of 20 popular or random movies to preload
    default_movies = [
        "Inception", "Interstellar", "The Dark Knight", "Titanic", "Avatar",
        "The Avengers", "Forrest Gump", "The Matrix", "Gladiator", "The Lion King",
        "Pulp Fiction", "Jurassic Park", "Minions", "The Godfather",
        "Fight Club", "Barbie", "Elf", "Mermaid", "Toy Story", "Deadpool"
    ]

    # Fetch and save movies only if they don’t already exist in the database
    for movie_name in default_movies:
        if not Movie.objects.filter(name__iexact=movie_name).exists():
            movie_data = fetch_movie_from_omdb(movie_name)
            if movie_data:
                Movie.objects.create(
                    name=movie_data['name'],
                    description=movie_data['description'],
                    image=movie_data['image'],
                    price=movie_data['price']
                )

def index(request):
    # Load 20 default movies into the database if not already present
    load_default_movies()

    search_term = request.GET.get('search')

    if search_term:
        # Check if the movie is already in the database
        movies = Movie.objects.filter(name__icontains=search_term)

        if not movies.exists():
            # Fetch from OMDb and save if available
            movie_data = fetch_movie_from_omdb(search_term)
            if movie_data:
                movie = Movie.objects.create(
                    name=movie_data['name'],
                    description=movie_data['description'],
                    image=movie_data['image'],
                    price=movie_data['price']
                )
                movies = [movie]
    else:
        # Show the first 20 movies by default
        movies = Movie.objects.all()[:20]

    template_data = {
        'title': 'Movies',
        'movies': movies
    }
    return render(request, 'movies/index.html', {'template_data': template_data})

def show(request, id):
    movie = get_object_or_404(Movie, id=id)
    template_data = {
        'title': movie.name,
        'movie': movie
    }
    return render(request, 'movies/show.html', {'template_data': template_data})


