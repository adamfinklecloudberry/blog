"""A blog where users can post content"""

from flask import Flask, render_template
from dotenv import load_dotenv
import os


app = Flask(__name__)


@app.route("/")
def home():
    """Main page of the blog"""
    return render_template("index.html")


if __name__ == "__main__":
    load_dotenv()
    debug = True if os.getenv("BACKEND_DEBUG_MODE") == "True" else False
    app.run(os.getenv("BACKEND_HOST_ADDRESS"), debug=debug)
