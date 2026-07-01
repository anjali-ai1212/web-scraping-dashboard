from flask import Flask, render_template, request, redirect, url_for, flash, session
'''from scipy import stats'''
from scraper.universal_scraper import scrape_website
from flask_bcrypt import Bcrypt
from config import Config
from database.db import mysql
from flask import send_file
from services.export_service import (
    export_csv,
    export_excel,
    export_json
)

app = Flask(__name__)
app.config.from_object(Config)

mysql.init_app(app)
bcrypt = Bcrypt(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        cur = mysql.connection.cursor()

        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()

        if user:
            flash("Email already exists!", "danger")
            cur.close()
            return redirect(url_for("register"))

        cur.execute(
            "INSERT INTO users(name,email,password) VALUES(%s,%s,%s)",
            (name, email, hashed_password),
        )

        mysql.connection.commit()
        cur.close()

        flash("Registration Successful!", "success")
        return redirect(url_for("register"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        cur = mysql.connection.cursor()

        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()

        cur.close()

        if user:

            if bcrypt.check_password_hash(user[3], password):

                session["user_id"] = user[0]
                session["name"] = user[1]
                session["email"] = user[2]

                flash("Login Successful!", "success")

                return redirect(url_for("dashboard"))

            else:

                flash("Invalid Password!", "danger")

        else:

            flash("Email Not Found!", "danger")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT 
            COUNT(*),
            COALESCE(SUM(total_links), 0),
            COALESCE(SUM(total_images), 0),
            COALESCE(SUM(total_emails), 0)
        FROM scrape_history
        WHERE user_id = %s
    """, (session["user_id"],))

    stats = cur.fetchone()
    cur.execute("""
        SELECT
            website_url,
            page_title,
            scraped_at
        FROM scrape_history
        WHERE user_id = %s
        ORDER BY id DESC
        LIMIT 5
    """, (session["user_id"],))

    recent_history = cur.fetchall()

    cur.close()

    return render_template(
        "dashboard.html",
        total_scrapes=stats[0],
        total_links=stats[1],
        total_images=stats[2],
        total_emails=stats[3],
        scraped_data=None,
        recent_history=recent_history
    )

@app.route("/scrape", methods=["POST"])
def scrape():

    if "user_id" not in session:
        return redirect(url_for("login"))

    url = request.form["url"]

    result = scrape_website(url)
    cur = mysql.connection.cursor()
    

    cur.execute("""
    INSERT INTO scrape_history
    (user_id, website_url, page_title, total_links,
    total_images, total_headings, total_emails, total_phones)

    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
""",
    (
    session["user_id"],
    url,
    result["title"],
    result["total_links"],
    result["total_images"],
    result["total_headings"],
    result["total_emails"],
    result["total_phones"]
))

    mysql.connection.commit()

    cur.close()

    return render_template(
        "dashboard.html",
        scraped_data=result
    )

@app.route("/logout")
def logout():

    session.clear()

    flash("Logged Out Successfully!", "success")

    return redirect(url_for("login"))
@app.route("/export/csv")
def export_csv_file():

    if "user_id" not in session:
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT website_url,
               page_title,
               total_links,
               total_images,
               total_headings,
               total_emails,
               total_phones,
               scraped_at
        FROM scrape_history
        WHERE user_id=%s
    """, (session["user_id"],))

    rows = cur.fetchall()
    cur.close()

    data = []

    for row in rows:
        data.append({
            "Website": row[0],
            "Title": row[1],
            "Links": row[2],
            "Images": row[3],
            "Headings": row[4],
            "Emails": row[5],
            "Phones": row[6],
            "Date": row[7]
        })

    file_path = export_csv(data)

    return send_file(file_path, as_attachment=True)


@app.route("/export/excel")
def export_excel_file():

    if "user_id" not in session:
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT website_url,
               page_title,
               total_links,
               total_images,
               total_headings,
               total_emails,
               total_phones,
               scraped_at
        FROM scrape_history
        WHERE user_id=%s
    """, (session["user_id"],))

    rows = cur.fetchall()
    cur.close()

    data = []

    for row in rows:
        data.append({
            "Website": row[0],
            "Title": row[1],
            "Links": row[2],
            "Images": row[3],
            "Headings": row[4],
            "Emails": row[5],
            "Phones": row[6],
            "Date": row[7]
        })

    file_path = export_excel(data)

    return send_file(file_path, as_attachment=True)


@app.route("/export/json")
def export_json_file():

    if "user_id" not in session:
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT website_url,
               page_title,
               total_links,
               total_images,
               total_headings,
               total_emails,
               total_phones,
               scraped_at
        FROM scrape_history
        WHERE user_id=%s
    """, (session["user_id"],))

    rows = cur.fetchall()
    cur.close()

    data = []

    for row in rows:
        data.append({
            "Website": row[0],
            "Title": row[1],
            "Links": row[2],
            "Images": row[3],
            "Headings": row[4],
            "Emails": row[5],
            "Phones": row[6],
            "Date": row[7]
        })

    file_path = export_json(data)

    return send_file(file_path, as_attachment=True)
@app.route("/history")
def history():

    if "user_id" not in session:
        return redirect(url_for("login"))

    page = request.args.get("page", 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    search = request.args.get("search", "")

    cur = mysql.connection.cursor()

    if search:
        cur.execute("""
            SELECT COUNT(*)
            FROM scrape_history
            WHERE user_id=%s
            AND website_url LIKE %s
        """, (session["user_id"], "%" + search + "%"))

        total = cur.fetchone()[0]

        cur.execute("""
            SELECT id,
                   website_url,
                   page_title,
                   total_links,
                   total_images,
                   total_headings,
                   total_emails,
                   total_phones,
                   scraped_at
            FROM scrape_history
            WHERE user_id=%s
            AND website_url LIKE %s
            ORDER BY id DESC
            LIMIT %s OFFSET %s
        """, (
            session["user_id"],
            "%" + search + "%",
            per_page,
            offset
        ))

    else:
        cur.execute("""
            SELECT COUNT(*)
            FROM scrape_history
            WHERE user_id=%s
        """, (session["user_id"],))

        total = cur.fetchone()[0]

        cur.execute("""
            SELECT id,
                   website_url,
                   page_title,
                   total_links,
                   total_images,
                   total_headings,
                   total_emails,
                   total_phones,
                   scraped_at
            FROM scrape_history
            WHERE user_id=%s
            ORDER BY id DESC
            LIMIT %s OFFSET %s
        """, (
            session["user_id"],
            per_page,
            offset
        ))

    history = cur.fetchall()
    cur.close()

    total_pages = (total + per_page - 1) // per_page

    return render_template(
        "history.html",
        history=history,
        search=search,
        page=page,
        total_pages=total_pages
    )

@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()

    cur.execute(
        "SELECT id, name, email FROM users WHERE id=%s",
        (session["user_id"],)
    )

    user = cur.fetchone()

    cur.close()

    return render_template("profile.html", user=user)

@app.route("/edit-profile", methods=["GET","POST"])
def edit_profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()

    if request.method=="POST":

        name=request.form["name"]

        email=request.form["email"]

        cur.execute("""
        UPDATE users
        SET name=%s,email=%s
        WHERE id=%s
        """,(name,email,session["user_id"]))

        mysql.connection.commit()

        flash("Profile Updated Successfully")

        return redirect(url_for("profile"))

    cur.execute("""
    SELECT name,email
    FROM users
    WHERE id=%s
    """,(session["user_id"],))

    user=cur.fetchone()

    cur.close()

    return render_template("edit_profile.html",user=user)

@app.route("/admin")
def admin():

    search = request.args.get("search", "")

    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM scrape_history")
    total_scrapes = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(SUM(total_emails),0) FROM scrape_history")
    total_emails = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(SUM(total_images),0) FROM scrape_history")
    total_images = cur.fetchone()[0]

    if search:
        cur.execute("""
            SELECT id,name,email
            FROM users
            WHERE name LIKE %s
            OR email LIKE %s
        """, ("%"+search+"%", "%"+search+"%"))
    else:
        cur.execute("""
            SELECT id,name,email
            FROM users
        """)

    users = cur.fetchall()

    cur.close()

    return render_template(
    "admin.html",
    users=users,
    total_users=total_users,
    total_scrapes=total_scrapes,
    total_emails=total_emails,
    total_images=total_images
)
     

@app.route("/delete-user/<int:id>")
def delete_user(id):

    cur = mysql.connection.cursor()

    cur.execute("DELETE FROM users WHERE id=%s", (id,))
    mysql.connection.commit()

    cur.close()
    flash("User Deleted Successfully!", "success")

    return redirect("/admin")

@app.route("/delete-history/<int:id>")
def delete_history(id):

    cur=mysql.connection.cursor()

    cur.execute("""
    DELETE FROM scrape_history
    WHERE id=%s
    """,(id,))

    mysql.connection.commit()

    flash("History Deleted")

    return redirect("/admin")

@app.route("/edit-user/<int:id>", methods=["GET","POST"])
def edit_user(id):

    cur = mysql.connection.cursor()

    if request.method=="POST":

        name=request.form["name"]
        email=request.form["email"]

        cur.execute("""
        UPDATE users
        SET name=%s,email=%s
        WHERE id=%s
        """,(name,email,id))

        mysql.connection.commit()

        return redirect(url_for("admin"))

    cur.execute("SELECT * FROM users WHERE id=%s",(id,))

    user=cur.fetchone()

    cur.close()

    return render_template("edit_user.html",user=user)

@app.route("/change-password",methods=["GET","POST"])
def change_password():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method=="POST":

        old=request.form["old"]

        new=request.form["new"]

        cur=mysql.connection.cursor()

        cur.execute(
        "SELECT password FROM users WHERE id=%s",
        (session["user_id"],)
        )

        user=cur.fetchone()

        if bcrypt.check_password_hash(user[0],old):

            password=bcrypt.generate_password_hash(new).decode("utf-8")

            cur.execute("""
            UPDATE users
            SET password=%s
            WHERE id=%s
            """,(password,session["user_id"]))

            mysql.connection.commit()

            flash("Password Changed")

        else:

            flash("Old Password Incorrect")

    return render_template("change_password.html")


print(app.url_map)

if __name__ == "__main__":
    app.run(debug=True)