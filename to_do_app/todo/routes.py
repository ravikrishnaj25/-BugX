from flask import Blueprint, render_template, request, redirect
from .storage import load_tasks, save_tasks

todo_bp = Blueprint("todo", __name__)

@todo_bp.route("/")
def index():
    tasks = load_tasks()
    return render_template("index.html", tasks=tasks)

@todo_bp.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        tasks = load_tasks()
        new_task = {
            "title": request.form["title"],
            "done": False
        }
        tasks.append(new_task)
        save_tasks(tasks)
        return redirect("/")
    return render_template("add.html")

@todo_bp.route("/done/<int:task_id>")
def mark_done(task_id):
    tasks = load_tasks()
    tasks[task_id]["done"] = True
    save_tasks(tasks)
    return redirect("/")
