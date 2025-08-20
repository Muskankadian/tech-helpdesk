from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = "your_secret_key"
bcrypt = Bcrypt(app)

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Muskan@4",  # replace with your MySQL password
    database="techhelpdesk_db"
)
cursor = db.cursor(dictionary=True)

# ---------------- Home Pages ----------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

# ---------------- Signup ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        # Check if user already exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("User already exists! Please log in.", "error")
            return redirect(url_for("signup"))

        # Hash the password before saving
        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

        try:
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", 
                (name, email, hashed_pw)
            )
            db.commit()
            flash("Signup successful! Please log in.", "success")
            return redirect(url_for("login"))
        except Error as e:
            db.rollback()
            flash("Database error: " + str(e), "error")

    return render_template("signup.html")

# ---------------- Login ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if user and bcrypt.check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            flash("Welcome back, " + user['name'] + "!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password.", "error")
            return redirect(url_for('login'))
    return render_template('login.html')

# ---------------- Dashboard ----------------
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        try:
            cursor.execute(
                "INSERT INTO tickets (user_id, title, description) VALUES (%s, %s, %s)",
                (session['user_id'], title, description)
            )
            db.commit()
            flash("Ticket created successfully!", "success")
        except Error as e:
            db.rollback()
            flash("Error creating ticket: " + str(e), "error")

    cursor.execute("SELECT * FROM tickets WHERE user_id=%s ORDER BY created_at DESC", (session['user_id'],))
    tickets = cursor.fetchall()
    return render_template('dashboard.html', tickets=tickets)

# ---------------- Logout ----------------
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('home'))

# ---------------- Run App ----------------
if __name__ == '__main__':
    app.run(debug=True)

