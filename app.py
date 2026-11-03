from flask import Flask, render_template, request
import sqlite3
from pathlib import Path
from predictor import predict_performance, recommend_study

app = Flask(__name__)
DB_PATH = Path(__file__).with_name("students.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                study_hours REAL,
                attendance REAL,
                previous_marks REAL,
                assignment_completion REAL,
                predicted_marks REAL,
                recommendation TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None

    if request.method == "POST":
        try:
            name = request.form["name"].strip()
            hours = float(request.form["study_hours"])
            attendance = float(request.form["attendance"])
            marks = float(request.form["previous_marks"])
            assignments = float(request.form["assignment_completion"])

            if not name:
                raise ValueError("Enter student name")
            if not 0 <= hours <= 24:
                raise ValueError("Study hours must be between 0 and 24")

            if any(not 0 <= x <= 100 for x in [attendance, marks, assignments]):
                raise ValueError("Percentage must be between 0 and 100")

            predicted = predict_performance(hours, attendance, marks, assignments)
            recommendation = recommend_study(hours, attendance, marks, assignments)

            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("""
                    INSERT INTO predictions
                    (name, study_hours, attendance, previous_marks,
                    assignment_completion, predicted_marks, recommendation)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (name, hours, attendance, marks, assignments,
                      predicted, recommendation))

            result = {
                "name": name,
                "predicted": predicted,
                "recommendation": recommendation
            }

        except (ValueError, KeyError) as e:
            error = str(e)

    with sqlite3.connect(DB_PATH) as conn:
        recent = conn.execute("""
            SELECT name, predicted_marks, created_at
            FROM predictions ORDER BY id DESC LIMIT 5
        """).fetchall()

    return render_template("index.html", result=result,
                           error=error, recent=recent)

@app.route("/history")
def history():
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("""
            SELECT * FROM predictions ORDER BY id DESC
        """).fetchall()

    return render_template("history.html", rows=rows)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
