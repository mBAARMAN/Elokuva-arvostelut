import sqlite3
import re
from flask import Flask
from flask import abort, redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
import config
import db
import movies
import users
import reviews
import error

app = Flask(__name__)
app.secret_key = config.secret_key

# Login tarkistus
def require_login():
    if "user_id" not in session:
        abort(403)

# Etusivu
@app.route("/")
def index():
    all_movies = movies.get_movies()
    return render_template("index.html", movies=all_movies)

# Käyttäjäsivut
@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        return error.page("Käyttäjää ei löytynyt", "Virhe sivun hakemisessa")
    reviews_list = reviews.get_reviews_by_user(user_id)
    return render_template("show_user.html", user=user, reviews=reviews_list)

# Haku
@app.route("/find_movie")
def find_movie():
    query = request.args.get("query")
    if query:
        results = movies.find_movies(query)
    else:
        query = ""
        results = []
    return render_template("find_movie.html",query=query, results=results)

# Elokuvasivut
@app.route("/movie/<int:movie_id>")
def show_movie(movie_id):
    movie = movies.get_movie(movie_id)
    if not movie:
        return error.page("Elokuvaa ei löytynyt", "Virhe sivun hakemisessa")
    reviews_list = reviews.get_reviews(movie_id)
    return render_template("show_movie.html", movie=movie, reviews=reviews_list)

# Uuden elokuvan lomake
@app.route("/new_movie")
def new_movie():
    require_login()
    return render_template("new_movie.html")

# Uuden elokuvan lisääminen
@app.route("/create_movie", methods=["GET", "POST"])
def create_movie():
    require_login()

    title = request.form["title"]
    if not title or len(title) > 50 or not title.strip():
        return error.page("Virheellinen elokuvan nimi", "Virhe elokuvan lisäämisessä")

    director = request.form["director"]
    if not director or len(director) > 50 or not director.strip():
        return error.page("Virheellinen ohjaajan nimi", "Virhe elokuvan lisäämisessä")

    year = request.form["year"]
    if not re.search(r"^(19[0-9]{2}|20[0-9]{2})$", year):
        return error.page("Virheellinen julkaisuvuosi", "Virhe elokuvan lisäämisessä")

    description = request.form["description"]
    if not description or len(description) > 1000 or not description.strip():
        return error.page("Virheellinen kuvaus", "Virhe elokuvan lisäämisessä")

    allowed_genres = {"draama", "komedia", "dokumentti", "musikaali", "toiminta", 
                      "seikkailu", "rakkaus", "kauhu", "scifi", "western"}

    genre = request.form.getlist("genre")
    if not genre or not set(genre).issubset(allowed_genres):
        return error.page("Virhe genren valinnassa", "Virhe elokuvan lisäämisessä")
    genre = ",".join(genre)

    user_id = session.get("user_id")
    if not user_id:
        return error.page("Käyttäjä ei ole kirjautunut", "Virhe elokuvan lisäämisessä")

    movies.add_movie(title, director, year, description, genre, user_id)

    return redirect("/")

# Elokuvan arvostelu
@app.route("/create_review", methods=["POST"])
def create_review():
    require_login()

    rating = int(request.form["rating"])
    review = request.form["review"]
    movie_id = request.form["movie_id"]

    if not movie_id:
        return error.page("Elokuvaa ei löytynyt", "Virhe arvostelun lisäämisessä")

    movie = movies.get_movie(movie_id)
    if not movie:
        return error.page("Elokuvaa ei löytynyt", "Virhe arvostelun lisäämisessä")

    user_id = session.get("user_id")
    if not user_id:
        return error.page("Käyttäjä ei ole kirjautunut", "Virhe arvostelun lisäämisessä")

    rating_id = db.query("SELECT id FROM ratings WHERE value = ?", [rating])
    if not rating_id:
        return error.page("Virheellinen arvosana", "Virhe arvostelun lisäämisessä")

    rating_id = rating_id[0]["id"]
    reviews.add_review(movie_id, user_id, rating_id, review)

    return redirect("/movie/" + str(movie_id))

# Arvostelut
@app.route("/review/<int:review_id>")
def show_review(review_id):
    review = reviews.get_review(review_id)
    if not review:
        return error.page("Arvostelua ei löytynyt", "Virhe sivun hakemisessa")
    return render_template("show_review.html", review=review)

# Elokuvan tietojen muokkaus
@app.route("/edit_movie/<int:movie_id>", methods=["GET", "POST"])
def edit_movie(movie_id):
    require_login()
    movie = movies.get_movie(movie_id)

    if not movie:
        return error.page("Elokuvaa ei löytynyt", "Virhe muokatessa elokuvan tietoja")

    if movie["user_id"] != session["user_id"]:
        return error.page("Käyttäjällä ei ole oikeuksia muokata elokuvan tietoja", 
                     "Virhe muokatessa elokuvan tietoja")

    if not session.get("username"):
        return redirect("/login")

    if request.method == "POST":
        if "confirm" in request.form:

            title = request.form["title"].strip()
            if not title or len(title) > 50:
                return error.page("Virheellinen elokuvan nimi", "Virhe muokatessa elokuvan tietoja")

            director = request.form["director"].strip()
            if not director or len(director) > 50:
                return error.page("Virheellinen ohjaajan nimi", "Virhe muokatessa elokuvan tietoja")

            year = request.form["year"]
            if not re.search(r"^(19[0-9]{2}|20[0-9]{2})$", year):
                return error.page("Virheellinen julkaisuvuosi", "Virhe muokatessa elokuvan tietoja")

            description = request.form["description"].strip()
            if not description or len(description) > 1000:
                return error.page("Virheellinen kuvaus", "Virhe muokatessa elokuvan tietoja")

            allowed_genres = {"draama", "komedia", "dokumentti", "musikaali", "toiminta", 
                      "seikkailu", "rakkaus", "kauhu", "scifi", "western"}

            genre = request.form.getlist("genre")
            if not genre or not set(genre).issubset(allowed_genres):
                return error.page("Virhe genren valinnassa", "Virhe muokatessa elokuvan tietoja")
            genre = ",".join(genre)

            user_id = session.get("user_id")
            if not user_id:
                return error.page("Käyttäjä ei ole kirjautunut", "Virhe muokatessa elokuvan tietoja")

            movies.update_movie(title, director, year, description, genre, user_id)
            return redirect("/movie/" + str(movie_id))
        return redirect("/movie/" + str(movie_id))
    return render_template("edit_movie.html", movie=movie)

# Tietojen päivitys
@app.route("/update_movie", methods=["POST"])
def update_movie():
    require_login()
    movie_id = request.form["movie_id"]
    movie = movies.get_movie(movie_id)

    if not movie:
        return error.page("Elokuvaa ei löytynyt", "Virhe muokatessa elokuvan tietoja")

    if movie["user_id"] != session["user_id"]:
        return error.page("Käyttäjällä ei ole oikeuksia muokata elokuvan tietoja", "Virhe muokatessa elokuvan tietoja")

    if not session.get("username"):
        return redirect("/login")

    title = request.form["title"].strip()
    if not title or len(title) > 50:
        return error.page("Virheellinen elokuvan nimi", "Virhe muokatessa elokuvan tietoja")

    director = request.form["director"].strip()
    if not director or len(director) > 50:
        return error.page("Virheellinen ohjaajan nimi", "Virhe muokatessa elokuvan tietoja")

    year = request.form["year"]
    if not re.search(r"^(19[0-9]{2}|20[0-9]{2})$", year):
        return error.page("Virheellinen julkaisuvuosi", "Virhe muokatessa elokuvan tietoja")

    description = request.form["description"].strip()
    if not description or len(description) > 1000:
        return error.page("Virheellinen kuvaus", "Virhe muokatessa elokuvan tietoja")

    allowed_genres = {"draama", "komedia", "dokumentti", "musikaali", "toiminta", 
              "seikkailu", "rakkaus", "kauhu", "scifi", "western"}

    genre = request.form.getlist("genre")
    if not genre or not set(genre).issubset(allowed_genres):
        return error.page("Virhe genren valinnassa", "Virhe muokatessa elokuvan tietoja")
    genre = ",".join(genre)

    movies.update_movie(movie_id, title, director, year, description, genre)

    return redirect("/movie/" + str(movie_id))

# Elokuvan poisto
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

# Rekisteröinti
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]

        if not username or not password1 or not password2:
            return error.page("Kaikki kentät tulee täyttää", "Virhe käyttäjän luomisessa")
        if password1 != password2:
            return error.page("Salasanat eivät täsmää", "Virhe käyttäjän luomisessa")
        if len(username) < 3:
            return error.page("Käyttäjänimen tulee olla vähintään 3 merkkiä pitkä", 
                         "Virhe käyttäjän luomisessa")
        if len(password1) < 5:
            return error.page("Salasanan tulee olla vähintään 5 merkkiä pitkä", "Virhe käyttäjän luomisessa")

        try:
            users.create_user(username, password1)
        except sqlite3.IntegrityError:
            return error.page("Käyttäjänimi varattu", "Virhe käyttäjän luomisessa")
        return render_template("account_created.html")

    return render_template("register.html")

# Kirjaudu sisään
@app.route("/login", methods=["GET", "POST"])
def login():
    """    if request.method == "GET":
            return render_template("login.html")"""

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if not username or not password:
            return error.page("Kaikki kentät tulee täyttää", "Virhe kirjautumisessa")

        user_id = users.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            session["username"] = username
            return redirect("/")
        return error.page("Virheellinen käyttäjätunnus/salasana", "Virhe kirjautumisessa")
    return render_template("login.html")

# Kirjaudu ulos
@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["username"]
        del session["user_id"]
    return redirect("/")
