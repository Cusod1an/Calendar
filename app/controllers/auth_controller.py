# app/controllers/auth_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session

bp = Blueprint("auth", __name__)

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # Приклад простої автентифікації: логін admin/admin
        if username == "admin" and password == "admin":
            session["user_id"] = 1  # заносимо примірний ідентифікатор користувача
            flash("Ви успішно увійшли в систему.", "success")
            return redirect(url_for("maintenance.index"))
        flash("Неправильний логін або пароль.", "danger")
    return render_template("auth/login.html")

@bp.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Ви вийшли з системи.", "success")
    return redirect(url_for("maintenance.index"))
