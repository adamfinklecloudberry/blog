"""The home route"""

from flask import Blueprint, render_template


home_blueprint = Blueprint("home", __name__)


@home_blueprint.route("/")
def home():
    """Main page of the blog"""
    return render_template("index.html")
