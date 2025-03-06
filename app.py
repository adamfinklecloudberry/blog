"""A blog where users can post content and upload/download files to/from S3"""

from config import init_app, create_bucket
from routes.home import home_blueprint
from routes.authentication import authentication_blueprint
from routes.submissions import submissions_blueprint
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_from_directory,
)
from dotenv import load_dotenv
import os


# Load environment variables from .env file
load_dotenv()

# Initialize the app
app = Flask(__name__)
init_app(app)

# Register the blueprints
app.register_blueprint(home_blueprint)
app.register_blueprint(authentication_blueprint)
app.register_blueprint(submissions_blueprint)


if __name__ == "__main__":
    # Create the bucket if it doesn't exist
    create_bucket(os.getenv("S3_BUCKET_NAME"))

    # Determine whether the debugger is to be used
    debug = True if os.getenv("BACKEND_DEBUG_MODE") == "True" else False

    # Set the app testing mode to what the debugger is
    app.config["TESTING"] = debug

    # Run the app
    app.run(os.getenv("BACKEND_HOST_ADDRESS"), debug=debug)
