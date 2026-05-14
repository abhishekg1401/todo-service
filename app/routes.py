from flask import jsonify, request, render_template_string, redirect, send_file
from app import app
from datetime import datetime
from zoneinfo import ZoneInfo
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import json
import os

DATA_FILE = "/data/todos.json"
IST = ZoneInfo("Asia/Kolkata")


def now_ist():
    return datetime.now(IST)


def date_str():
    return now_ist().strftime("%d-%m-%Y")


def datetime_str():
    return now_ist().strftime("%d-%m-%Y %I:%M:%S %p IST")


def save_todos(todos):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as file:
        json.dump(todos, file, indent=4)


def cleanup_completed_todos(todos):
    today = now_ist().date()
    remaining = []

    for todo in todos:
        completed_at = todo.get("completed_at")

        if todo.get("completed") and completed_at:
            completed_date = datetime.strptime(completed_at, "%d-%m-%Y").date()

            # completed tasks removed from next day
            if today > completed_date:
                continue

        remaining.append(todo)

    return remaining


def normalize_todos(todos):
    changed = False

    for todo in todos:
        if not todo.get("created_at"):
            todo["created_at"] = date_str()
            changed = True

        if "completed_at" not in todo:
            todo["completed_at"] = None
            changed = True

    return todos, changed


def load_todos():
    if not os.path.exists(DATA_FILE):
        default_todos = [
            {
                "id": 1,
                "title": "Learn Docker",
                "completed": False,
                "created_at": date_str(),
                "completed_at": None
            },
            {
                "id": 2,
                "title": "Build Flask microservice",
                "completed": False,
                "created_at": date_str(),
                "completed_at": None
            }
        ]
        save_todos(default_todos)
        return default_todos

    with open(DATA_FILE, "r") as file:
        todos = json.load(file)

    todos, changed = normalize_todos(todos)
    todos = cleanup_completed_todos(todos)

    if changed:
        save_todos(todos)

    return todos


HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Todo List</title>

    <style>
        * {
            box-sizing: border-box;
        }

        html, body {
            min-height: 100%;
        }

        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 40px;
            position: relative;
            overflow-x: hidden;
            background: #000;
        }

        body::before {
            content: "";
            position: fixed;
            inset: 0;
            background-image: url("/static/background.jpg");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            opacity: 0.7;
            z-index: 0;
        }

        .container {
            position: relative;
            z-index: 1;
            max-width: 780px;
            margin: auto;
            background: rgba(255,255,255,0.88);
            padding: 35px;
            border-radius: 18px;
            box-shadow: 0 15px 40px rgba(0,0,0,0.2);
            backdrop-filter: blur(5px);
        }

        h1 {
            text-align: center;
            color: #111827;
            margin-bottom: 25px;
            font-size: 42px;
        }

        .top-actions {
            display: flex;
            justify-content: flex-end;
            margin-bottom: 18px;
        }

        form {
            display: flex;
            gap: 12px;
            margin-bottom: 25px;
        }

        input {
            flex: 1;
            padding: 14px;
            border-radius: 10px;
            border: 1px solid #ccc;
            font-size: 16px;
            outline: none;
        }

        input:focus {
            border-color: #2563eb;
        }

        button, .download-btn {
            padding: 14px 20px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            color: white;
            font-size: 15px;
            text-decoration: none;
            transition: 0.3s ease;
        }

        button:hover, .download-btn:hover {
            transform: scale(1.03);
        }

        .add-btn {
            background: #2563eb;
        }

        .download-btn {
            background: #7c3aed;
        }

        .todo {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 18px;
            margin-bottom: 14px;
            border-radius: 12px;
            background: rgba(255,255,255,0.82);
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }

        .todo-title {
            font-size: 18px;
            color: #111827;
            margin-bottom: 8px;
        }

        .todo-date {
            font-size: 13px;
            color: #4b5563;
        }

        .completed {
            text-decoration: line-through;
            color: #6b7280;
        }

        .actions {
            display: flex;
            gap: 10px;
        }

        .actions form {
            margin-bottom: 0;
        }

        .done-btn {
            background: #16a34a;
        }

        .delete-btn {
            background: #dc2626;
        }

        .empty {
            text-align: center;
            color: #555;
            font-size: 18px;
            margin-top: 20px;
        }

        .footer {
            text-align: center;
            margin-top: 30px;
            color: #333;
            font-size: 14px;
        }
    </style>
</head>

<body>
    <div class="container">
        <h1>Todo List</h1>

        <div class="top-actions">
            <a class="download-btn" href="/download-pdf">Download Tasks PDF</a>
        </div>

        <form method="POST" action="/add">
            <input type="text" name="title" placeholder="Enter your todo..." required>
            <button class="add-btn" type="submit">Add Todo</button>
        </form>

        {% if todos %}
            {% for todo in todos %}
                <div class="todo">
                    <div>
                        <div class="todo-title {{ 'completed' if todo.completed else '' }}">
                            {% if todo.completed %}
                                ✅
                            {% else %}
                                📌
                            {% endif %}
                            {{ todo.title }}
                        </div>

                        <div class="todo-date">
                            Created: {{ todo.created_at }}

                            {% if todo.completed and todo.completed_at %}
                                | Completed: {{ todo.completed_at }}
                            {% endif %}
                        </div>
                    </div>

                    <div class="actions">
                        <form method="POST" action="/toggle/{{ todo.id }}">
                            <button class="done-btn" type="submit">
                                {% if todo.completed %}
                                    Undo
                                {% else %}
                                    Done
                                {% endif %}
                            </button>
                        </form>

                        <form method="POST" action="/delete/{{ todo.id }}">
                            <button class="delete-btn" type="submit">Delete</button>
                        </form>
                    </div>
                </div>
            {% endfor %}
        {% else %}
            <p class="empty">No todos available. Add your first todo 🚀</p>
        {% endif %}

        <div class="footer">
            Personal Todo - Abhishek Ghosh
        </div>
    </div>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def home():
    todos = load_todos()
    return render_template_string(HTML, todos=todos)


@app.route("/add", methods=["POST"])
def add_todo_ui():
    todos = load_todos()
    title = request.form.get("title")

    if title:
        new_id = max([todo["id"] for todo in todos], default=0) + 1

        todos.append({
            "id": new_id,
            "title": title,
            "completed": False,
            "created_at": date_str(),
            "completed_at": None
        })

        save_todos(todos)

    return redirect("/")


@app.route("/toggle/<int:todo_id>", methods=["POST"])
def toggle_todo(todo_id):
    todos = load_todos()

    for todo in todos:
        if todo["id"] == todo_id:
            todo["completed"] = not todo["completed"]
            todo["completed_at"] = date_str() if todo["completed"] else None
            break

    save_todos(todos)
    return redirect("/")


@app.route("/delete/<int:todo_id>", methods=["POST"])
def delete_todo_ui(todo_id):
    todos = load_todos()
    todos = [todo for todo in todos if todo["id"] != todo_id]
    save_todos(todos)

    return redirect("/")


@app.route("/download-pdf", methods=["GET"])
def download_pdf():
    todos = load_todos()

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4
    y = height - 50

    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(50, y, "Todo List Report")

    y -= 35
    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, y, f"Generated on: {datetime_str()}")

    y -= 40

    if not todos:
        pdf.drawString(50, y, "No tasks available.")
    else:
        for index, todo in enumerate(todos, start=1):
            if y < 90:
                pdf.showPage()
                y = height - 50

            status = "Done" if todo.get("completed") else "Pending"

            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(50, y, f"{index}. {todo.get('title')}")

            y -= 18
            pdf.setFont("Helvetica", 10)
            pdf.drawString(70, y, f"Created Date: {todo.get('created_at', '-')}")

            y -= 15
            pdf.drawString(70, y, f"Status: {status}")

            if todo.get("completed_at"):
                y -= 15
                pdf.drawString(70, y, f"Completed Date: {todo.get('completed_at')}")

            y -= 28

    pdf.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="todo-list.pdf",
        mimetype="application/pdf"
    )


@app.route("/todos", methods=["GET"])
def get_todos():
    return jsonify({"todos": load_todos()}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200