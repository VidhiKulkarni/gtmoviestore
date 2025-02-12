from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review
from django.contrib.auth.decorators import login_required
from .utils import fetch_movies_list, fetch_movie_from_omdb, fetch_movie_details
from django.shortcuts import render, get_object_or_404
from .models import Movie, Review
from .utils import fetch_movie_from_omdb

def load_default_movies():
    """Loads 20 default movies into the database if they don’t exist."""
    default_movies = [
        "Inception", "Interstellar", "The Dark Knight", "Titanic", "Avatar",
        "The Avengers", "Forrest Gump", "The Matrix", "Gladiator", "The Lion King",
        "Pulp Fiction", "Jurassic Park", "Minions", "The Godfather",
        "Fight Club", "Barbie", "Elf", "The Little Mermaid", "Toy Story", "Deadpool"
    ]

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
    """Loads the homepage with preloaded movies or search results and stores new movies."""
    load_default_movies()

    search_term = request.GET.get('search')

    if search_term:
        # Check if the movie exists in the database
        movies = Movie.objects.filter(name__icontains=search_term)

        if not movies.exists():
            # Fetch from OMDb if not in the database
            movie_data = fetch_movie_from_omdb(search_term)

            if movie_data:
                # Check again by name to ensure it's not added twice
                movie, created = Movie.objects.get_or_create(
                    name=movie_data['name'],
                    defaults={
                        "description": movie_data['description'],
                        "image": movie_data['image'],
                        "price": movie_data['price']
                    }
                )
                movies = [movie]
    else:
        # Show the first 20 movies from the database
        movies = Movie.objects.all()[:20]

    template_data = {
        'title': 'Movies',
        'movies': movies
    }
    return render(request, 'movies/index.html', {'template_data': template_data})


def show(request, id):
    """Displays movie details and saves the movie if fetched from OMDb."""
    try:
        movie = Movie.objects.get(id=id)
    except Movie.DoesNotExist:
        # Fetch movie details from OMDb and store in database if not found
        movie_data = fetch_movie_from_omdb(id)
        if movie_data:
            movie = Movie.objects.create(
                name=movie_data['name'],
                description=movie_data['description'],
                image=movie_data['image'],
                price=movie_data['price']
            )
        else:
            return render(request, "movies/show.html", {"error": "Movie not found"})

    reviews = Review.objects.filter(movie=movie)  # Fetch related reviews

    template_data = {
        'title': movie.name,
        'movie': movie,
        'reviews': reviews
    }
    return render(request, 'movies/show.html', {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html',{'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)