import db

def add_movie(title, director, year, description, genre, user_id):
    sql = """INSERT INTO movies (title, director, year, description, genre, user_id) 
    VALUES (?, ?, ?, ?, ?, ?)"""
    db.execute(sql, [title, director, year, description, genre, user_id])

def get_movies():
    sql = "SELECT id, title FROM movies ORDER BY id DESC"
    return db.query(sql)

def get_movie(movie_id):
    sql = """SELECT movies.id,
                    movies.title,
                    movies.director,
                    movies.year,
                    movies.description,
                    movies.genre,
                    users.id user_id,
                    users.username
            FROM movies, users
            WHERE movies.user_id = users.id AND
                movies.id = ?"""
    result = db.query(sql, [movie_id])
    return result[0] if result else None

def update_movie(movie_id, title, director, year, description, genre):
    sql = """UPDATE movies SET title = ?,
                                director = ?,
                                year = ?,
                                description = ?,
                                genre = ?
                            WHERE id = ?"""
    db.execute(sql, [title, director, year, description, genre, movie_id])

def remove_movie(movie_id):
    sql = "DELETE FROM movies WHERE id = ?"
    db.execute(sql, [movie_id])

def find_movies(query):
    sql = """SELECT id, title
            FROM movies
            WHERE title LIKE ? OR description LIKE ? OR director LIKE ?
            ORDER BY id DESC"""
    like = "%" + query + "%"
    return db.query(sql, [like, like, like])