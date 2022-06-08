from flask import Flask, render_template, request, session, redirect, url_for
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash, check_password_hash

tweeter = Flask(__name__)
tweeter.config["SECRET_KEY"] = "this is not secret, remember, change it!"
engine = create_engine("sqlite:///tweeter.db")

@tweeter.route("/")
def index():
    tweets = []
    if "username" in session:
        query = f"""
        SELECT u.id, u.picture, u.username, t.tweet
        FROM tweets t
        INNER JOIN users u ON t.user_id=u.id
        INNER JOIN follows f ON f.followee_id=u.id
        WHERE f.follower_id={session['user_id']}
        """

        with engine.connect() as connection:
            tweets = connection.execute(query).fetchall()

    return render_template("index.html", tweets=tweets)

@tweeter.route("/register")
def register():
    return render_template("register.html")

@tweeter.route("/register", methods=["POST"])
def handle_register():
    username=request.form["username"]
    password=request.form["password"]
    picture=request.form["picture"]

    hashed_password = generate_password_hash(password)

    insert_query = f"""
    INSERT INTO users(username, picture, password)
    VALUES ('{username}', '{picture}', '{hashed_password}')
    """

    with engine.connect() as connection:
        connection.execute(insert_query)

        return redirect(url_for("index"))


@tweeter.route("/users")
def users():
    query = """
    SELECT id, username, picture
    FROM users
    """

    with engine.connect() as connection:
        users = connection.execute(query)

        return render_template("users.html", users=users)


@tweeter.route("/users/<user_id>")
def user_detail(user_id):
    query = f"""
    SELECT id, username, picture
    FROM users
    where id={user_id}
    """

    tweets_query = f"""
    SELECT tweet
    FROM tweets
    WHERE user_id={user_id}
    """

    with engine.connect() as connection:
        user = connection.execute(query).fetchone()
        tweets = connection.execute(tweets_query).fetchall()

        if user:
            return render_template("user_detail.html", user=user, tweets=tweets)
        else:
            return render_template("404.html"), 404

@tweeter.route("/login")
def login():
    return render_template("login.html")

@tweeter.route("/login", methods=["POST"])
def handle_login():
    username=request.form["username"]
    password=request.form["password"]

    login_query = f"""
    SELECT password, id
    FROM users
    WHERE username='{username}'
    """

    with engine.connect() as connection:
        user = connection.execute(login_query).fetchone()

        if user and check_password_hash(user[0], password):
            session["user_id"] = user[1]
            session["username"] = username
            return redirect(url_for("index"))
        else:
            return render_template("404.html"), 404

@tweeter.route("/logout")
def logout():
    session.pop("username")
    session.pop("user_id")

    return redirect(url_for("index"))


@tweeter.route("/tweet", methods=["POST"])
def handle_tweet():
    tweet=request.form["tweet"]

    insert_query = f"""
    INSERT INTO tweets(tweet, user_id)
    VALUES ('{tweet}', {session['user_id']})
    """

    with engine.connect() as connection:
        connection.execute(insert_query)

        return redirect(url_for("index"))

@tweeter.route("/follow/<followee>")
def follow(followee):
    if "user_id" not in session:
        return render_template("403.html"), 403    
    else:
        follower = session["user_id"]

        insert_query = f"""
        INSERT INTO follows(follower_id, followee_id)
        VALUES ({follower}, {followee})
        """

        with engine.connect() as connection:
            connection.execute(insert_query)

            return redirect(url_for("index"))

@tweeter.route("/search")
def search():
    return render_template("search.html")

@tweeter.route("/search", methods = ["POST"])
def search_keyword():
    keyword = request.form["keyword"]

    search_query = f"""
    SELECT tweet, user_id, picture, username
    FROM tweets
    INNER JOIN users ON users.id = tweets.user_id
    WHERE tweets.tweet LIKE '%{keyword}%'
    """

    with engine.connect() as connection:
        tweets = connection.execute(search_query)
        return render_template("search.html", tweets=tweets)


@tweeter.route("/messages")
def messages():
    if "user_id" not in session:
        return render_template("403.html"), 403    
    else:
        query = f"""
        SELECT u.id, u.username, u.picture
        FROM users u
        INNER JOIN messages m ON m.from_id=u.id
        WHERE m.to_id = {session['user_id']}
        UNION
        SELECT DISTINCT u.id, u.username, u.picture
        FROM users u
        INNER JOIN messages m ON m.to_id=u.id
        WHERE m.from_id = {session['user_id']}
        """

        all_users_query = f"""
        SELECT id, username
        FROM users
        WHERE id <> {session['user_id']}
        """

        with engine.connect() as connection:
            messengers = connection.execute(query).fetchall()
            users = connection.execute(all_users_query).fetchall()

            return render_template("messages.html", messengers=messengers, users=users)


@tweeter.route("/direct_messages/<user_id>")
def direct_messages(user_id):
    query = f"""
    SELECT id, username, picture
    FROM users
    where id={user_id} 
    """

    own_user_query = f"""
    SELECT username, picture
    FROM users
    WHERE id={session["user_id"]} 
    """

    message_query = f"""
    SELECT text, from_id, to_id
    FROM messages
    WHERE (from_id={user_id} AND to_id={session['user_id']} )
    OR (from_id={session['user_id']} AND to_id={user_id})
    """

    with engine.connect() as connection:
        user = connection.execute(query).fetchone()
        self = connection.execute(own_user_query).fetchone()
        messages = connection.execute(message_query).fetchall()

        if user:
            return render_template("direct_message.html", user=user, messages=messages, self=self)
        else:
            return render_template("404.html"), 404

@tweeter.route("/sent_message", methods=["POST"])
def handle_sent_message():
    print(request.form)
    message = request.form["message"]
    to_id = request.form["to_id"]

    insert_query = f"""
    INSERT INTO messages(text, from_id, to_id)
    VALUES ('{message}', {session['user_id']}, '{to_id}')
    """

    with engine.connect() as connection:
        connection.execute(insert_query)

        return redirect(url_for("direct_messages",user_id=to_id))

tweeter.run(debug=True)
