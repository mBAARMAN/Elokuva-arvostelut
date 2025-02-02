import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
import config
import db
import movies

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    all_movies = movies.get_movies()
    return render_template("index.html", movies=all_movies)

@app.route("/movie/<int:movie_id>")
def show_movie(movie_id):
    movie = movies.get_movie(movie_id)
    return render_template("show_movie.html", movie=movie)

@app.route("/new_movie")
def new_movie():
    return render_template("new_movie.html")

@app.route("/create_movie", methods=["POST"])
def create_movie():
    title = request.form["title"]
    director = request.form["director"]
    year = request.form["year"]
    description = request.form["description"]
    user_id = session["user_id"]

    movies.add_movie(title, director, year, description, user_id)

    return redirect("/")

@app.route("/edit_movie/<int:movie_id>")
def edit_movie(movie_id):
    movie = movies.get_movie(movie_id)
    return render_template("edit_movie.html", movie=movie)

@app.route("/update_movie", methods=["POST"])
def update_movie():
    movie_id = request.form["movie_id"]
    title = request.form["title"]
    director = request.form["director"]
    year = request.form["year"]
    description = request.form["description"]

    movies.update_movie(movie_id, title, director, year, description)

    return redirect("/movie/" + str(movie_id))

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"

    return "Tunnus luotu"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        sql = "SELECT id, password_hash FROM users WHERE username = ?"
        result = db.query(sql, [username])[0]
        user_id = result["id"]
        password_hash = result["password_hash"]

        if check_password_hash(password_hash, password):
            session["user_id"] = user_id
            session["username"] = username
            return redirect("/")
        else:
            return "VIRHE: väärä tunnus tai salasana"

@app.route("/logout")
def logout():
    del session["username"]
    del session["user_id"]
    return redirect("/")
