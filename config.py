"""Configuration for the app"""

import boto3
from botocore.client import Config
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from flask_sqlalchemy import SQLAlchemy
import secrets
import os


# Initialize the database
db = SQLAlchemy()

# Configure S3 client
if os.getenv("BACKEND_DEBUG_MODE") == "True":
    s3 = boto3.client(
        "s3",
        # aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        # aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        endpoint_url=os.getenv("LOCALSTACK_ENDPOINT"),
        config=Config(signature_version="s3v4"),
        # region_name=os.getenv("AWS_REGION"),
    )
else:
    s3 = boto3.client(
        "s3",
        # aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        # aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION"),
    )


def init_app(app):
    """Initializes the app"""
    # Set the secret key
    app.secret_key = secrets.token_hex(32)

    # Setup testing mode
    app.config["TESTING"] = os.getenv("BACKEND_DEBUG_MODE") == "True"

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
    """Creates a bucket of this name"""
    try:
        s3.create_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} created successfully.")
    except ClientError as e:
        print(f"Error creating bucket {bucket_name}: {e}")
    except (NoCredentialsError, PartialCredentialsError) as e:
        print(f"Credentials error: {e}")
