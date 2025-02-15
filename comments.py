import db

def add_comment(review_id, user_id, comment):
    sql = """INSERT INTO comments (review_id, user_id, comment) 
    VALUES (?, ?, ?)"""
    db.execute(sql, [review_id, user_id, comment])

def get_comments(review_id):
    sql = """SELECT comments.id,
                    users.id user_id,
                    users.username,
                    comments.comment,
                    comments.created_at time
            FROM comments
            JOIN users ON comments.user_id = users.id
            WHERE comments.review_id = ?
            ORDER BY comments.id DESC"""
    return db.query(sql, [review_id])

def get_comment(comment_id):
    sql = """SELECT comments.id,
                    comments.comment,
                    comments.created_at time,
                    reviews.id review_id,
                    users.id user_id,
                    users.username
            FROM comments
            JOIN reviews ON comments.review_id = reviews.id
            JOIN users ON comments.user_id = users.id
            WHERE comments.id = ?"""
    result = db.query(sql, [comment_id])
    return result[0] if result else None

def update_comment(comment_id, comment):
    sql = """UPDATE comments
            SET comment = ?, created_at = DATETIME('now', '+2 hours')
            WHERE id = ?"""
    db.execute(sql, [comment,comment_id])

def remove_comment(comment_id):
    sql = "DELETE FROM comments WHERE id = ?"
    db.execute(sql, [comment_id])