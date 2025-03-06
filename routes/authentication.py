"""Routes for user authentication"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from models.user import User
from extensions import bcrypt
from config import db


authentication_blueprint = Blueprint("authentication", __name__)


@authentication_blueprint.route("/register", methods=["GET", "POST"])
def register():
    """Route to handle user registration"""
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Your account has been created! You can now log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")


@authentication_blueprint.route("/login", methods=["GET", "POST"])
def login():
    """Route to handle user login"""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            flash("You have been logged in!", "success")
            return redirect(url_for("home.home"))
        else:
            flash("Login Unsuccessful. Please check email and password", "danger")
    return render_template("login.html")
