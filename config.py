"""
Configuration for the app

- Provides the configuration settings and initialization functions for a Flask
    application
- Includes configurations for the database, login manager, and S3 client
"""

import boto3
from botocore.client import Config
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import secrets
import os


# Initialize the LoginManager
login_manager = LoginManager()
login_manager.login_view = "authentication.login"

# Initialize the database
db = SQLAlchemy()

# Configure S3 client
if os.getenv("BACKEND_DEBUG_MODE") == "True":
    s3 = boto3.client(
        "s3",
        endpoint_url=os.getenv("LOCALSTACK_ENDPOINT"),
        config=Config(signature_version="s3v4"),
    )
else:
    s3 = boto3.client(
        "s3",
        region_name=os.getenv("AWS_REGION"),
    )


def init_app(app):
    """
    Initializes the Flask application with the necessary configurations and settings

    - Sets up the Flask application by configuring the secret key, testing mode, login
        manager, database URI, and initializing the SQLAlchemy object.
    - Also creates the database and tables if they do not exist

    Args:
        app (Flask): The Flask application instance to be initialized.
    """
    # Set the secret key
    app.secret_key = secrets.token_hex(32)

    # Setup testing mode
    app.config["TESTING"] = os.getenv("BACKEND_DEBUG_MODE") == "True"

    # Initialize login
    login_manager.init_app(app)

    # Configure the app
    if app.config["TESTING"] == True:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
            os.path.dirname(__file__), "test.db"
        )
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")

    # Don't track modifications
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize the SQLAlchemy object
    db.init_app(app)

    # Create the database and tables
    with app.app_context():
        db.create_all()
        print("Database initialized and tables created.")


def create_bucket(bucket_name: str):
    """
    Creates an S3 bucket with the specified name

    - Attempts to create an S3 bucket using the provided bucket name
    - Handles various exceptions, including client errors and credential errors, and
        prints appropriate messages

    Args:
        bucket_name (str): the name of the S3 bucket to create
            The bucket name must be unique across all existing bucket names in Amazon
            S3.
    """
    try:
        s3.create_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} created successfully.")
    except ClientError as e:
        print(f"Error creating bucket {bucket_name}: {e}")
    except (NoCredentialsError, PartialCredentialsError) as e:
        print(f"Credentials error: {e}")
