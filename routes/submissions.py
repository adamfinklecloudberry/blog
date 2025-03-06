"""Routes for submission handling"""

from config import s3
from flask import Blueprint, request, render_template
from botocore.exceptions import ClientError
import os


submissions_blueprint = Blueprint("submissions", __name__)


@submissions_blueprint.route("/upload", methods=["GET", "POST"])
def upload_file():
    """Route to handle file uploads"""
    if request.method == "POST":
        if "file" not in request.files:
            return "No file part"
        file = request.files["file"]
        if file.filename == "":
            return "No selected file"
        if file:
            try:
                s3.upload_fileobj(file, os.getenv("S3_BUCKET_NAME"), file.filename)
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
        obj = s3.get_object(Bucket=os.getenv("S3_BUCKET_NAME"), Key=filename)
        file_content = obj["Body"].read().decode("utf-8")
        return render_template("view.html", filename=filename, content=file_content)
    except Exception as e:
        return str(e)
