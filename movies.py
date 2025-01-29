import db

def add_movie(title, director, year, description, user_id):
    sql = "INSERT INTO movies (title, director, year, description, user_id) VALUES (?, ?, ?, ?, ?)"
    db.execute(sql, [title, director, year, description, user_id])