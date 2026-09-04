from flask import Flask, render_template, request, session, redirect, url_for, abort
import os
import sqlite3
from werkzeug.utils import secure_filename
app = Flask(__name__)
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "dev-key"
)
UPLOAD_FOLDER = os.path.join(
    app.root_path,
    "static",
    "uploads",
    "profiles"
)

ALLOWED_IMAGE_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

os.makedirs(
    app.config["UPLOAD_FOLDER"],
    exist_ok=True
)
conn = sqlite3.connect("bookclub.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        book TEXT NOT NULL,
        review TEXT NOT NULL
    )
""")

with sqlite3.connect("bookclub.db") as conn:
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(users)")
    existing_columns = {
        column[1]
        for column in cursor.fetchall()
    }

    if "profile_picture" not in existing_columns:
        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN profile_picture TEXT
        """)

conn.commit()
conn.close()

def allowed_profile_picture(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_IMAGE_EXTENSIONS
    )

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/events")
def events():
    return render_template("events.html")

@app.route("/writings")
def writings():
    return render_template("writings.html")

@app.route("/writings/CreativeWriting")
def CreativeWriting():
    return render_template("WritingSubmissions.html")

@app.route("/books")
def books():
    return render_template("books.html")




BOOKS = {
    "CanneryRow": {
        "title": "Cannery Row",
        "image": "images/Can.jpg" 
    },         
    "TheHourOfTheStar": {
        "title": "The Hour of the Star",
        "image": "images/Star.jpg"
    },    

    "TheEmperorOfGladness": {
        "title": "The Emperor of Gladness",
        "image": "images/Glad.jpg"
    },

    "Vaim": {
        "title": "Vaim",
        "image": "images/Vaim.jpg"
    },

    "ADogsHeart": {
        "title": "A Dog's Heart",
        "image": "images/ADogsHeart.jpg"
    },
    "GriefIsAThingWithFeathers": {
        "title": "Grief Is A Thing With Feathers",
        "image": "images/Grief.jpg" 
    }, 
    "Siddartha": {
        "title": "Siddartha",
        "image": "images/Sid.jpg" 
    }, 
    "DriveYourPlowOverTheBonesOfTheDead": {
        "title": "Drive Your Plow Over the Bones of the Dead",
        "image": "images/Plow.jpg" 
    },    
    "TheOldManAndTheSea": {
        "title": "The Old Man and the Sea",
        "image": "images/Old.jpg" 
    }, 
    "SmallThingsLikeThese": {
        "title": "Small Things Like These",
        "image": "images/Small.jpg" 
    },    
    "Frankenstein": {
        "title": "Frankenstein",
        "image": "images/Frank.jpg" 
    },     
    "GiovannisRoom": {
        "title": "Giovanni's Room",
        "image": "images/GiovannisRoom.jpg"
    },    
}


@app.route("/books/<book_slug>", methods=["GET", "POST"])
def book_page(book_slug):

    book_details = BOOKS.get(book_slug)

    if book_details is None:
        abort(404)

    if request.method == "POST":

        if "username" not in session:
            return redirect("/login")

        review_text = request.form.get("review", "").strip()
        rating_text = request.form.get("rating", "").strip()

        try:
            rating = int(rating_text)
        except ValueError:
            rating = 0

        if review_text and 1 <= rating <= 5:

            with sqlite3.connect("bookclub.db") as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO reviews
                        (username, book, review, rating)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        session["username"],
                        book_details["title"],
                        review_text,
                        rating,
                    
                    )
                )

        return redirect(f"/books/{book_slug}")

    with sqlite3.connect("bookclub.db") as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
            reviews.username,
            reviews.review,
            reviews.rating,
            users.profile_picture
        FROM reviews
        LEFT JOIN users
            ON reviews.username = users.username
        WHERE reviews.book = ?
        ORDER BY reviews.id DESC

            """,
            (book_details["title"],)
        )

        reviews = cursor.fetchall()

        cursor.execute(
            """
            SELECT AVG(rating), COUNT(rating)
            FROM reviews
            WHERE book = ?
            """,
            (book_details["title"],)
        )

        average_rating, rating_count = cursor.fetchone()

    return render_template(
        "book.html",
        book=book_details,
        reviews=reviews,
        average_rating=average_rating,
        rating_count=rating_count
    )

@app.route("/user/<username>")
def public_profile(username):

    with sqlite3.connect("bookclub.db") as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT profile_picture
            FROM users
            WHERE username = ?
        """, (username,))

        user = cursor.fetchone()

        if user is None:
            abort(404)

        profile_picture = user[0]

        cursor.execute("""
            SELECT book, review
            FROM reviews
            WHERE username = ?
            ORDER BY id DESC
        """, (username,))

        reviews = cursor.fetchall()

    return render_template(
        "public_profile.html",
        username=username,
        profile_picture=profile_picture,
        reviews=reviews
    )

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        action = request.form["action"]

        if action == "register":

            username = request.form["register_username"]
            email = request.form["register_email"]
            password = request.form["register_password"]

            conn = sqlite3.connect("bookclub.db")
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO users
                (username, email, password)
                VALUES (?, ?, ?)
            """, (username, email, password))

            conn.commit()
            conn.close()

            return redirect("/home")

        elif action == "login":

            username = request.form["login_username"]
            password = request.form["login_password"]

            conn = sqlite3.connect("bookclub.db")
            cursor = conn.cursor()

            cursor.execute("""
                SELECT *
                FROM users
                WHERE username = ?
                AND password = ?
            """, (username, password))

            user = cursor.fetchone()

            conn.close()

            if user:
                
                session["username"] = username
                return redirect("/home")
            else:
                return "Invalid username or password."

    return render_template("login.html")

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")
@app.route("/profile", methods=["GET", "POST"])
def profile():

    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    upload_message = None

    if request.method == "POST":

        uploaded_file = request.files.get(
            "profile_picture"
        )

        if (
            uploaded_file is None
            or uploaded_file.filename == ""
        ):
            upload_message = "Please select an image."

        elif not allowed_profile_picture(
            uploaded_file.filename
        ):
            upload_message = (
                "Please upload a PNG, JPG, JPEG "
                "or WEBP image."
            )

        else:
            original_filename = secure_filename(
                uploaded_file.filename
            )

            extension = original_filename.rsplit(
                ".",
                1
            )[1].lower()

            safe_username = secure_filename(username)

            stored_filename = (
                f"{safe_username}_profile.{extension}"
            )

            save_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                stored_filename
            )

            uploaded_file.save(save_path)

            with sqlite3.connect(
                "bookclub.db"
            ) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    UPDATE users
                    SET profile_picture = ?
                    WHERE username = ?
                """, (
                    stored_filename,
                    username
                ))

            return redirect(url_for("profile"))

    with sqlite3.connect("bookclub.db") as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT profile_picture
            FROM users
            WHERE username = ?
        """, (username,))

        user = cursor.fetchone()

        cursor.execute("""
            SELECT book, review
            FROM reviews
            WHERE username = ?
            ORDER BY id DESC
        """, (username,))

        user_reviews = cursor.fetchall()

    profile_picture = None

    if user is not None:
        profile_picture = user[0]
    
    return render_template(
        "profile.html",
        username=username,
        profile_picture=profile_picture,
        reviews=user_reviews,
        upload_message=upload_message
    )

@app.route("/test-reviews")
def test_reviews():
    with sqlite3.connect("bookclub.db") as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM reviews")
        return str(cursor.fetchall())

@app.route("/test-db")
def test_db():

    import sqlite3

    conn = sqlite3.connect("bookclub.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")

    users = cursor.fetchall()

    conn.close()

    return str(users)
if __name__ == "__main__":
    app.run(debug=True)


