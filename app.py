"""Main program"""

import sqlite3
import re
import secrets
from flask import Flask
from flask import redirect, render_template, request, session, make_response
import config
import movies
import users
import reviews
import comments
import error

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

def require_login():
    """
    Ensures that the user is logged in. If not, renders an error page.

    Returns:
        None
    """
    if "user_id" not in session:
        return error.page("Kirjautuminen vaaditaan", "Virhe kirjautumisessa")

def check_csrf():
    """
    """
    if "csrf_token" not in request.form:
        return error.page('Istuntoa ei voitu vahvistaa', 'Virhe istunnon tietojen hakemisessa')
    if request.form["csrf_token"] != session["csrf_token"]:
        return error.page('Istuntoa ei voitu vahvistaa', 'Virhe istunnon tietojen hakemisessa')

@app.route("/")
def index():
    """
    Renders the front page displaying all available movies.

    Returns:
        rendered template: The rendered HTML template for the index page with a list of all movies
    """
    all_movies = movies.get_movies()
    return render_template("index.html", movies=all_movies)

@app.route("/user/<int:user_id>")
def show_user(user_id):
    """
    Renders a user's profile page showing their reviews.

    Args:
        user_id (int): The ID of the user to display.

    Returns:
        rendered template or error: The rendered template with user data and reviews, or an error
        page if user not found.
    """
    user = users.get_user(user_id)
    if not user:
        return error.page("Käyttäjää ei löytynyt", "Virhe sivun hakemisessa")
    reviews_list = reviews.get_reviews_by_user(user_id)
    return render_template("show_user.html", user=user, reviews=reviews_list)

@app.route("/add_image", methods=["GET", "POST"])
def add_image():
    """
    """
    require_login()

    if request.method == "GET":
        return render_template("add_image.html")

    if request.method == "POST":
        check_csrf()
        user_id = session["user_id"]
        if not user_id:
            return error.page("Käyttäjää ei löytynyt", "Virhe profiilin muokkaamisessa")

        if "confirm" in request.form:
            file = request.files["image"]
            if not file.filename.endswith(".jpg"):
                return "VIRHE: väärä tiedostomuoto"

            image = file.read()
            if len(image) > 100 * 1024:
                return "VIRHE: liian suuri kuva"

            users.update_image(user_id, image)
        return redirect("/user/" + str(user_id))

@app.route("/image/<int:user_id>")
def show_image(user_id):
    """
    """
    image = users.get_image(user_id)
    if not image:
        return error.page('Profiilikuvaa ei löytynyt', 'Virhe profiilikuvan hakemisessa')

    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/jpeg")
    return response

@app.route("/remove_image", methods=["GET", "POST"])
def remove_image():
    """
    """
    require_login()

    user_id = session.get("user_id")
    if not user_id:
        return error.page('Käyttäjää ei löytynyt', 'Virhe profiilikuvan poistamisessa')

    user = users.get_user(user_id)
    if not user:
        return error.page('Käyttäjää ei löytynyt', 'Virhe profiilikuvan poistamisessa')

    image = users.get_image(user_id)
    if not image:
        return error.page('Profiilikuvaa ei löytynyt', 'Virhe profiilikuvan poistamisessa')

    if request.method == "GET":
        return render_template("remove_image.html", user=user)

    if request.method == "POST":
        check_csrf()
        if "remove" in request.form:
            users.remove_image(user_id)
        return redirect("/user/" + str(user_id))

@app.route("/find_movie")
def find_movie():
    """
    Renders the movie search page, showing the results for the search query.

    Returns:
        rendered template: The rendered template for the find movie page.
    """
    query = request.args.get("query")
    if query:
        results = movies.find_movies(query)
    else:
        query = ""
        results = []
    return render_template("find_movie.html",query=query, results=results)

@app.route("/movie/<int:movie_id>")
def show_movie(movie_id):
    """
    Renders the page for a specific movie, displaying movie details, reviews, and classes.

    Args:
        movie_id: The ID of the movie to display.

    Returns:
        rendered template or error: The rendered template with movie data, reviews, and movie
        classes, or an error page if the movie is not found.
    """
    movie = movies.get_movie(movie_id)
    if not movie:
        return error.page("Elokuvaa ei löytynyt", "Virhe sivun hakemisessa")
    reviews_list = reviews.get_reviews(movie_id)
    classes = movies.get_classes(movie_id)
    return render_template("show_movie.html", movie=movie, reviews=reviews_list, classes=classes)

@app.route("/review/<int:review_id>")
def show_review(review_id):
    """
    Renders the page for a specific review, displaying the review details and its comments.

    Args:
        review_id: The ID of the review to display.

    Returns:
        rendered template or error: The rendered template with review data and comments, or an
        error page if the review is not found.
    """
    review = reviews.get_review(review_id)
    if not review:
        return error.page("Arvostelua ei löytynyt", "Virhe kommentin näytössä")
    comments_list = comments.get_comments(review_id)
    return render_template("show_review.html", review=review, comments=comments_list)

@app.route("/comment/<int:comment_id>")
def show_comment(comment_id):
    """
    Renders the page for a specific comment, displaying the comment details and the related review.

    Args:
        comment_id: The ID of the comment to display.

    Returns:
        rendered template or error: The rendered template with comment data and the related review,
        or an error page if the comment or review is not found.
    """
    comment = comments.get_comment(comment_id)
    if not comment:
        return error.page("Kommenttia ei löytynyt", "Virhe kommentin näytössä")

    review = reviews.get_review(comment["review_id"])
    if not review:
        return error.page("Arvostelua ei löytynyt", "Virhe kommentin näytössä")
    return render_template("show_comment.html", comment=comment, review=review)

@app.route("/new_movie")
def new_movie():
    """
    Renders the new movie form page for adding a new movie.

    Returns:
        rendered template: The rendered template for creating a new movie.
    """
    require_login()

    classes = movies.get_all_classes()
    return render_template("new_movie.html", classes=classes)

@app.route("/create_movie", methods=["GET", "POST"])
def create_movie():
    """
    Handles the creation of a new movie, processing the form data and adding the movie to the
    database.

    Returns:
        rendered template or redirect: Redirects to the home page on success, or renders an error
        page on failure.
    """
    require_login()
    check_csrf()

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

@app.route("/create_review", methods=["POST"])
def create_review():
    """
    Handles the creation of a new review for a movie. Validates the review input, including rating
    and content, and adds the review to the database.

    Returns:
        rendered template or redirect: Redirects to the movie page on success, or renders an error
        page on failure.
    """
    require_login()
    check_csrf()

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

    rating_id = reviews.get_rating(rating)
    if not rating_id:
        return error.page("Virheellinen arvosana", "Virhe arvostelun lisäämisessä")
    rating_id = rating_id[0]["id"]

    reviews.add_review(movie_id, user_id, rating_id, review)
    return redirect("/movie/" + str(movie_id))

@app.route("/create_comment", methods=["POST"])
def create_comment():
    """
    Handles the creation of a new comment on a review. Validates the comment input and saves the
    comment to the database.

    Returns:
        rendered template or redirect: Redirects to the review page on success, or renders an error
        page on failure.
    """
    require_login()
    check_csrf()

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

@app.route("/edit_movie/<int:movie_id>")
def edit_movie(movie_id):
    """
    Displays the form to edit an existing movie's details. Requires the user to be logged in and
    have ownership of the movie.

    Args:
        movie_id: ID of the movie to be edited.

    Returns:
        rendered template: Renders the "edit_movie.html" template with the current movie data
        or an error page if the user cannot edit the movie.
    """
    require_login()
    check_csrf()

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

@app.route("/update_movie", methods=["POST"])
def update_movie():
    """
    Handles updating an existing movie's data, including validation and saving the updated details
    to the database.

    Returns:
        rendered template or redirect: Redirects to the updated movie page on success, or renders
        an error page on failure.
    """
    require_login()
    check_csrf()
    movie_id = request.form["movie_id"]
    movie = movies.get_movie(movie_id)

    if not movie:
        return error.page("Elokuvaa ei löytynyt", "Virhe muokatessa elokuvan tietoja")

    if movie["user_id"] != session["user_id"]:
        return error.page("Käyttäjällä ei ole oikeuksia muokata elokuvan tietoja",
                          "Virhe muokatessa elokuvan tietoja")

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

@app.route("/edit_review/<int:review_id>", methods=["GET", "POST"])
def edit_review(review_id):
    """
    Displays the form to edit an existing review. Only the user who created the review is allowed
    to modify it. Processes the form submission and updates the review if valid.

    Args:
        review_id: The ID of the review to be edited.

    Returns:
        rendered template or redirect: Renders the "edit_review.html" template on GET request or
        redirects to the review page after successful POST request. If any error occurs, an error
        page is displayed.
    """
    require_login()
    review = reviews.get_review(review_id)

    if not review:
        return error.page("Arvostelua ei löytynyt", "Virhe muokatessa arvostelua")

    if review["user_id"] != session["user_id"]:
        return error.page("Käyttäjällä ei ole oikeuksia muokata arvostelua",
                    "Virhe muokatessa arvostelua")

    if request.method == "POST":
        check_csrf()
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

            rating_id = reviews.get_rating(rating)
            if not rating_id:
                return error.page("Virheellinen arvosana", "Virhe muokatessa arvostelua")
            rating_id = rating_id[0]["id"]

            reviews.update_review(review_id, review, rating_id)
            return redirect("/review/" + str(review_id))
        return redirect("/review/" + str(review_id))
    return render_template("edit_review.html", review=review, movie_id=review["movie_id"])

@app.route("/edit_comment/<int:comment_id>", methods=["GET", "POST"])
def edit_comment(comment_id):
    """
    Displays the form to edit an existing comment. Only the user who created the comment is allowed
    to modify it. Processes the form submission and updates the comment if valid.

    Args:
        comment_id: The ID of the comment to be edited.

    Returns:
        rendered template or redirect: Renders the "edit_comment.html" template on GET request or
        redirects to the comment page after successful POST request. If any error occurs, an
        error page is displayed.
    """
    require_login()

    comment = comments.get_comment(comment_id)
    if not comment:
        return error.page("Kommenttia ei löytynyt", "Virhe muokatessa kommenttia")

    if comment["user_id"] != session["user_id"]:
        return error.page("Käyttäjällä ei ole oikeuksia muokata kommenttia",
                    "Virhe muokatessa kommenttia")

    if request.method == "POST":
        check_csrf()
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

@app.route("/remove_movie/<int:movie_id>", methods=["GET", "POST"])
def remove_movie(movie_id):
    """
    Displays a confirmation form to remove a movie. Only the user who added the movie is allowed
    to remove it. If the form is confirmed, the movie is removed from the database.

    Args:
        movie_id: The ID of the movie to be removed.

    Returns:
        rendered template or redirect: Renders the "remove_movie.html" template on GET request or
        redirects to the home page after successful POST request. If any error occurs, an error
        page is displayed.
    """
    require_login()
    movie = movies.get_movie(movie_id)
    if not movie:
        return error.page("Elokuvaa ei löytynyt", "Virhe elokuvan poistossa")
    if movie["user_id"] != session["user_id"]:
        return error.page("Käyttäjällä ei oikeuksia poistaa elokuvaa", "Virhe elokuvan poistossa")

    if request.method == "GET":
        return render_template("remove_movie.html", movie=movie)

    if request.method == "POST":
        check_csrf()
        if "remove" in request.form:
            movies.remove_movie(movie_id)
            return redirect("/")
        else:
            return redirect("/movie/" + str(movie_id))

@app.route("/remove_review/<int:review_id>", methods=["GET", "POST"])
def remove_review(review_id):
    """
    Displays a confirmation form to remove a review. Only the user who created the review is
    allowed to remove it. If the form is confirmed, the review is removed from the database.

    Args:
        review_id: The ID of the review to be removed.

    Returns:
        rendered template or redirect: Renders the "remove_review.html" template on GET request or
        redirects to the movie page after successful POST request. If any error occurs, an error
        page is displayed.
    """
    require_login()
    review = reviews.get_review(review_id)

    if not review:
        return error.page("Arvostelua ei löytynyt", "Virhe arvostelun poistossa")
    if review["user_id"] != session["user_id"]:
        return error.page("Käyttäjällä ei oikeuksia poistaa arvostelua",
                        "Virhe arvostelun poistossa")

    if request.method == "GET":
        return render_template("remove_review.html", review=review)

    if request.method == "POST":
        check_csrf()
        if "remove" in request.form:
            reviews.remove_review(review_id)
            return redirect("/movie/" + str(review["movie_id"]))
        else:
            return redirect("/review/" + str(review_id))

@app.route("/remove_comment/<int:comment_id>", methods=["GET", "POST"])
def remove_comment(comment_id):
    """
    Displays a confirmation form to remove a comment. Only the user who created the comment is
    allowed to remove it. If the form is confirmed, the comment is removed from the database.

    Args:
        comment_id: The ID of the comment to be removed.

    Returns:
        rendered template or redirect: Renders the "remove_comment.html" template on GET request or
        redirects to the review page after successful POST request. If any error occurs, an error
        page is displayed.
    """
    require_login()
    comment = comments.get_comment(comment_id)

    if not comment:
        return error.page("Kommenttia ei löytynyt", "Virhe kommentin poistossa")
    if comment["user_id"] != session["user_id"]:
        return error.page("Käyttäjällä ei oikeuksia poistaa kommenttia",
                          "Virhe kommentin poistossa")

    if request.method == "GET":
        return render_template("remove_comment.html", comment=comment)

    if request.method == "POST":
        check_csrf()
        if "remove" in request.form:
            comments.remove_comment(comment_id)
            return redirect("/review/" + str(comment["review_id"]))
        else:
            return redirect("/comment/" + str(comment_id))

@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Displays the registration form for a new user and processes the form submission. Validates the
    input fields, checks for username availability, and creates a new user if valid.

    Returns:
        rendered template or error page: Renders the registration form or displays an error page
        if validation fails. Redirects to the "account_created.html" template if registration is
        successful.
    """
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
            return error.page("Salasanan tulee olla vähintään 5 merkkiä pitkä",
                              "Virhe käyttäjän luomisessa")

        try:
            users.create_user(username, password1)
        except sqlite3.IntegrityError:
            return error.page("Käyttäjänimi varattu", "Virhe käyttäjän luomisessa")
        return render_template("account_created.html")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Displays the login form and processes the form submission. Validates the entered username and
    password, and if they are correct, logs the user in by saving the user ID and username in the
    session.

    Returns:
        rendered template or error page: Renders the login form or displays an error page if login
        fails. Redirects to the home page upon successful login.
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if not username or not password:
            return error.page("Kaikki kentät tulee täyttää", "Virhe kirjautumisessa")

        user_id = users.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            session["username"] = username
            session["csrf_token"] = secrets.token_hex(16)
            return redirect("/")
        return error.page("Virheellinen käyttäjätunnus/salasana", "Virhe kirjautumisessa")
    return render_template("login.html")

@app.route("/logout")
def logout():
    """
    Logs the user out by clearing the session data.

    Returns:
        redirect: Redirects to the home page after logging out.
    """
    if "user_id" in session:
        del session["username"]
        del session["user_id"]
    return redirect("/")
