import db

def add_movie(title, director, year, description, user_id):
    sql = "INSERT INTO movies (title, director, year, description, user_id) VALUES (?, ?, ?, ?, ?)"
    db.execute(sql, [title, director, year, description, user_id])

def get_movies():
    sql = "SELECT id, title FROM movies ORDER BY id DESC"
    return db.query(sql)

def get_movie(movie_id):
    sql = """SELECT movies.title,
                    movies.director,
                    movies.year,
                    movies.description
            FROM movies, users
            WHERE movies.user_id = users.id AND
                movies.id = ?"""
    return db.query(sql, [movie_id])[0]