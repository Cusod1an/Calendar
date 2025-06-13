# app/controllers/equipment_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Equipment
from app import db
from app.decorators import login_required  # імпортуємо декоратор

bp = Blueprint("equipment", __name__)

@bp.route("/", methods=["GET"])
def list_equipment():
    equipments = Equipment.query.all()
    return render_template("equipment/index.html", equipments=equipments)

# Додавання нового обладнання потребує авторизації
@bp.route("/create", methods=["GET", "POST"])
@login_required
def create_equipment():
    if request.method == "POST":
        data = request.form
        try:
            new_equipment = Equipment(
                name=data["name"],
                location=data.get("location", ""),
                model=data.get("model", "")
            )
            db.session.add(new_equipment)
            db.session.commit()
            flash(f"Обладнання додано успішно! ID: {new_equipment.id}", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Помилка при додаванні обладнання: {str(e)}", "danger")
        return redirect(url_for("equipment.list_equipment"))
    return render_template("equipment/create.html")
