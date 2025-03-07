# blog
A blog where users can post content


## Installation

1. Clone the repository
```
git clone https://github.com/adamfinklecloudberry/blog.git
```
2. Change directories into the cloned repository
```
cd blog
```
3. Create a virtual environment
```
python3 -m venv venv
```
4. Activate the virtual environment
```
source venv/bin/activate
```
5. Install the requirements
```
pip install -r requirements.txt
```
If you plan to develop Blog, also install the development requirements
```
pip install -r requirements-dev.txt
```
6. Copy the example.env to a .env file
```
cp example.env .env
```
If you plan to run locally, setup localstack.  See below.
8. Launch blog
```
python3 -m app
```

## localstack
1. Docker: Ensure Docker is installed on your machine. 
You can download it from Docker's official website.
2. Open your terminal and pull the latest LocalStack Docker image from Docker Hub.
```
docker pull localstack/localstack
```
3. Start LocalStack with default settings.
```
docker run -it -p 4566:4566 -p 4571:4571 localstack/localstack
```
4. To run the app locally, return to step 8 of Installation 

## Use
To upload and view a file for the first time
1. Click Register
2. Enter your username, email, and password
3. Click Register
4. Enter your email and password
5. Click Login
6. Click Upload File
7. Click Browse
8. Select a text (.txt) file
9. Click Upload
10. Click Back to Home
11. Click your username
12. Click the name of your file
13. See your blog post


