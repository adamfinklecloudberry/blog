"""
Routes for submission handling

Defines the routes for handling file submissions, downloads, and viewing user files in
a blog application. It includes routes for uploading files, downloading files,
displaying a list of files for a specific user, and retrieving the content of a
specific file.
"""

from blog.config import s3, db
from blog.models.file import File
from blog.models.user import User
from flask import (
    Blueprint,
    request,
    render_template,
    current_app,
    flash,
    url_for,
    jsonify,
    send_from_directory,
    redirect,
    abort,
)
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
import boto3
from werkzeug.utils import secure_filename
from botocore.exceptions import ClientError
import requests
import os
import logging


submissions_blueprint = Blueprint("submissions", __name__)

# Initialize logger
logger = logging.getLogger(__name__)


@submissions_blueprint.route("/upload", methods=["GET", "POST"])
@login_required
def upload_file():
    """
    Route to handle file uploads

    = Allows authenticated users to upload .txt files.
    - Handles both GET and POST requests

    GET Request:
        - Renders the upload form.

    POST Request:
        - Validates the uploaded file
        - Checks if the file has a .txt extension
        - Ensures the file does not already exist for the user
        - Secures the filename
        - Creates a new File instance in the database
        - Uploads the file to an S3 bucket
        - Provides feedback to the user via flash messages

    Parameters:
        None

    Returns:
        render_template("upload.html"): Renders the upload form for GET requests.
        redirect(url_for("submissions.upload_file")): Redirects to the upload form
            with appropriate flash messages for POST requests.

    Raises:
        SQLAlchemyError: If there is an error interacting with the database.
        ClientError: If there is an error uploading the file to S3.
    """
    logger.info("File upload route accessed")

    if request.method == "POST":
        logger.info("Handling POST request for file upload")

        if "file" not in request.files:
            logger.warning("No file part in the request")
            flash("No file part", "danger")
            return redirect(url_for("submissions.upload_file"))

        file = request.files["file"]
        if file.filename == "":
            logger.warning("No selected file")
            flash("No selected file", "danger")
            return redirect(url_for("submissions.upload_file"))

        if file:
            # Check if the file has a .txt extension
            if not file.filename.lower().endswith(".txt"):
                logger.warning("File does not have a .txt extension")
                flash("Only .txt files are allowed", "danger")
                return redirect(url_for("submissions.upload_file"))

            try:
                # Secure the filename
                original_filename = secure_filename(file.filename)
                filename = f"{current_user.username}/{original_filename}"
                logger.info(f"Secure filename: {filename}")

                # Check if the file already exists for the user
                existing_file = File.query.filter_by(
                    user_id=current_user.id, filename=original_filename
                ).first()
                if existing_file:
                    logger.warning(
                        "A file with the same name already exists for the user"
                    )
                    flash("A blog post with the same name already exists.", "danger")
                    return redirect(url_for("submissions.upload_file"))

                # Create a new File instance and associate it with the current user
                file_instance = File(
                    filename=original_filename, user_id=current_user.id
                )
                db.session.add(file_instance)
                db.session.commit()
                logger.info("File instance created and committed to the database")

                # Upload to S3
                s3.upload_fileobj(file, os.getenv("S3_BUCKET_NAME"), filename)
                logger.info("File uploaded to S3 successfully")
                flash("Blog post uploaded successfully", "success")
                return redirect(url_for("submissions.upload_file"))
            except (SQLAlchemyError, ClientError) as e:
                logger.error(f"Error uploading file: {e}")
                flash("Error uploading file: Database error", "danger")
                return redirect(url_for("submissions.upload_file"))
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                flash("An unexpected error occurred. Please try again later.", "danger")
                return redirect(url_for("submissions.upload_file"))
    else:
        logger.info("Handling GET request for file upload")
    return render_template("upload.html")


@submissions_blueprint.route("/download/<username>/<postname>")
def download_file(username, postname):
    """
    Route to handle file downloads

    - Allows users to download .txt files from an S3 bucket
    - Constructs the filename and S3 key based on the provided username and postname,
    downloads the file from S3 to a temporary location, and serves it for download

    Parameters:
        username (str): username of the user who uploaded the file
        postname (str): name of the post (file) to be downloaded

    Returns:
        send_from_directory("/tmp", filename, as_attachment=True): Serves the file for
            download from the temporary directory

    Raises:
        Exception: If there is an error downloading the file from S3 or serving the
            file for download
    """
    logger.info(f"Download request for user: {username}, post: {postname}")

    try:
        # Create a filename with a .txt attached
        filename = f"{postname}.txt"
        logger.info(f"Constructed filename: {filename}")

        # Construct the S3 key using the username and filename
        s3_key = f"{username}/{filename}"
        logger.info(f"Constructed S3 key: {s3_key}")

        # Download the file from S3 to a temporary location
        s3.download_file(os.getenv("S3_BUCKET_NAME"), s3_key, f"/tmp/{filename}")
        logger.info(f"File downloaded from S3 to /tmp/{filename}")

        # Serve the file for download
        return send_from_directory("/tmp", filename, as_attachment=True)
    except Exception as e:
        # Handle any exceptions and return an error message
        logger.error(f"Error downloading file: {e}")
        abort(500, description=str(e))


@submissions_blueprint.route("/blog/<username>")
def user_files(username):
    """
    Route to display files associated with a specific user

    - Allows users to view a list of files (blog posts) associated with a specific user
    - Queries the database for the user and their files, generates file links, and
        renders a template to display the information

    Parameters:
        username (str): The username of the user whose files are to be displayed.

    Returns:
        render_template(
                "user_files.html",
                user=user.username,
                file_links=file_links,
                error_message=None
        ): Renders the user_files.html template with the user's files and no error
            message if successful.
        render_template(
                "user_files.html",
                user=username,
                file_links=[],
                error_message="Database error occurred"
        ), 500: Renders the user_files.html template with an error message and an empty
            list of file links if a database error occurs.

    Raises:
        SQLAlchemyError: If there is an error interacting with the database
        404: If the user is not found in the database
    """
    logger.info(f"User files request for username: {username}")

    try:
        # Query the database for the user
        user = User.query.filter_by(username=username).first()
        if not user:
            logger.warning(f"User not found: {username}")
            abort(404, description="User not found")

        # Query the database for files associated with the user
        files = File.query.filter_by(user_id=user.id).all()
        logger.info(f"Retrieved {len(files)} files for user: {username}")

        # Create a list of file links without the .txt extension
        file_links = [
            f'/blog/{username}/{file.filename.rsplit(".", 1)[0]}' for file in files
        ]
        logger.info(f"Generated file links: {file_links}")

        # Render the template with the file links
        return render_template(
            "user_files.html",
            user=user.username,
            file_links=file_links,
            error_message=None,
        )
    except SQLAlchemyError as e:
        # Handle database errors
        logger.error(f"Database error occurred: {e}")
        return (
            render_template(
                "user_files.html",
                user=username,
                file_links=[],
                error_message="Database error occurred",
            ),
            500,
        )


@submissions_blueprint.route("/blog/<username>/<filename>")
def get_file(username: str, filename: str):
    """
    Route to retrieve and display the content of a specific file for a user

    - Allows users to view the content of a specific file (blog post)
    associated with a user
    - Queries the database for the user, generates the S3 key, retrieves the file
        content from the S3 bucket, and renders a template to display the content

    Parameters:
        username (str): The username of the user whose file is to be retrieved.
        filename (str): The name of the file to be retrieved.

    Returns:
        render_template("view.html", filename=filename, content=file_content):
            Renders the view.html template with the file content if successful
        render_template(
                "error.html",
                error_title="User Not Found",
                error_message="The specified user does not exist.",
                url_for=url_for
        ): Renders the error.html template with a user not found message if the user is
            not found
        render_template(
                "error.html",
                error_title="S3 Error",
                error_message="There was an error fetching the file from S3.",
                url_for=url_for
        ), 500: Renders the error.html template with an S3 error message and a 500
            status code if an S3-specific error occurs
        render_template(
            "error.html",
            error_title="Unexpected Error",
            error_message="An unexpected error occurred.",
            url_for=url_for
        ), 500: Renders the error.html template with a generic error message and a 500
            status code if an unexpected error occurs

    Raises:
        ClientError: If there is an error interacting with the S3 bucket.
        Exception: If there is an unexpected error.
    """
    logger.info(f"Request to get file for user: {username}, filename: {filename}")

    # Query the database for the user
    user = User.query.filter_by(username=username).first()
    if not user:
        logger.warning(f"User not found: {username}")
        return render_template(
            "error.html",
            error_title="User Not Found",
            error_message="The specified user does not exist.",
            url_for=url_for,
        )

    # Generate the S3 key
    s3_key = f"{username}/{filename}.txt"
    if os.getenv("ENVIRONMENT") in ["development", "staging"]:
        logger.info(f"Generated S3 key: {s3_key}")

    try:
        # Get the object from the S3 bucket
        obj = s3.get_object(Bucket=os.getenv("S3_BUCKET_NAME"), Key=s3_key)
        # Read the file content
        file_content = obj["Body"].read().decode("utf-8")
        if os.getenv("ENVIRONMENT") in ["development", "staging"]:
            logger.info(f"Successfully retrieved file content for {s3_key}")
        # Render the template with the file content
        return render_template("view.html", filename=filename, content=file_content)
    except ClientError as e:
        # Handle S3-specific errors
        logger.error(f"S3 error occurred: {e}")
        return (
            render_template(
                "error.html",
                error_title="S3 Error",
                error_message="There was an error fetching the file from S3.",
                url_for=url_for,
            ),
            500,
        )
    except Exception as e:
        # Handle any other exceptions
        logger.error(f"Unexpected error occurred: {e}")
        return (
            render_template(
                "error.html",
                error_title="Unexpected Error",
                error_message="An unexpected error occurred.",
                url_for=url_for,
            ),
            500,
        )
