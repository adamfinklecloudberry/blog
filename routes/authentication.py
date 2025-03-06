"""Routes for user authentication"""

from config import login_manager, db
from models.user import User
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash


authentication_blueprint = Blueprint("authentication", __name__)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@authentication_blueprint.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful!", "success")
        return redirect(url_for("authentication.login"))
    return render_template("register.html")


@authentication_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("You have been logged in!", "success")
            return redirect(url_for("home.home"))
        else:
            flash("Login Unsuccessful. Please check email and password", "danger")
    return render_template("login.html")


@authentication_blueprint.route("/logout")
@login_required
def logout():
    """Route to handle user logout"""
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("authentication.login"))
