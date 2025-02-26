"""Module with functions related to user created comments."""

import db

def add_comment(review_id, user_id, comment):
    """
    Adds a new comment to a specific review.

    Args:
        review_id: The ID of the review to which the comment is associated.
        user_id: The ID of the user who is adding the comment.
        comment: The content of the comment.

    Returns:
        None
    """
    sql = """INSERT INTO comments (review_id, user_id, comment)
    VALUES (?, ?, ?)"""
    db.execute(sql, [review_id, user_id, comment])

def get_comments(review_id):
    """
    Retrieves all comments for a specific review.

    Args:
        review_id: The ID of the review for which comments are to be retrieved.

    Returns:
        list of tuples: A list of tuples containing comment details. Each tuple contains:
            - comment ID
            - user ID
            - username
            - comment text
            - comment creation time
    """
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
    """
    Retrieves detailed information about a specific comment.

    Args:
        comment_id: The ID of the comment to retrieve.

    Returns:
        tuple or None: A tuple containing the comment's details (comment ID, comment text,
        creation time, review ID, user ID, and username), or None if the comment is not found.
    """
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
    """
    Updates the content of an existing comment.

    Args:
        comment_id: The ID of the comment to be updated.
        comment: The new content of the comment.

    Returns:
        None
    """
    sql = """UPDATE comments
            SET comment = ?, created_at = DATETIME('now', '+2 hours')
            WHERE id = ?"""
    db.execute(sql, [comment,comment_id])

def remove_comment(comment_id):
    """
    Deletes a comment from the database.

    Args:
        comment_id: The ID of the comment to be deleted.

    Returns:
        None
    """
    sql = "DELETE FROM comments WHERE id = ?"
    db.execute(sql, [comment_id])
