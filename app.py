from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "jobportal_secret_key"
DB = "database.db"

# ---------- DATABASE INIT ----------
def init_db():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        password TEXT
    )
    """)

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
    return redirect(url_for("login"))

# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, password)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")

# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM users WHERE email=? AND password=?",
            (email, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            return redirect(url_for("dashboard"))
        else:
            return "Invalid credentials"

    return render_template("login.html")

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM jobs")
    total_jobs = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM applications WHERE user_id=?",
        (session["user_id"],)
    )
    applied_jobs = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        total_jobs=total_jobs,
        applied_jobs=applied_jobs
    )

# ---------- ADD JOB ----------
@app.route("/add-job", methods=["GET", "POST"])
def add_job():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form["title"]
        company = request.form["company"]
        location = request.form["location"]
        description = request.form["description"]

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO jobs (title, company, location, description) VALUES (?, ?, ?, ?)",
            (title, company, location, description)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("jobs"))

    return render_template("add_job.html")

# ---------- VIEW JOBS ----------
@app.route("/jobs")
def jobs():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, company, location, description FROM jobs")
    jobs = cursor.fetchall()
    conn.close()

    return render_template("jobs.html", jobs=jobs)

# ---------- APPLY JOB ----------
@app.route("/apply/<int:job_id>", methods=["POST"])
def apply_job(job_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM applications WHERE user_id=? AND job_id=?",
        (session["user_id"], job_id)
    )

    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO applications (user_id, job_id) VALUES (?, ?)",
            (session["user_id"], job_id)
        )
        conn.commit()

    conn.close()
    return redirect(url_for("applied_jobs"))

# ---------- APPLIED JOBS ----------
@app.route("/applied-jobs")
def applied_jobs():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT jobs.title, jobs.company, jobs.location, jobs.description
        FROM applications
        JOIN jobs ON applications.job_id = jobs.id
        WHERE applications.user_id = ?
    """, (session["user_id"],))

    jobs = cursor.fetchall()
    conn.close()

    return render_template("applied_jobs.html", jobs=jobs)

# ---------- USERS ----------
@app.route("/users")
def users():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM users")
    users = cursor.fetchall()
    conn.close()

    return render_template("users.html", users=users)

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)