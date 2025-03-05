"""A blog where users can post content and upload/download files to/from S3"""

from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from dotenv import load_dotenv
import os
import boto3
from botocore.client import Config
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Configure S3 client
if os.getenv("BACKEND_DEBUG_MODE") == "True":
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        endpoint_url=os.getenv("LOCALSTACK_ENDPOINT"),
        config=Config(signature_version='s3v4'),
        region_name=os.getenv("AWS_REGION")
    )
else:
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION")
    )

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

def create_bucket(bucket_name):
    try:
        s3.create_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} created successfully.")
    except ClientError as e:
        print(f"Error creating bucket {bucket_name}: {e}")
    except (NoCredentialsError, PartialCredentialsError) as e:
        print(f"Credentials error: {e}")

@app.route("/")
def home():
    """Main page of the blog"""
    return render_template("index.html")

@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    """Route to handle file uploads"""
    if request.method == "POST":
        if 'file' not in request.files:
            return "No file part"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
        if file:
            try:
                s3.upload_fileobj(file, BUCKET_NAME, file.filename)
                return "File uploaded successfully"
            except ClientError as e:
                return f"Error uploading file: {e}"
    return render_template("upload.html")

@app.route("/download/<filename>")
def download_file(filename):
    """Route to handle file downloads"""
    try:
        s3.download_file(BUCKET_NAME, filename, f"/tmp/{filename}")
        return send_from_directory("/tmp", filename, as_attachment=True)
    except Exception as e:
        return str(e)

@app.route("/view/<filename>")
def view_file(filename):
    """Route to handle file viewing"""
    try:
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=filename)
        file_content = obj['Body'].read().decode('utf-8')
        return render_template("view.html", filename=filename, content=file_content)
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    # Create the bucket if it doesn't exist
    create_bucket(BUCKET_NAME)
    debug = True if os.getenv("BACKEND_DEBUG_MODE") == "True" else False
    app.run(os.getenv("BACKEND_HOST_ADDRESS"), debug=debug)
