import db

def add_movie(title, director, year, description, user_id):
    sql = "INSERT INTO movies (title, director, year, description, user_id) VALUES (?, ?, ?, ?, ?)"
    db.execute(sql, [title, director, year, description, user_id])

def get_movies():
    sql = "SELECT id, title FROM movies ORDER BY id DESC"
    return db.query(sql)

def get_movie(movie_id):
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
    return db.query(sql, [movie_id])[0]

def update_movie(movie_id, title, director, year, description):
    sql = """UPDATE movies SET title = ?,
                                director = ?,
                                year = ?,
                                description = ?
                            WHERE id = ?"""
    db.execute(sql, [title, director, year, description, movie_id])