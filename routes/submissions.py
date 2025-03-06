"""Routes for submission handling"""

from config import s3, db
from models.file import File
from models.user import User
from flask import Blueprint, request, render_template, current_app, url_for, jsonify
from flask_login import login_required, current_user
import boto3
from werkzeug.utils import secure_filename
from botocore.exceptions import ClientError
import os
import requests


submissions_blueprint = Blueprint("submissions", __name__)


@submissions_blueprint.route("/upload", methods=["GET", "POST"])
@login_required
def upload_file():
    """Route to handle file uploads"""
    if not current_user.is_authenticated:
        return "User is not authenticated", 401

    if request.method == "POST":
        if "file" not in request.files:
            return "No file part"
        file = request.files["file"]
        if file.filename == "":
            return "No selected file"
        if file:
            try:
                # Secure the filename
                original_filename = secure_filename(file.filename)
                filename = original_filename

                # Check if the filename already exists in the database
                existing_file = File.query.filter_by(filename=filename).first()
                if existing_file:
                    return "A file with this name already exists", 400

                # Create a new File instance and associate it with the current user
                file_instance = File(filename=filename, user_id=current_user.id)
                db.session.add(file_instance)
                db.session.commit()

                # Upload to S3
                s3.upload_fileobj(file, os.getenv("S3_BUCKET_NAME"), filename)
                return "File uploaded successfully"
            except ClientError as e:
                return f"Error uploading file: {e}"
    return render_template("upload.html")


@submissions_blueprint.route("/download/<filename>")
def download_file(filename):
    """Route to handle file downloads"""
    try:
        s3.download_file(os.getenv("S3_BUCKET_NAME"), filename, f"/tmp/{filename}")
        return send_from_directory("/tmp", filename, as_attachment=True)
    except Exception as e:
        return str(e)


@submissions_blueprint.route("/view/<filename>")
def view_file(filename):
    """Route to handle file viewing"""
    try:
        # Get the bucket name from environment variables
        bucket_name = os.getenv("S3_BUCKET_NAME")
        if not bucket_name:
            return "S3 bucket name is not set in environment variables", 500
        # Get the object from the S3 bucket
        obj = s3.get_object(Bucket=bucket_name, Key=filename)
        # Read the file content
        file_content = obj["Body"].read().decode("utf-8")
        # Render the template with the file content
        return render_template("view.html", filename=filename, content=file_content)
    except Exception as e:
        # Return the error message
        return str(e), 500


def get_user_files(user_id: int):
    """Function to return links to all files associated with a user"""
    # Get all files associated with the specified user
    files = File.query.filter_by(user_id=user_id).all()

    # Create a list of file links
    file_links = [
        url_for("submissions.view_file", filename=file.filename, _external=True)
        for file in files
    ]

    # Return the list of file links as JSON
    return jsonify(file_links)


@submissions_blueprint.route("/user/<int:user_id>/files", methods=["GET"])
def get_user_files_route(user_id: int):
    """Route to return links to all files associated with a user"""
    return get_user_files(user_id)


@submissions_blueprint.route("/user/<int:user_id>/files_page", methods=["GET"])
def user_files_page(user_id: int):
    """Route to render the HTML page with file links"""
    try:
        # Call the get_user_files function directly
        file_links = get_user_files(user_id).get_json()
        error_message = ""
    except Exception as e:
        # Handle any exceptions
        file_links = []
        error_message = str(e)

    # Render the HTML template with the file links
    return render_template(
        "user_files.html",
        file_links=file_links,
        user_id=user_id,
        error_message=error_message,
    )
