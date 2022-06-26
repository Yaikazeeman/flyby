from asyncio.windows_events import NULL
from flask import Flask, render_template, request, session, redirect, url_for
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

app = Flask(__name__)


# Google Cloud SQL (change this accordingly)
PASSWORD ="capstone"
PUBLIC_IP_ADDRESS ="34.79.169.36"
DBNAME ="flyby_database"
PROJECT_ID ="flyby-capstone"
INSTANCE_NAME ="flyby-capstone:europe-west1:flyby-capstone-database"
SQLALCHEMY_DATABASE_URI = f'mysql+mysqldb://root:{PASSWORD}@{PUBLIC_IP_ADDRESS}/{DBNAME}?unix_socket=/cloudsql/{PROJECT_ID}:{INSTANCE_NAME}'
 
# configuration
app.config["SECRET_KEY"] = "bSkb22Tr+YaTLDtaIVtoui99n8KPVeDxLtil/A2Q"
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

engine = create_engine(SQLALCHEMY_DATABASE_URI)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/posted_projects")
def posted_projects():
    return render_template("c_posted_projects.html")

@app.route("/running_projects")
def running_projects():
    return render_template("c_running_projects.html")

@app.route("/pilot_application_list")
def pilot_application_list():
    return render_template("c_pilot_application_list.html")

@app.route("/pilot_request_list")
def pilot_request_list():
    return render_template("c_pilot_request_list.html")

@app.route("/applied_projects")
def applied_projects():
    return render_template("p_applied_projects.html")

@app.route("/request_to_hire")
def request_to_hire():
    return render_template("p_request_to_hire.html")

@app.route("/p_running_projects")
def p_running_projects():
    return render_template("p_running_projects.html")

@app.route("/brochure", methods=["POST"])
def brochure():

    email = request.form["email"]

    insert_brochure_query = f"""
    INSERT INTO BROCHURE_DATA (email_brochure)
    VALUES ('{email}')
    """
    with engine.connect() as connection:
        connection.execute(insert_brochure_query)
        return redirect(url_for("index"))

@app.route("/pilot-signup", methods=["POST", "GET"])
def handle_signup_pilot():
    first_name=request.form["first_name"]
    last_name=request.form["last_name"]
    email=request.form["email"]
    password=request.form["password"]

    hashed_password = generate_password_hash(password)

    insert_query = f"""
    INSERT INTO PILOT_DATA (first_name, last_name, email, password)
    VALUES ('{first_name}', '{last_name}','{email}', '{hashed_password}')
    """

    get_id_query = f"""
    SELECT id FROM PILOT_DATA WHERE first_name = '{first_name}' AND last_name = '{last_name}' AND email = '{email}'
    """

    with engine.connect() as connection:
        connection.execute(insert_query)
        id = connection.execute(get_id_query).fetchone()
        return redirect(f"/pilotregister/'{int(id[0])}'")


@app.route("/company-signup", methods=["POST"])
def handle_signup_company():
    name=request.form["company_name"]
    email=request.form["email"]
    password=request.form["password"]

    hashed_password = generate_password_hash(password)

    insert_query = f"""
    INSERT INTO COMPANY_DATA (company_name, email, password)
    VALUES ('{name}','{email}', '{hashed_password}')
    """
    get_id_query = f"""
    SELECT id FROM COMPANY_DATA WHERE company_name = '{name}' AND email = '{email}'
    """

    with engine.connect() as connection:
        connection.execute(insert_query)
        id = connection.execute(get_id_query).fetchone()
        return redirect(f"/companyregister/'{int(id[0])}'")

@app.route("/createprojectpage")
def get_create_project_page():
    return render_template("create_project.html")

@app.route("/createproject", methods=["POST"])
def handle_create_project():
    project_name=request.form["project_name"]
    services=request.form["services"]
    country=request.form["country"] 
    city=request.form["city"] 
    start_date=request.form["start_date"] 
    duration=request.form["duration"] 
    description=request.form["description"] 
    project_requirements=request.form["project_requirements"] 
    certification=request.form["certification"] 
    years_of_experience=request.form["years_of_experience"] 
    salary=request.form["salary"] 
    project_email=request.form["project_email"] 

    insert_query = f"""
    INSERT INTO MOCK_DATA (project_name, services, country, city, start_date, duration, description, project_requirements, certification, years_of_experience, salary, project_email)
    VALUES ('{project_name}', '{services}', '{country}', '{city}', '{start_date}', {duration}, '{description}', '{project_requirements}', '{certification}', {years_of_experience}, {salary}, '{project_email}')
    """
    get_id_query = f"""
    SELECT id FROM MOCK_DATA WHERE project_name = '{project_name}' AND project_email = '{project_email}'
    """

    with engine.connect() as connection:
        connection.execute(insert_query)
        id = connection.execute(get_id_query).fetchone()
        return redirect(f"/projects/'{id[0]}'")

@app.route("/pilotregister/<pilot_id>")
def pilotregister(pilot_id):

    get_pilot_query = f"""
    SELECT id, first_name, last_name, email FROM PILOT_DATA WHERE id = {pilot_id}
    """

    with engine.connect() as connection:
        pilot = connection.execute(get_pilot_query).fetchall()
        return render_template("pilotregister.html", pilot=pilot[0])

@app.route("/companyregister/<company_id>")
def companyregister(company_id):


    get_company_query = f"""
    SELECT id, company_name, email FROM COMPANY_DATA WHERE id = {company_id}
    """

    with engine.connect() as connection:
        company = connection.execute(get_company_query).fetchall()
        return render_template("companyregister.html", company=company[0])


@app.route("/register_pilot/<pilot_id>", methods=["POST"])
def handle_register_pilot(pilot_id):
    first_name=request.form["first_name"]
    last_name=request.form["last_name"]
    email=request.form["email"]
    gender=request.form["gender"]
    country=request.form["country"]
    city=request.form["city"]
    profession=request.form["profession"]
    certifications=request.form["certifications"]
    services=request.form["services"]
    years_of_experience=request.form["years_of_experience"]
    portfolio_url=request.form["portfolio_url"]
    profilepicture_url=request.form["profilepicture_url"]
    hourly_rate=request.form["hourly_rate"]
    description=request.form["description"]

    s1_mechanical_understanding=request.form["s1"]
    s2_communication_skills=request.form["s2"]
    s3_problem_solving =request.form["s3"]
    s4_detail_oriented =request.form["s4"]
    s5_knowledge_of_regulations =request.form["s5"]
    s6_navigation=request.form["s6"]

    member_since = date.today().strftime("%Y-%m-%d %H:%M:%S")
    flyby_certified = 'No'
    badge = "New Joiner"

    insert_query = f"""
    UPDATE PILOT_DATA
    SET 
        first_name = '{first_name}', 
        last_name = '{last_name}',
        email = '{email}', 
        gender = '{gender}', 
        country = '{country}',
        city = '{city}', 
        profession = '{profession}', 
        certifications = '{certifications}', 
        services = '{services}', 
        years_of_experience = {years_of_experience}, 
        portfolio_url = '{portfolio_url}', 
        profilepicture_url = '{profilepicture_url}', 
        hourly_rate = {hourly_rate}, 
        description = '{description}',
        s1_mechanical_understanding =  {s1_mechanical_understanding}, 
        s2_communication_skills = {s2_communication_skills}, 
        s3_problem_solving = {s3_problem_solving}, 
        s4_detail_oriented = {s4_detail_oriented}, 
        s5_knowledge_of_regulations =  {s5_knowledge_of_regulations}, 
        s6_navigation = {s6_navigation}, 
        member_since = '{member_since}', 
        flyby_certified = '{flyby_certified}' , 
        badge = '{badge}' 
    WHERE id = {pilot_id}
    """

    with engine.connect() as connection:
        connection.execute(insert_query)

        return redirect(url_for("browse_companies"))


@app.route("/register_company/<company_id>", methods=["POST"])
def handle_register_company(company_id):
    company_name=request.form["company_name"]
    email=request.form["email"]
    country=request.form["country"]
    city=request.form["city"]
    number_of_employees=request.form["number_of_employees"]
    industry=request.form["industry"]
    profilepicture_url=request.form["profilepicture_url"]
    website_link=request.form["website_link"]
    description=request.form["description"]

    member_since = date.today().strftime("%Y-%m-%d %H:%M:%S")
    badge = "New Joiner"

    insert_query = f"""
    UPDATE COMPANY_DATA
    SET 
        company_name = '{company_name}',
        email = '{email}', 
        country = '{country}',
        city = '{city}', 
        number_of_employees = '{number_of_employees}', 
        industry = '{industry}', 
        website_link = '{website_link}', 
        profilepicture_url = '{profilepicture_url}', 
        description = '{description}',
        member_since = '{member_since}',  
        badge = '{badge}' 
    WHERE id = {company_id}
    """

    with engine.connect() as connection:
        connection.execute(insert_query)

        return redirect(url_for("browse_pilots"))


################################# start pilot part

@app.route("/browse_pilots", methods=["POST", "GET"])
def browse_pilots():
    if "user_id" not in session:
        return render_template("403.html"), 403    
    else:

        if request.method == 'POST':

            name = request.form["name"]
            location = request.form["location"]
            service = request.form["service"]

            query = f"""
            SELECT id, first_name, profilepicture_url, services, last_name, badge 
            FROM PILOT_DATA WHERE 
                first_name = '{name}' OR 
                last_name = '{name}' OR 
                city = '{location}' OR 
                country = '{location}' OR 
                services = '{service}'
            """
        else:
            query = """
            SELECT id, first_name, profilepicture_url, services, last_name, badge
            FROM PILOT_DATA
            """

        with engine.connect() as connection:
            pilots = connection.execute(query)

            return render_template("browse_pilots.html", pilots=pilots)


@app.route("/pilots/<pilot_id>")
def pilot_detail(pilot_id):
    if "user_id" not in session:
        return render_template("403.html"), 403    
    else:
        query = f"""
        SELECT id, first_name, profilepicture_url, last_name, city, country, gender, badge, services, years_of_experience, member_since, description, s2_communication_skills
        FROM PILOT_DATA
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


@app.route("/browse_companies", methods=["POST", "GET"])
def browse_companies():
    if "user_id" not in session:
        return render_template("403.html"), 403    
    else:

        if request.method == 'POST':

            name = request.form["name"]
            location = request.form["location"]
            industry = request.form["industry"]

            query = f"""
            SELECT id, company_name, profilepicture_url, country, city, industry, badge
            FROM COMPANY_DATA WHERE 
                company_name = '{name}' OR 
                city = '{location}' OR 
                country = '{location}' OR 
                industry = '{industry}'
            """
        else:

            query = """
            SELECT id, company_name, profilepicture_url, country, city, industry, badge
            FROM COMPANY_DATA
            """

        with engine.connect() as connection:
            companies = connection.execute(query)

            return render_template("browse_companies.html", companies=companies)

@app.route("/companies/<company_id>")
def company_detail(company_id):
    if "user_id" not in session:
        return render_template("403.html"), 403    
    else:
        query = f"""
        SELECT id, company_name, email, country, city, website_link, profilepicture_url, description, industry, badge, member_since
        FROM COMPANY_DATA
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



@app.route("/browse_projects", methods=["POST", "GET"])
def browse_projects():
    if "user_id" not in session:
        return render_template("403.html"), 403    
    else:
        if request.method == 'POST':

            name = request.form["name"]
            location = request.form["location"]
            service = request.form["service"]

            query = f"""
            SELECT id, project_name, country, city, services, start_date
            FROM MOCK_DATA WHERE
                project_name = '{name}' OR
                city = '{location}' OR 
                country = '{location}' OR 
                services = '{service}'
            """
        else:

            query = """
            SELECT id, project_name, country, city, services, start_date
            FROM MOCK_DATA
            """

        with engine.connect() as connection:
            projects = connection.execute(query)

            return render_template("browse_projects.html", projects=projects)

@app.route("/projects/<project_id>")
def project_detail(project_id):
    if "user_id" not in session:
        return render_template("403.html"), 403    
    else:
        query = f"""
        SELECT id, project_name, project_email, country, city, description, services, certification, duration, start_date, years_of_experience, project_requirements
        FROM MOCK_DATA
        where id={project_id}
        """
        with engine.connect() as connection:
            project = connection.execute(query).fetchone()

            if project:
                return render_template("project_detail.html", project=project)
            else:
                return render_template("404.html"), 404

############################################################# end project part

@app.route("/payment")
def payment():
    # if "user_id" not in session:
    #     return render_template("403.html"), 403    
    # else:
        return render_template("payment-methode.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def handle_login():
    email=request.form["email"]
    password=request.form["password"]

    login_query = f"""
    SELECT password, id
    FROM PILOT_DATA
    WHERE email='{email}'

    UNION

    SELECT password, id
    FROM COMPANY_DATA
    WHERE email='{email}'

    """

    with engine.connect() as connection:
        user = connection.execute(login_query).fetchone()
        print(user)
        if user and check_password_hash(user[0], password):
            session["user_id"] = user[1]
            session["useremail"] = email
            return redirect(url_for("index"))
        else:
            return render_template("404.html"), 404

@app.route("/logout")
def logout():
    session.pop("useremail")
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

# if __name__ == '__main__':
#     app.run(debug=True)