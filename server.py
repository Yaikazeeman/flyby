from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)


# Google Cloud SQL (change this accordingly)
PASSWORD ="capstone"
PUBLIC_IP_ADDRESS ="34.79.169.36"
DBNAME ="flyby_database"
PROJECT_ID ="flyby-capstone"
INSTANCE_NAME ="flyby-capstone:europe-west1:flyby-capstone-database"
SQLALCHEMY_DATABASE_URI = f"mysql+mysqldb://root:{PASSWORD}@{PUBLIC_IP_ADDRESS}/{DBNAME}?unix_socket=/cloudsql/{PROJECT_ID}:{INSTANCE_NAME}"
 
# configuration
app.config["SECRET_KEY"] = "bSkb22Tr+YaTLDtaIVtoui99n8KPVeDxLtil/A2Q"
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

engine = create_engine(SQLALCHEMY_DATABASE_URI)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
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

@app.route("/register_pilot", methods=["POST"])
def handle_register_pilot():
    first_name=request.form["first_name"]
    password=request.form["password"]
    picture=request.form["profile_url"]

    hashed_password = generate_password_hash(password)

    insert_query = f"""
    INSERT INTO PILOT_DATA4(first_name, profile_url, password)
    VALUES ('{first_name}', '{picture}', '{hashed_password}')
    """

    with engine.connect() as connection:
        connection.execute(insert_query)

        return redirect(url_for("index"))

################################# start pilot part

@app.route("/browse_pilots")
def browse_pilots():
    query = """
    SELECT id, first_name, profile_url
    FROM PILOT_DATA4
    """

    with engine.connect() as connection:
        pilots = connection.execute(query)

        return render_template("browse_pilots.html", pilots=pilots)


@app.route("/pilots/<pilot_id>")
def pilot_detail(pilot_id):
    query = f"""
    SELECT id, first_name, profile_url
    FROM PILOT_DATA4
    where id={pilot_id}
    """
    with engine.connect() as connection:
        pilot = connection.execute(query).fetchone()

        if pilot:
            return render_template("pilot_detail.html", pilot=pilot)
        else:
            return render_template("404.html"), 404

################################################### end pilot part

################################################## start company part


@app.route("/browse_companies")
def browse_companies():
    query = """
    SELECT id, company_name, profile_url, country, city, industry, badges
    FROM COMPANY_DATA4
    """

    with engine.connect() as connection:
        companies = connection.execute(query)

        return render_template("browse_companies.html", companies=companies)

@app.route("/companies/<company_id>")
def company_detail(company_id):
    query = f"""
    SELECT id, company_name, email, country, city, website_link, profile_url, description, industry, badges, member_since
    FROM COMPANY_DATA4
    where id={company_id}
    """
    with engine.connect() as connection:
        company = connection.execute(query).fetchone()

        if company:
            return render_template("company_detail.html", company=company)
        else:
            return render_template("404.html"), 404

######################################################## end company part

######################################################## start project part



@app.route("/browse_projects")
def browse_projects():
    query = """
    SELECT id, project_name, country, city, services, start_date
    FROM PROJECT_DATA4
    """

    with engine.connect() as connection:
        projects = connection.execute(query)

        return render_template("browse_projects.html", projects=projects)

@app.route("/projects/<project_id>")
def project_detail(project_id):
    query = f"""
    SELECT id, project_name, contact_email, country, city, description, services, certification, project_duration_days, start_date, years_of_experience
    FROM PROJECT_DATA4
    where id={project_id}
    """
    with engine.connect() as connection:
        project = connection.execute(query).fetchone()

        if project:
            return render_template("project_detail.html", project=project)
        else:
            return render_template("404.html"), 404

############################################################# end project part

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
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

@app.route("/logout")
def logout():
    session.pop("username")
    session.pop("user_id")

    return redirect(url_for("index"))


@app.route("/tweet", methods=["POST"])
def handle_tweet():
    tweet=request.form["tweet"]

    insert_query = f"""
    INSERT INTO tweets(tweet, user_id)
    VALUES ('{tweet}', {session['user_id']})
    """

    with engine.connect() as connection:
        connection.execute(insert_query)

        return redirect(url_for("index"))

@app.route("/follow/<followee>")
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

@app.route("/search")
def search():
    return render_template("search.html")

@app.route("/search", methods = ["POST"])
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


@app.route("/messages")
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


@app.route("/direct_messages/<user_id>")
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

@app.route("/sent_message", methods=["POST"])
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

app.run(debug=True)
