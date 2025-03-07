"""Routes for submission handling"""

from config import s3, db
from models.file import File
from models.user import User
from flask import (
    Blueprint,
    request,
    render_template,
    current_app,
    url_for,
    jsonify,
    send_from_directory,
    redirect,
)
from flask_login import login_required, current_user
import boto3
from werkzeug.utils import secure_filename
from botocore.exceptions import ClientError
import os
import requests


submissions_blueprint = Blueprint("submissions", __name__)


"""Routes for submission handling"""

from config import s3, db
from models.file import File
from models.user import User
from flask import (
    Blueprint,
    request,
    render_template,
    current_app,
    url_for,
    jsonify,
    send_from_directory,
)
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
    if request.method == "POST":
        if "file" not in request.files:
            return "No file part"
        file = request.files["file"]
        if file.filename == "":
            return "No selected file"
        if file:
            # Check if the file has a .txt extension
            if not file.filename.lower().endswith(".txt"):
                return "Only .txt files are allowed", 400

            try:
                # Secure the filename
                original_filename = secure_filename(file.filename)
                filename = f"{current_user.username}/{original_filename}"

                # Check if the file already exists for the user
                existing_file = File.query.filter_by(
                    user_id=current_user.id, filename=original_filename
                ).first()
                if existing_file:
                    return "File with the same name already exists", 400

                # Create a new File instance and associate it with the current user
                file_instance = File(
                    filename=original_filename, user_id=current_user.id
                )
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


@submissions_blueprint.route("/blog/<username>")
def user_files(username):
    # Query the database for the user
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404, description="User not found")

    # Query the database for files associated with the user
    files = File.query.filter_by(user_id=user.id).all()

    # Create a list of file links without the .txt extension
    file_links = [
        f'/blog/{username}/{file.filename.rsplit(".", 1)[0]}' for file in files
    ]

    # Render the template with the file links
    return render_template(
        "user_files.html", user=user.username, file_links=file_links, error_message=None
    )


@submissions_blueprint.route("/blog/<username>/<filename>")
def get_file(username: str, filename: str):
    user = User.query.filter_by(username=username).first()
    if not user:
        return "User not found", 404

    # Generate the S3 key
    s3_key = f"{username}/{filename}.txt"

    try:
        # Get the object from the S3 bucket
        obj = s3.get_object(Bucket=os.getenv("S3_BUCKET_NAME"), Key=s3_key)
        # Read the file content
        file_content = obj["Body"].read().decode("utf-8")
        # Render the template with the file content
        return render_template("view.html", filename=filename, content=file_content)
    except Exception as e:
        return f"Error fetching file: {e}", 500
