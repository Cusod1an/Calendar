import calendar
import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import MaintenanceTask, Equipment, User
from app import db, socketio  # імпортуємо глобальний socketio
from app.decorators import login_required

bp = Blueprint("maintenance", __name__)

@bp.route("/", methods=["GET"])
def index():
    today = datetime.date.today()
    default_year = today.year
    default_month = today.month

    try:
        year = int(request.args.get("year", default_year))
        month = int(request.args.get("month", default_month))
    except ValueError:
        year, month = default_year, default_month

    if month < 1 or month > 12:
        month = default_month

    cal = calendar.monthcalendar(year, month)
    tasks = MaintenanceTask.query.filter_by(status="pending").order_by(MaintenanceTask.date_scheduled.asc()).all()
    tasks_by_date = {}
    for task in tasks:
        date_str = task.date_scheduled.strftime("%Y-%m-%d")
        tasks_by_date.setdefault(date_str, []).append(task)

    month_names = {
        1: "Січень", 2: "Лютий", 3: "Березень", 4: "Квітень", 5: "Травень",
        6: "Червень", 7: "Липень", 8: "Серпень", 9: "Вересень", 10: "Жовтень",
        11: "Листопад", 12: "Грудень"
    }
    month_name = month_names.get(month, str(month))
    current_year = default_year

    return render_template("maintenance/index.html", cal=cal, year=year, month=month,
                           month_name=month_name, tasks_by_date=tasks_by_date, current_year=current_year)

@bp.route("/create", methods=["GET", "POST"])
@login_required
def create_task():
    equipments = Equipment.query.all()
    statuses = [("pending", "Очікується"), ("completed", "Виконано"), ("overdue", "Просрочено")]
    if request.method == "POST":
        data = request.form
        try:
            # Перевірка дати: дата планування не повинна бути до сьогоднішньої
            date_scheduled = datetime.datetime.strptime(data["date_scheduled"], "%Y-%m-%d").date()
            today = datetime.date.today()
            if date_scheduled < today:
                flash("Дата завдання не може бути раніше сьогоднішньої.", "danger")
                return redirect(url_for("maintenance.create_task"))

            user_id = data.get("user_id")
            if not user_id or user_id.strip() == "":
                user_id = None
            else:
                user_id = int(user_id)
            equipment_id = int(data.get("equipment_id"))

            new_task = MaintenanceTask(
                equipment_id=equipment_id,
                title=data["title"],
                description=data.get("description", ""),
                date_scheduled=date_scheduled,
                status=data.get("status", "pending").lower(),
                user_id=user_id
            )
            db.session.add(new_task)
            equipment = Equipment.query.get(equipment_id)
            equipment.busy = True
            db.session.commit()
            flash(f"Завдання створено успішно! ID завдання: {new_task.id}", "success")
            # Посилаємо повідомлення всім клієнтам, що завдання оновлено
            socketio.emit("tasks_updated", {"msg": "New task created"}, broadcast=True)
        except Exception as e:
            db.session.rollback()
            flash(f"Помилка: {str(e)}", "danger")
        return redirect(url_for("maintenance.index"))
    return render_template("maintenance/create.html", equipments=equipments, statuses=statuses)

@bp.route("/edit/<int:task_id>", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = MaintenanceTask.query.get_or_404(task_id)
    statuses = [("pending", "Очікується"), ("completed", "Виконано"), ("overdue", "Просрочено")]
    if request.method == "POST":
        data = request.form
        try:
            task.title = data["title"]
            task.description = data.get("description", "")
            task.date_scheduled = datetime.datetime.strptime(data["date_scheduled"], "%Y-%m-%d").date()
            new_status = data.get("status", "pending").lower()
            if new_status == "completed":
                task.status = "completed"
                task.user_id = None
                if task.equipment:
                    task.equipment.busy = False
            elif new_status == "overdue":
                if task.equipment:
                    task.equipment.busy = False
                db.session.delete(task)
                db.session.commit()
                flash("Просрочене завдання видалено.", "warning")
                socketio.emit("tasks_updated", {"msg": "Task deleted"}, broadcast=True)
                return redirect(url_for("maintenance.index"))
            else:
                task.status = new_status
            db.session.commit()
            flash(f"Завдання оновлено успішно! (ID: {task.id})", "success")
            socketio.emit("tasks_updated", {"msg": "Task updated"}, broadcast=True)
        except Exception as e:
            db.session.rollback()
            flash(f"Помилка: {str(e)}", "danger")
        return redirect(url_for("maintenance.index"))
    return render_template("maintenance/edit.html", task=task, statuses=statuses)

@bp.route("/test_emit")
def test_emit():
    socketio.emit("tasks_updated", {"msg": "Test update"}, broadcast=True)
    return "Emit test sent"

@bp.route("/view/<int:task_id>", methods=["GET"])
def view_task(task_id):
    task = MaintenanceTask.query.get_or_404(task_id)
    return render_template("maintenance/view.html", task=task)

@bp.route("/refresh", methods=["GET"])
def refresh_calendar():
    import calendar
    import datetime
    today = datetime.date.today()
    default_year = today.year
    default_month = today.month

    try:
        year = int(request.args.get("year", default_year))
        month = int(request.args.get("month", default_month))
    except ValueError:
        year, month = default_year, default_month

    if month < 1 or month > 12:
        month = default_month

    cal = calendar.monthcalendar(year, month)
    tasks = MaintenanceTask.query.filter_by(status="pending").order_by(MaintenanceTask.date_scheduled.asc()).all()
    tasks_by_date = {}
    for task in tasks:
        date_str = task.date_scheduled.strftime("%Y-%m-%d")
        tasks_by_date.setdefault(date_str, []).append(task)

    month_names = {
        1: "Січень", 2: "Лютий", 3: "Березень", 4: "Квітень", 5: "Травень",
        6: "Червень", 7: "Липень", 8: "Серпень", 9: "Вересень", 10: "Жовтень",
        11: "Листопад", 12: "Грудень"
    }
    month_name = month_names.get(month, str(month))
    current_year = default_year

    # Рендеримо частковий шаблон із календарем
    return render_template(
        "maintenance/calendar_partial.html",
        cal=cal,
        year=year,
        month=month,
        month_name=month_name,
        tasks_by_date=tasks_by_date
    )

@bp.route("/api/events", methods=["GET"])
def get_events():
    tasks = MaintenanceTask.query.filter_by(status="pending").order_by(MaintenanceTask.date_scheduled.asc()).all()
    events = []
    for task in tasks:
        events.append({
            "id": task.id,
            "title": task.title,
            "start": task.date_scheduled.strftime("%Y-%m-%d"),
            "end": task.date_completed.strftime("%Y-%m-%d") if task.date_completed else None
        })
    return jsonify(events)
