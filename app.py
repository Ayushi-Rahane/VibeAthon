from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from datetime import date as dt_date

app = Flask(__name__)
app.secret_key = 'f982769ef50cb351c6905ac625fdea35'

# MySQL connection setup
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="imastronaut",
    database="edutrack"
)

# ---------------- Dashboard ----------------
@app.route('/')
def dashboard():
    if not session.get('logged_in') or not session.get('user_id'):
        return redirect(url_for('login'))

    user_id = session['user_id']
    cursor = db.cursor(dictionary=True)

    # Fetch user info
    cursor.execute("SELECT * FROM students WHERE Student_ID = %s", (user_id,))
    student = cursor.fetchone()

    # Fetch recent progress
    cursor.execute("SELECT * FROM progress WHERE Student_ID = %s ORDER BY Date DESC LIMIT 5", (user_id,))
    recent_progress = cursor.fetchall()

    # Fetch goals
    cursor.execute("SELECT * FROM goals WHERE Student_ID = %s ORDER BY Created_At DESC LIMIT 5", (user_id,))
    goals = cursor.fetchall()

    cursor.close()

    return render_template('index.html', student=student, recent_progress=recent_progress, goals=goals)


# ---------------- Login ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password']

        cursor = db.cursor(dictionary=True)
        query = "SELECT * FROM students WHERE email = %s AND password_hash = %s"
        cursor.execute(query, (email, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session['logged_in'] = True
            session['user_id'] = user['Student_ID']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ---------------- Onboarding Form ----------------
@app.route('/onboarding', methods=['GET', 'POST'])
def onboarding():
    if request.method == 'POST':
        name = request.form['name']
        grade = request.form['grade']
        subjects = request.form['subjects']
        email = request.form['email']
        password = request.form['password']

        cursor = db.cursor()
        query = """INSERT INTO students (name, grade, subjects, email, password_hash) 
                   VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(query, (name, grade, subjects, email, password))
        db.commit()
        cursor.close()

        flash("Registration successful! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('onboarding.html')


# ---------------- Add Study Progress ----------------
@app.route('/add_progress', methods=['POST'])
def add_progress():
    if not session.get('user_id'):
        return redirect(url_for('login'))

    student_id = session['user_id']
    date_value = request.form['date'] or dt_date.today().strftime("%Y-%m-%d")
    subject = request.form['subject']
    activity = request.form['activity']
    notes = request.form['notes']

    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO progress (Student_ID, Date, Subject, Activity, Notes)
        VALUES (%s, %s, %s, %s, %s)
    """, (student_id, date_value, subject, activity, notes))
    db.commit()
    cursor.close()

    flash("Progress report added successfully!", "success")
    return redirect(url_for('dashboard'))


# ---------------- Goals ----------------
@app.route('/add_goal', methods=['POST'])
def add_goal():
    if not session.get('user_id'):
        return redirect(url_for('login'))

    student_id = session['user_id']
    goal_text = request.form['goal']

    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO goals (Student_ID, Goal_Text, Status, Created_At)
        VALUES (%s, %s, %s, NOW())
    """, (student_id, goal_text, "Pending"))
    db.commit()
    cursor.close()

    flash("Goal added successfully!", "success")
    return redirect(url_for('dashboard'))


@app.route('/complete_goal/<int:goal_id>')
def complete_goal(goal_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))

    cursor = db.cursor()
    cursor.execute("UPDATE goals SET Status = 'Completed' WHERE Goal_ID = %s", (goal_id,))
    db.commit()
    cursor.close()

    flash("Goal marked as completed!", "success")
    return redirect(url_for('dashboard'))


# ---------------- Recommendations ----------------
@app.route('/recommendations')
def recommendations():
    if not session.get('user_id'):
        return redirect(url_for('login'))

    # Dummy recommendations (you can later connect YouTube API or DB)
    recs = [
        {"title": "Python Basics for Beginners", "link": "https://youtu.be/_uQrJ0TkZlc"},
        {"title": "DSA Made Easy", "link": "https://youtu.be/sVxBVvlnJsM"},
        {"title": "How to Stay Consistent in Studies", "link": "https://youtu.be/ZXsQAXx_ao0"}
    ]

    return render_template('recommendations.html', recs=recs)


# ---------------- Analytics ----------------
@app.route('/analytics')
def analytics():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('analytics.html')


if __name__ == '__main__':
    app.run(debug=True)
