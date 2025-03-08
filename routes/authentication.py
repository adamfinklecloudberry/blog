"""
Routes for user authentication

- Defines the routes and functionality for user authentication in a Flask application.
- Includes routes for user registration, login, and logout, as well as the necessary user
    loader function for Flask-Login
- Uses Flask-Login for session management and user authentication, and SQLAlchemy for
    database interactions
- Handles user registration by processing form data, hashing passwords, and storing
    user information in the database
- Also handles user login by authenticating users based on their email and password,
    and user logout by invalidating the user's session
"""

from blog.config import login_manager, db
from blog.models.user import User
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash


authentication_blueprint = Blueprint("authentication", __name__)


@login_manager.user_loader
def load_user(user_id):
    """
    Load a user from the database using the user ID.

    This function is used by Flask-Login to reload the user object from the
    user ID stored in the session.

    Args:
        user_id (int): The ID of the user to load.

    Returns:
        User: The user object if found, otherwise None.
    """
    return User.query.get(int(user_id))


@authentication_blueprint.route("/register", methods=["GET", "POST"])
def register():
    """
    Handle user registration.

    This route handles both GET and POST requests. For GET requests, it renders
    the registration form. For POST requests, it processes the form data to
    create a new user in the database.

    Returns:
        str: The rendered registration template for GET requests, or a redirect
             to the login page for successful POST requests.
    """
    if request.method == "POST":
        try:
            username = request.form.get("username")
            email = request.form.get("email")
            password = request.form.get("password")
            hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
            new_user = User(username=username, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful!", "success")
            return redirect(url_for("authentication.login"))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash("Registration failed. Please try again.", "danger")
            return render_template("register.html", error=str(e))
    return render_template("register.html")


@authentication_blueprint.route("/login", methods=["GET", "POST"])
def login():
    """
    Handle user login.

    This route handles both GET and POST requests. For GET requests, it renders
    the login form. For POST requests, it processes the form data to authenticate
    the user and log them in.

    Returns:
        str: The rendered login template for GET requests, or a redirect to the
             home page for successful POST requests.
    """
    if request.method == "POST":
        try:
            email = request.form.get("email")
            password = request.form.get("password")
            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                flash("You have been logged in!", "success")
                return redirect(url_for("home.home"))
            else:
                flash("Login Unsuccessful. Please check email and password", "danger")
        except SQLAlchemyError as e:
            flash("Login failed. Please try again.", "danger")
            return render_template("login.html", error=str(e))
    return render_template("login.html")


@authentication_blueprint.route("/logout")
@login_required
def logout():
    """
    Handle user logout.

    This route logs out the currently logged-in user and redirects them to the
    login page.

    Returns:
        str: A redirect to the login page.
    """
    try:
        logout_user()
        flash("You have been logged out.", "success")
        return redirect(url_for("authentication.login"))
    except Exception as e:
        flash("Logout failed. Please try again.", "danger")
        return redirect(url_for("authentication.login"))
