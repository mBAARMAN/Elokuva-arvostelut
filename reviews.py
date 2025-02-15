import db

def get_all_ratings():
    sql = "SELECT title, value FROM rating ORDER BY id"
    result = db.query(sql)

    ratings = {}
    for title, value in result:
        ratings[title] = []
    for title, value in result:
        ratings[title].append(value)

    return ratings

def add_review(movie_id, user_id, rating_id, review):
    sql = """INSERT INTO reviews (movie_id, user_id, rating_id, review) 
    VALUES (?, ?, ?, ?)"""
    db.execute(sql, [movie_id, user_id, rating_id, review])

def get_reviews(movie_id):
    sql = """SELECT reviews.id, ratings.value, users.id user_id, users.username, reviews.review
            FROM reviews
            JOIN users ON reviews.user_id = users.id
            JOIN ratings ON reviews.rating_id = ratings.id
            WHERE reviews.movie_id = ?
            ORDER BY reviews.id DESC"""
    return db.query(sql, [movie_id])

def get_review(review_id):
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

def update_review(review_id, review, rating_id):
    sql = """UPDATE reviews
            SET review = ?, rating_id = ?, created_at = DATETIME('now', '+2 hours')
            WHERE id = ?"""
    db.execute(sql, [review, rating_id, review_id])

def remove_review(review_id):
    sql = "DELETE FROM reviews WHERE id = ?"
    db.execute(sql, [review_id])

def get_reviews_by_user(user_id):
    sql = """SELECT reviews.id, movies.title movie_title, ratings.value rating, reviews.review
             FROM reviews
             JOIN movies ON reviews.movie_id = movies.id
             JOIN ratings ON reviews.rating_id = ratings.id
             WHERE reviews.user_id = ?
             ORDER BY reviews.id DESC"""
    return db.query(sql, [user_id])