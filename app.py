import sqlite3
import re
from flask import Flask
from flask import abort, redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
import config
import db
import movies

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    if "user_id" not in session:
        abort(403)

def error(message, type):
    return render_template("error.html", message=message, type=type)

@app.route("/")
def index():
    all_movies = movies.get_movies()
    return render_template("index.html", movies=all_movies)

@app.route("/find_movie")
def find_movie():
    query = request.args.get("query")
    if query:
        results = movies.find_movies(query)
    else:
        query = ""
        results = []
    return render_template("find_movie.html",query=query, results=results)

@app.route("/movie/<int:movie_id>")
def show_movie(movie_id):
    movie = movies.get_movie(movie_id)
    if not movie:
        abort(404)
    return render_template("show_movie.html", movie=movie)

@app.route("/new_movie")
def new_movie():
    require_login()
    return render_template("new_movie.html")

@app.route("/create_movie", methods=["POST"])
def create_movie():
    require_login()

    title = request.form["title"]
    if not title or len(title) > 50:
        abort(403)
    director = request.form["director"]
    if not director or len(director) > 50:
        abort(403)
    year = request.form["year"]
    if not re.search("^[1-9][0-9]{0,3}$", year):
        abort(403)
    description = request.form["description"]
    if not description or len(description) > 1000:
        abort(403)
    genre = ",".join(request.form.getlist("genre"))
    if not genre:
        abort(403)

    user_id = session["user_id"]

    movies.add_movie(title, director, year, description, genre, user_id)

    return redirect("/")

@app.route("/edit_movie/<int:movie_id>")
def edit_movie(movie_id):
    require_login()
    movie = movies.get_movie(movie_id)
    if not movie:
        abort(404)
    if movie["user_id"] != session["user_id"]:
        abort(403)

    return render_template("edit_movie.html", movie=movie)

@app.route("/update_movie", methods=["POST"])
def update_movie():
    require_login()
    movie_id = request.form["movie_id"]
    movie = movies.get_movie(movie_id)
    if not movie:
        abort(404)
    if movie["user_id"] != session["user_id"]:
        abort(403)

    title = request.form["title"]
    if not title or len(title) > 50:
        abort(403)
    director = request.form["director"]
    if not director or len(director) > 50:
        abort(403)
    year = request.form["year"]
    if not re.search("^[1-9][0-9]{0,3}$", year):
        abort(403)
    description = request.form["description"]
    if not description or len(description) > 1000:
        abort(403)
    genre = ",".join(request.form.getlist("genre"))
    if not genre:
        abort(403)

    movies.update_movie(movie_id, title, director, year, description, genre)

    return redirect("/movie/" + str(movie_id))

@app.route("/remove_movie/<int:movie_id>", methods=["GET", "POST"])
def remove_movie(movie_id):
    require_login()
    movie = movies.get_movie(movie_id)
    if not movie:
        abort(404)
    if movie["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove_movie.html", movie=movie)

    if request.method == "POST":
        if "remove" in request.form:
            movies.remove_movie(movie_id)
            return redirect("/")
        else:
            return redirect("/movie/" + str(movie_id))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        password_hash = generate_password_hash(password1)

        if not username or not password1 or not password2:
            return error("Kaikki kentät tulee täyttää", "Virhe käyttäjän luomisessa")
        if password1 != password2:
            return error("Salasanat eivät täsmää", "Virhe käyttäjän luomisessa")
        if len(username) < 3:
            return error("Käyttäjänimen tulee olla vähintään 3 merkkiä pitkä", "Virhe käyttäjän luomisessa")
        if len(password1) < 5:
            return error("Salasanan tulee olla vähintään 5 merkkiä pitkä", "Virhe käyttäjän luomisessa")

        try:
            sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
            db.execute(sql, [username, password_hash])
        except sqlite3.IntegrityError:
            return error("Käyttäjänimi varattu", "Virhe käyttäjän luomisessa")
        return render_template("account_created.html")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """    if request.method == "GET":
            return render_template("login.html")"""

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if not username or not password:
            return error("Kaikki kentät tulee täyttää", "Virhe kirjautumisessa")

        sql = "SELECT id, password_hash FROM users WHERE username = ?"
        result = db.query(sql, [username])
        if not result:
            return error("Virheellinen käyttäjätunnus/salasana", "Virhe kirjautumisessa")

        result = result[0]
        user_id = result["id"]
        password_hash = result["password_hash"]

        if check_password_hash(password_hash, password):
            session["user_id"] = user_id
            session["username"] = username
            return redirect("/")
        return error("Virheellinen käyttäjätunnus/salasana", "Virhe kirjautumisessa")
    return render_template("login.html")

@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["username"]
        del session["user_id"]
    return redirect("/")
