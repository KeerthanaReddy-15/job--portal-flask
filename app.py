from flask import Flask, render_template, request,redirect,url_for,session
import sqlite3

app = Flask(__name__)
app.secret_key="jobportal_secret_key"

# ---------- DATABASE INIT ----------
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        company TEXT,
        location TEXT,
        description TEXT
    )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            password TEXT
        )
    """)
    cursor.execute("""
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    job_id INTEGER
)
""")
    conn.commit()
    conn.close()

init_db()

# ---------- HOME ----------
@app.route("/")
def home():
    return "Job Portal Project Started Successfully"







# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, password)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")






# ---------- USERS LIST ----------
@app.route("/users")
def users():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    data = cursor.fetchall()
    conn.close()

    return render_template("users.html", users=data)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM users WHERE email = ? AND password = ?",
            (email, password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]   # ✅ FIX
            return redirect(url_for("dashboard"))
        else:
            return "Invalid credentials"

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # total jobs
    cursor.execute("SELECT COUNT(*) FROM jobs")
    total_jobs = cursor.fetchone()[0]

    # applied jobs count for this user
    cursor.execute(
        "SELECT COUNT(*) FROM applications WHERE user_id = ?",
        (user_id,)
    )
    applied_jobs = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        total_jobs=total_jobs,
        applied_jobs=applied_jobs
    )




@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))





@app.route("/add-job", methods=["GET", "POST"])
def add_job():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form["title"]
        company = request.form["company"]
        location = request.form["location"]
        description = request.form["description"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO jobs (title, company, location, description) VALUES (?, ?, ?, ?)",
            (title, company, location, description)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("dashboard"))

    return render_template("add_job.html")



@app.route('/jobs')
def view_jobs():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title,company, location, description FROM jobs")
    jobs = cursor.fetchall()
    conn.close()
    return render_template("jobs.html", jobs=jobs)



@app.route("/apply/<int:job_id>", methods=["POST"])
def apply_job(job_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # prevent duplicate apply
    cursor.execute(
        "SELECT 1 FROM applications WHERE user_id=? AND job_id=?",
        (user_id, job_id)
    )

    if cursor.fetchone():
        conn.close()
        return redirect(url_for("applied_jobs"))

    # insert application
    cursor.execute(
        "INSERT INTO applications (user_id, job_id) VALUES (?, ?)",
        (user_id, job_id)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("applied_jobs"))
    


@app.route('/applied-jobs')
def applied_jobs():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT jobs.title, jobs.company, jobs.location, jobs.description
        FROM applications
        JOIN jobs ON applications.job_id = jobs.id
        WHERE applications.user_id = ?
    """, (user_id,))

    applied = cursor.fetchall()
    conn.close()

    return render_template("applied_jobs.html", jobs=applied)


# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)

