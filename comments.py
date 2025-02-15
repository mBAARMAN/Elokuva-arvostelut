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
