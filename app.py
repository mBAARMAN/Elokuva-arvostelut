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
import comments
import error

app = Flask(__name__)
app.secret_key = config.secret_key

# Check login
def require_login():
    if "user_id" not in session:
        abort(403)

# Front page
@app.route("/")
def index():
    all_movies = movies.get_movies()
    return render_template("index.html", movies=all_movies)

# User pages
@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        return error.page("Käyttäjää ei löytynyt", "Virhe sivun hakemisessa")
    reviews_list = reviews.get_reviews_by_user(user_id)
    return render_template("show_user.html", user=user, reviews=reviews_list)

# Search for a movie
@app.route("/find_movie")
def find_movie():
    query = request.args.get("query")
    if query:
        results = movies.find_movies(query)
    else:
        query = ""
        results = []
    return render_template("find_movie.html",query=query, results=results)

# Render a movie page
@app.route("/movie/<int:movie_id>")
def show_movie(movie_id):
    movie = movies.get_movie(movie_id)
    if not movie:
        return error.page("Elokuvaa ei löytynyt", "Virhe sivun hakemisessa")
    reviews_list = reviews.get_reviews(movie_id)
    classes = movies.get_classes(movie_id)
    return render_template("show_movie.html", movie=movie, reviews=reviews_list, classes=classes)

# Render a review page
@app.route("/review/<int:review_id>")
def show_review(review_id):
    review = reviews.get_review(review_id)
    if not review:
        return error.page("Arvostelua ei löytynyt", "Virhe kommentin näytössä")
    comments_list = comments.get_comments(review_id)
    return render_template("show_review.html", review=review, comments=comments_list)

# Render a comment page
@app.route("/comment/<int:comment_id>")
def show_comment(comment_id):
    comment = comments.get_comment(comment_id)
    if not comment:
        return error.page("Kommenttia ei löytynyt", "Virhe kommentin näytössä")

    review = reviews.get_review(comment["review_id"])
    if not review:
        return error.page("Arvostelua ei löytynyt", "Virhe kommentin näytössä")
    return render_template("show_comment.html", comment=comment, review=review)

# Render new movie form
@app.route("/new_movie")
def new_movie():
    require_login()
    classes = movies.get_all_classes()
    return render_template("new_movie.html", classes=classes)

# Create movie
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

    user_id = session.get("user_id")
    if not user_id:
        return error.page("Käyttäjä ei ole kirjautunut", "Virhe elokuvan lisäämisessä")

    all_classes = movies.get_all_classes()

    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
            class_title, class_value = entry.split(":")
            if class_title not in all_classes:
                return error.page("Virheellinen luokitus", "Virhe elokuvan lisäämisessä")
            if class_value not in all_classes[class_title]:
                return error.page("Virheellinen luokitus", "Virhe elokuvan lisäämisessä")
            classes.append((class_title, class_value))

    movies.add_movie(title, director, year, description, user_id, classes)

    return redirect("/")

# Create review on movie
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

# Create comment on review
@app.route("/create_comment", methods=["POST"])
def create_comment():
    require_login()

    comment = request.form["comment"]
    review_id = request.form["review_id"]

    if not review_id:
        return error.page("Arvostelua ei löytynyt", "Virhe kommentin lisäämisessä")

    review = reviews.get_review(review_id)
    if not review:
        return error.page("Arvostelua ei löytynyt", "Virhe kommentin lisäämisessä")

    user_id = session.get("user_id")
    if not user_id:
        return error.page("Käyttäjä ei ole kirjautunut", "Virhe kommentin lisäämisessä")

    comments.add_comment(review_id, user_id, comment)
    return redirect("/review/" + str(review_id))

# Edit movie data
@app.route("/edit_movie/<int:movie_id>")
def edit_movie(movie_id):
    require_login()
    movie = movies.get_movie(movie_id)

    if not movie:
        return error.page("Elokuvaa ei löytynyt", "Virhe muokatessa elokuvan tietoja")

    if movie["user_id"] != session["user_id"]:
        return error.page("Käyttäjällä ei ole oikeuksia muokata elokuvan tietoja", 
                     "Virhe muokatessa elokuvan tietoja")

    all_classes = movies.get_all_classes()
    classes = {}
    for my_class in all_classes:
        classes[my_class] = ""
    for entry in movies.get_classes(movie_id):
        classes[entry["title"]] = entry["value"]

    return render_template("edit_movie.html", movie=movie, classes=classes, 
                           all_classes=all_classes)

# Update data
@app.route("/update_movie", methods=["POST"])
def update_movie():
    require_login()
    movie_id = request.form["movie_id"]
    movie = movies.get_movie(movie_id)

    if not movie:
        return error.page("Elokuvaa ei löytynyt", "Virhe muokatessa elokuvan tietoja")

    if movie["user_id"] != session["user_id"]:
        return error.page("Käyttäjällä ei ole oikeuksia muokata elokuvan tietoja", "Virhe muokatessa elokuvan tietoja")

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

    all_classes = movies.get_all_classes()

    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
            class_title, class_value = entry.split(":")
            if class_title not in all_classes:
                return error.page("Virheellinen luokitus", "Virhe elokuvan lisäämisessä")
            if class_value not in all_classes[class_title]:
                return error.page("Virheellinen luokitus", "Virhe elokuvan lisäämisessä")
            classes.append((class_title, class_value))

        movies.update_movie(movie_id, title, director, year, description, classes)

        return redirect("/movie/" + str(movie_id))
    return redirect("/movie/" + str(movie_id))

# Edit review data
@app.route("/edit_review/<int:review_id>", methods=["GET", "POST"])
def edit_review(review_id):
    require_login()
    review = reviews.get_review(review_id)

    if not review:
        return error.page("Arvostelua ei löytynyt", "Virhe muokatessa arvostelua")

    if review["user_id"] != session["user_id"]:
        return error.page("Käyttäjällä ei ole oikeuksia muokata arvostelua", 
                     "Virhe muokatessa arvostelua")

    if request.method == "POST":
        if "confirm" in request.form:

            rating = int(request.form["rating"])
            review = request.form["review"].strip()
            if not review or len(review) > 1000:
                return error.page("Virheellinen arvostelu", "Virhe muokatessa arvostelua")

            movie_id = request.form["movie_id"]
            if not movie_id:
                return error.page("Elokuvaa ei löytynyt", "Virhe muokatessa arvostelua")
            movie = movies.get_movie(movie_id)
            if not movie:
                return error.page("Elokuvaa ei löytynyt", "Virhe muokatessa arvostelua")

            user_id = session.get("user_id")
            if not user_id:
                return error.page("Käyttäjä ei ole kirjautunut", "Virhe muokatessa arvostelua")

            rating_id = db.query("SELECT id FROM ratings WHERE value = ?", [rating])
            if not rating_id:
                return error.page("Virheellinen arvosana", "Virhe muokatessa arvostelua")
            rating_id = rating_id[0]["id"]

            reviews.update_review(review_id, review, rating_id)
            return redirect("/review/" + str(review_id))
        return redirect("/review/" + str(review_id))
    return render_template("edit_review.html", review=review, movie_id=review["movie_id"])

# Edit comment data
@app.route("/edit_comment/<int:comment_id>", methods=["GET", "POST"])
def edit_comment(comment_id):
    require_login()

    comment = comments.get_comment(comment_id)
    if not comment:
        return error.page("Kommenttia ei löytynyt", "Virhe muokatessa kommenttia")

    if comment["user_id"] != session["user_id"]:
        return error.page("Käyttäjällä ei ole oikeuksia muokata kommenttia", 
                     "Virhe muokatessa kommenttia")

    if request.method == "POST":
        if "confirm" in request.form:

            comment = request.form["comment"].strip()
            if not comment or len(comment) > 1000:
                return error.page("Virheellinen kommentti", "Virhe muokatessa kommenttia")

            review_id = request.form["review_id"]
            if not review_id:
                return error.page("Arvostelua ei löytynyt", "Virhe muokatessa kommenttia")
            review = reviews.get_review(review_id)
            if not review:
                return error.page("Arvostelua ei löytynyt", "Virhe muokatessa kommenttia")

            user_id = session.get("user_id")
            if not user_id:
                return error.page("Käyttäjä ei ole kirjautunut", "Virhe muokatessa kommenttia")

            comments.update_comment(comment_id, comment)
            return redirect("/comment/" + str(comment_id))
        return redirect("/comment/" + str(comment_id))
    return render_template("edit_comment.html", comment=comment, review_id=comment["review_id"])

# Remove movie
@app.route("/remove_movie/<int:movie_id>", methods=["GET", "POST"])
def remove_movie(movie_id):
    require_login()
    movie = movies.get_movie(movie_id)
    if not movie:
        return error.page("Elokuvaa ei löytynyt", "Virhe elokuvan poistossa")
    if movie["user_id"] != session["user_id"]:
        return error.page("Käyttäjällä ei oikeuksia poistaa elokuvaa", "Virhe elokuvan poistossa")

    if request.method == "GET":
        return render_template("remove_movie.html", movie=movie)

    if request.method == "POST":
        if "remove" in request.form:
            movies.remove_movie(movie_id)
            return redirect("/")
        else:
            return redirect("/movie/" + str(movie_id))

# Remove review
@app.route("/remove_review/<int:review_id>", methods=["GET", "POST"])
def remove_review(review_id):
    require_login()
    review = reviews.get_review(review_id)

    if not review:
        return error.page("Arvostelua ei löytynyt", "Virhe arvostelun poistossa")
    if review["user_id"] != session["user_id"]:
        return error.page("Käyttäjällä ei oikeuksia poistaa arvostelua", "Virhe arvostelun poistossa")

    if request.method == "GET":
        return render_template("remove_review.html", review=review)

    if request.method == "POST":
        if "remove" in request.form:
            reviews.remove_review(review_id)
            return redirect("/movie/" + str(review["movie_id"]))
        else:
            return redirect("/review/" + str(review_id))

# Remove comment
@app.route("/remove_comment/<int:comment_id>", methods=["GET", "POST"])
def remove_comment(comment_id):
    require_login()
    comment = comments.get_comment(comment_id)

    if not comment:
        return error.page("Kommenttia ei löytynyt", "Virhe kommentin poistossa")
    if comment["user_id"] != session["user_id"]:
        return error.page("Käyttäjällä ei oikeuksia poistaa kommenttia", "Virhe kommentin poistossa")

    if request.method == "GET":
        return render_template("remove_comment.html", comment=comment)

    if request.method == "POST":
        if "remove" in request.form:
            comments.remove_comment(comment_id)
            return redirect("/review/" + str(comment["review_id"]))
        else:
            return redirect("/comment/" + str(comment_id))

# Register form
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

# Login
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

# Logout
@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["username"]
        del session["user_id"]
    return redirect("/")
