"""Module for varying functions relating to user data."""

from werkzeug.security import generate_password_hash, check_password_hash
import db
import error

def get_user(user_id):
    """Retrieves user from database via unique user id.
    Executes a SQL query to fetch the user's id number and username
    from the 'users' table in the app's database. If the user exists,
    the user's data is returned as a dictionaty. If no user is found,
    returns None.

    Args:
        user_id: unique identification number for the user in the database.
    Returns:
        dict or None: a dictionary containing the user's 'id' and 'username'
                        if the user is found, else None.
    """
    sql = """SELECT id, username, image IS NOT NULL has_image
            FROM users
            WHERE id = ?"""
    result = db.query(sql, [user_id])
    return result[0] if result else None

def get_reviews(user_id):
    """Retrieves reviews made by user via unique user id.
    Executes a SQL query to fetch ids of reviews the user has made and movies the user
    has reviewed from the 'reviews' table in the app's database. Returns reviews meeting
    the criteria.

    Args:
        user_id: unique identification number for the user in the database.
    Returns:
        list: a list of dictionaries, each containing review id and movie id.
    """
    sql = """SELECT id, movie_id FROM reviews WHERE user_id = ? ORDER BY id DESC"""
    return db.query(sql, [user_id])

def create_user(username, password1):
    """Creates new user account with a hashed password.

    Args:
        username: the username chosen by the user.
        password1: the password chosen by the user, which is hashed before being stored
        in the database.
    Returns:
        None
    """
    password_hash = generate_password_hash(password1)
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    db.execute(sql, [username, password_hash])

def update_image(user_id, image):
    """Updates the profile picture of a user
    
    Args:
        user_id: unique identification number for the user in the database.
        image: jpg file the user wishes to use as their profile picture.
    Returns:
        None
    """
    sql = "UPDATE users SET image = ? WHERE id = ?"
    db.execute(sql, [image, user_id])

def get_image(user_id):
    """Retrieves the profile picture the user has set.

    Retrieves the user's profile picture from the database and returns it. If no profile picture
    exists for the users, returns None.

    Args:
        user_id: unique identification number for the user in the database.
    Returns:
        image or None: profile picture of user if one exists, else None.
    """
    sql = "SELECT image FROM users WHERE id = ?"
    result = db.query(sql, [user_id])
    return result[0][0] if result else None

def check_login(username, password):
    """Checks if the provided username and password match an existing user.

    If the provided credentials match an user, returns the user's id, else returns an
    error page.

    Args:
        username: the username provided by the user.
        password: the password provided by the user.
    Returns:
        int or Response: id of user if credentials are valid, else an error page response.
    """
    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])
    if not result:
        return error.page("Virheellinen käyttäjätunnus/salasana", "Virhe kirjautumisessa")

    result = result[0]
    user_id = result["id"]
    password_hash = result["password_hash"]

    if check_password_hash(password_hash, password):
        return user_id
    return error.page("Virheellinen käyttäjätunnus/salasana", "Virhe kirjautumisessa")
