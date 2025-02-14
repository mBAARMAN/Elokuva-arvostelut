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
    sql = """SELECT ratings.value, users.id user_id, users.username, reviews.review
            FROM reviews
            JOIN users on reviews.user_id = users.id
            JOIN ratings ON reviews.rating_id = ratings.id
            WHERE reviews.movie_id = ?
            ORDER BY reviews.id DESC"""
    return db.query(sql, [movie_id])

def get_reviews_by_user(user_id):
    sql = """SELECT reviews.id, movies.title movie_title, ratings.value rating, reviews.review
             FROM reviews
             JOIN movies ON reviews.movie_id = movies.id
             JOIN ratings ON reviews.rating_id = ratings.id
             WHERE reviews.user_id = ?
             ORDER BY reviews.id DESC"""
    return db.query(sql, [user_id])