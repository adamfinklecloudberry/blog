from blog.config import db, s3
from blog.app import app
from blog.models.user import User
from blog.models.file import File
import pytest
from flask import url_for
from unittest.mock import patch
from io import BytesIO


@pytest.fixture
def client():
    """
    Fixture to set up a test client and database for the Flask application.

    This fixture configures the Flask app for testing, creates an in-memory SQLite database,
    and sets up the test client. It also ensures that the database is dropped after the tests.

    Yields:
        client: The test client for the Flask application.
    """
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["S3_BUCKET_NAME"] = "test-bucket"
    app.config["SERVER_NAME"] = "localhost"
    app.config["APPLICATION_ROOT"] = "/"

    with app.test_client() as client:
        with app.app_context():
            print("Setting up the test client and database")
            db.create_all()
            yield client
            db.drop_all()
            print("Tearing down the test client and database")


@pytest.fixture
def user():
    """
    Fixture to create a test user.

    This fixture creates a test user with a username, email, and password,
    and adds the user to the database.

    Returns:
        User: The created test user.
    """
    print("Creating a test user")
    user = User(username="testuser", email="testuser@example.com")
    user.set_password("password")
    db.session.add(user)
    db.session.commit()
    print(f"User created: {user.username}")
    return user


@pytest.fixture
def login(user):
    """
    Fixture to simulate a logged-in user.

    This fixture uses a mock to simulate a logged-in user by patching the `_get_user` function
    from `flask_login.utils`.

    Yields:
        None
    """
    print("Setting up the login fixture")
    with patch("flask_login.utils._get_user") as mock_get_user:
        mock_get_user.return_value = user
        print(f"User logged in: {user.username}")
        yield


def test_upload_get(client, login):
    """
    Test the GET request for the upload file endpoint.

    This test ensures that the GET request to the upload file endpoint returns a 200 status code
    and that the response contains the expected content.

    Args:
        client: The test client for the Flask application.
        login: The fixture to simulate a logged-in user.
    """
    print("Testing GET request for upload file")
    response = client.get(url_for("submissions.upload_file"))
    print(f"Response status code: {response.status_code}")
    print(f"Response data: {response.data}")
    assert response.status_code == 200
    assert (
        b"Upload File" in response.data
    )  # Assuming the form has a label "Upload File"


def test_upload_post_no_file(client, login):
    """
    Test the POST request to the upload file endpoint with no file.

    This test ensures that the POST request to the upload file endpoint without a file
    returns a 302 status code and that the response contains the expected content.

    Args:
        client: The test client for the Flask application.
        login: The fixture to simulate a logged-in user.
    """
    print("Testing POST request with no file")
    response = client.post(url_for("submissions.upload_file"))
    print(f"Response status code: {response.status_code}")
    print(f"Response data: {response.data}")
    assert response.status_code == 302
    response = client.get(response.location)
    assert b"No file part" in response.data


def test_upload_post_no_selected_file(client, login):
    """
    Test the POST request to the upload file endpoint with no selected file.

    This test ensures that the POST request to the upload file endpoint with no selected file
    returns a 302 status code and that the response contains the expected content.

    Args:
        client: The test client for the Flask application.
        login: The fixture to simulate a logged-in user.
    """
    print("Testing POST request with no selected file")
    data = {"file": (None, "")}
    response = client.post(
        url_for("submissions.upload_file"),
        data=data,
        content_type="multipart/form-data",
    )
    print(f"Response status code: {response.status_code}")
    print(f"Response data: {response.data}")
    assert response.status_code == 302
    response = client.get(response.location)
    assert b"No selected file" in response.data


def test_upload_post_wrong_extension(client, login):
    """
    Test the POST request to the upload file endpoint with a wrong file extension.

    This test ensures that the POST request to the upload file endpoint with a file
    having a wrong extension returns a 302 status code and that the response contains
    the expected content.

    Args:
        client: The test client for the Flask application.
        login: The fixture to simulate a logged-in user.
    """
    print("Testing POST request with wrong file extension")
    data = {"file": (BytesIO(b"file content"), "testfile.pdf")}
    response = client.post(
        url_for("submissions.upload_file"),
        data=data,
        content_type="multipart/form-data",
    )
    print(f"Response status code: {response.status_code}")
    print(f"Response data: {response.data}")
    assert response.status_code == 302
    response = client.get(response.location)
    assert b"Only .txt files are allowed" in response.data


def test_upload_post_success(client, login, user):
    """
    Test a successful POST request to the upload file endpoint.

    This test ensures that the POST request to the upload file endpoint with a valid file
    returns a 302 status code, the response contains the expected content, and the file
    is correctly saved in the database.

    Args:
        client: The test client for the Flask application.
        login: The fixture to simulate a logged-in user.
        user: The test user.
    """
    print("Testing successful POST request")
    with patch("blog.config.s3.upload_fileobj") as mock_s3_upload:
        mock_s3_upload.return_value = None
        data = {"file": (BytesIO(b"file content"), "testfile.txt")}
        response = client.post(
            url_for("submissions.upload_file"),
            data=data,
            content_type="multipart/form-data",
        )
        print(f"Response status code: {response.status_code}")
        print(f"Response data: {response.data}")
        assert response.status_code == 302
        response = client.get(response.location)
        assert b"Blog post uploaded successfully" in response.data
        file_instance = File.query.filter_by(
            user_id=user.id, filename="testfile.txt"
        ).first()
        assert file_instance is not None


def test_upload_post_file_already_exists(client, login, user):
    """
    Test the POST request to the upload file endpoint with a file that already exists.

    This test ensures that the POST request to the upload file endpoint with a file
    that already exists returns a 302 status code and that the response contains
    the expected content.

    Args:
        client: The test client for the Flask application.
        login: The fixture to simulate a logged-in user.
        user: The test user.
    """
    print("Testing POST request with file already existing")
    file_instance = File(filename="testfile.txt", user_id=user.id)
    db.session.add(file_instance)
    db.session.commit()

    with patch("blog.config.s3.upload_fileobj") as mock_s3_upload:
        mock_s3_upload.return_value = None
        data = {"file": (BytesIO(b"file content"), "testfile.txt")}
        response = client.post(
            url_for("submissions.upload_file"),
            data=data,
            content_type="multipart/form-data",
        )
        print(f"Response status code: {response.status_code}")
        print(f"Response data: {response.data}")
        assert response.status_code == 302
        response = client.get(response.location)
        assert b"A blog post with the same name already exists." in response.data
