"""Module with functions related to movies."""


import db

def get_all_classes():
    """
    Retrieves all unique class titles and their associated values from the database.

    Returns:
        dict: A dictionary where each key is a class title, and the value is a list of associated
        values.
    """
    sql = "SELECT title, value FROM classes ORDER BY id"
    result = db.query(sql)

    classes = {}
    for title, value in result:
        classes[title] = []
    for title, value in result:
        classes[title].append(value)

    return classes

def add_movie(title, director, year, description, user_id, classes):
    """
    Adds a new movie to the database along with its associated classes.

    Args:
        title: The title of the movie.
        director: The director of the movie.
        year: The release year of the movie.
        description: A short description of the movie.
        user_id: The ID of the user who added the movie.
        classes: A list of (title, value) pairs representing movie classifications.

    Returns:
        None
    """
    sql = """INSERT INTO movies (title, director, year, description, user_id)
    VALUES (?, ?, ?, ?, ?)"""
    db.execute(sql, [title, director, year, description, user_id])

    movie_id = db.last_insert_id()

    sql = "INSERT INTO movie_classes (movie_id, title, value) VALUES (?, ?, ?)"
    for title, value in classes:
        db.execute(sql, [movie_id, title, value])

def get_classes(movie_id):
    """
    Retrieves all classes associated with a given movie.

    Args:
        movie_id: The ID of the movie.

    Returns:
        list of tuples: A list of (title, value) pairs representing the movie's classifications.
    """
    sql = "SELECT title, value FROM movie_classes WHERE movie_id = ?"
    return db.query(sql, [movie_id])

def get_movies():
    """
    Retrieves all movies from the database, sorted by most recent.

    Returns:
        list of tuples: A list of (id, title) pairs representing movies.
    """
    sql = "SELECT id, title, director, year FROM movies ORDER BY id DESC"
    return db.query(sql)

def get_movie(movie_id):
    """
    Retrieves detailed information about a specific movie, including user details.

    Args:
        movie_id: The ID of the movie.

    Returns:
        tuple or None: A tuple containing movie details (id, title, director, year, description,
        user_id, username),
                       or None if no movie is found.
    """
    sql = """SELECT movies.id,
                    movies.title,
                    movies.director,
                    movies.year,
                    movies.description,
                    users.id user_id,
                    users.username
            FROM movies, users
            WHERE movies.user_id = users.id AND
                movies.id = ?"""
    result = db.query(sql, [movie_id])
    return result[0] if result else None

def update_movie(movie_id, title, director, year, description, classes):
    """
    Updates an existing movie's details and its associated classes.

    Args:
        movie_id: The ID of the movie to update.
        title: The new title of the movie.
        director: The new director of the movie.
        year: The new release year of the movie.
        description: The new description of the movie.
        classes: A list of (title, value) pairs representing updated classifications.

    Returns:
        None
    """
    sql = """UPDATE movies SET title = ?,
                                director = ?,
                                year = ?,
                                description = ?
                            WHERE id = ?"""
    db.execute(sql, [title, director, year, description, movie_id])

    sql = "DELETE FROM movie_classes WHERE movie_id = ?"
    db.execute(sql, [movie_id])

    sql = "INSERT INTO movie_classes (movie_id, title, value) VALUES (?, ?, ?)"
    for title, value in classes:
        db.execute(sql, [movie_id, title, value])

def remove_movie(movie_id):
    """
    Deletes a movie from the database.

    Args:
        movie_id: The ID of the movie to remove.

    Returns:
        None
    """
    sql = "DELETE FROM movies WHERE id = ?"
    db.execute(sql, [movie_id])

def find_movies(query):
    """
    Searches for movies in the database by title, description, or director.

    Args:
        query: The search query.

    Returns:
        list of tuples: A list of (id, title) pairs for matching movies.
    """
    sql = """SELECT id, title
            FROM movies
            WHERE title LIKE ? OR description LIKE ? OR director LIKE ?
            ORDER BY id DESC"""
    like = "%" + query + "%"
    return db.query(sql, [like, like, like])
