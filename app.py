"""
A blog where users can post content and upload/download files to/from S3

- Defines the main application for a blog where users can post content and
    upload/download files to/from Amazon S3.
- Initializes the Flask application, configures logging, registers blueprints for
    different routes, and handles the creation of an S3 bucket
"""

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
import logging


# Load environment variables from .env file
load_dotenv()

# Configure logging
logging_level = os.getenv("LOGGING_LEVEL", "INFO").upper()
logging.basicConfig(
    level=logging_level,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

# Initialize the app
app = Flask(__name__)
init_app(app)

# Register the blueprints
app.register_blueprint(home_blueprint)
app.register_blueprint(authentication_blueprint)
app.register_blueprint(submissions_blueprint)

logging.info("Application initialized and blueprints registered.")

if __name__ == "__main__":
    # Create the bucket if it doesn't exist
    bucket_name = os.getenv("S3_BUCKET_NAME")
    if bucket_name:
        create_bucket(bucket_name)
        logging.info(f"S3 bucket '{bucket_name}' created or already exists.")
    else:
        logging.error("S3 bucket name not found in environment variables.")

    # Determine whether the debugger is to be used
    debug = True if os.getenv("BACKEND_DEBUG_MODE") == "True" else False

    # Set the app testing mode to what the debugger is
    app.config["TESTING"] = debug

    # Run the app
    host = os.getenv("BACKEND_HOST_ADDRESS", "127.0.0.1")
    port = int(os.getenv("BACKEND_PORT", 5000))
    logging.info(
        f"Starting the application on {host}:{port} with debug mode {'enabled' if debug else 'disabled'}."
    )
    app.run(host=host, port=port, debug=debug)
