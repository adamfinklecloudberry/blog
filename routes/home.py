"""
The home route

- Defines the home route for a Flask application
"""

from flask import Blueprint, render_template
import logging


home_blueprint = Blueprint("home", __name__)


@home_blueprint.route("/")
def home():
    """Main page of the blog"""
    logging.info("Home route accessed")
    return render_template("index.html")
