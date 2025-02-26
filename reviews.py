"""Module with functions related to user created reviews."""

import db

def add_review(movie_id, user_id, rating_id, review):
    """Lets a user create a review and stores the review and rating entered by the user, as well
    as the user's id and the id of the movie, in the database.

    Args:
        movie_id: unique identification number for the movie in the database.
        user_id: unique identification number for the user in the database.
        rating_id: unique identification number for the rating in the database.
        review: plain text entered by the user.
    Returns:
        None
    """

    sql = """INSERT INTO reviews (movie_id, user_id, rating_id, review)
    VALUES (?, ?, ?, ?)"""
    db.execute(sql, [movie_id, user_id, rating_id, review])

def get_reviews(movie_id):
    """Retrieves reviews made by users about a specific movie from the database.

    Args:
        movie_id: unique identification number for the movie in the database.
    Returns:
        list: a list of dictionaries, each containing the id of the review, integer value of the
        rating, id of the user, username of the user, and the review written by the user.
    """

    sql = """SELECT reviews.id, ratings.value, users.id user_id, users.username, reviews.review
            FROM reviews
            JOIN users ON reviews.user_id = users.id
            JOIN ratings ON reviews.rating_id = ratings.id
            WHERE reviews.movie_id = ?
            ORDER BY reviews.id DESC"""
    return db.query(sql, [movie_id])

def get_review(review_id):
    """Retrieves a specific review from the database.

    Args:
        review_id: unique identification number for the review in the database.
    Returns:
        dict or None: a dictionary containing details of the review if found, else None. The dict
        includes: id of the review, the review written by the user, timestamp when the review was
        created, value of the given rating, id of the associated movie, title of the associated
        movie, id of the associated user and username of the user.
    """

    sql = """SELECT reviews.id,
                    reviews.review,
                    reviews.created_at time,
                    ratings.value rating_value, 
                    movies.id movie_id,
                    movies.title movie_title,
                    users.id user_id,
                    users.username
            FROM reviews
            JOIN ratings ON reviews.rating_id = ratings.id
            JOIN movies ON reviews.movie_id = movies.id
            JOIN users ON reviews.user_id = users.id
            WHERE reviews.id = ?"""
    result = db.query(sql, [review_id])
    return result[0] if result else None

def get_rating(rating):
    """Retrieves the ID of the rating based on its numerical value.

    Args:
        rating: numerical value of the rating.
    Returns:
        list: a list of dicts containing the id of the rating.
    """

    sql = "SELECT id FROM ratings WHERE value = ?"
    return db.query(sql, [rating])

def update_review(review_id, review, rating_id):
    """Updates the review text and rating value of an existing review.

    Updating the data also updates the timestamp to current time.

    Args:
        review_id: unique identification number for the review in the database.
        review: plain text entered by the user.
        rating_id: unique identification number for the rating value in the database.
    Returns:
        None
    """

    sql = """UPDATE reviews
            SET review = ?, rating_id = ?, created_at = DATETIME('now', '+2 hours')
            WHERE id = ?"""
    db.execute(sql, [review, rating_id, review_id])

def remove_review(review_id):
    """Deletes a review from the database.

    Args:
        review_id: unique identification number for the review in the database.
    Returns:
        None
    """

    sql = "DELETE FROM reviews WHERE id = ?"
    db.execute(sql, [review_id])

def get_reviews_by_user(user_id):
    """Retrieves all reviews written by a specific user by executing a SQL query.

    Args:
        user_id: unique identification number for the user in the database.
    Returns:
        list: a list of dictionaries containing the user's reviews. Each dict includes id of the
        review, title of the reviewed movie, numerical value of given rating, and review written
        by the user.
    """

    sql = """SELECT reviews.id, movies.title movie_title, ratings.value rating, reviews.review
             FROM reviews
             JOIN movies ON reviews.movie_id = movies.id
             JOIN ratings ON reviews.rating_id = ratings.id
             WHERE reviews.user_id = ?
             ORDER BY reviews.id DESC"""
    return db.query(sql, [user_id])
