# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.7.0]

### Added

- Two missing steps to the installation instructions

### Changed

- The use instructions


## [0.6.0]

### Added

- A list of blogs on the main page


## [0.5.0]

### Added

- Wrote and expanded docstrings for all python files
- Logging configuration by environment variable
- Logging to all routes
- An error.html where errors will redirect
- SQLAlchemy error handling to submissions.user_files, authentication.register, and authentication.login
- Error handling to authentication.logout
- Abort import

### Changed

- Changed download route to use username/postname
- Rearranged fields in example.env to be easier to understand


## [0.4.0]

### Changed

- Login and register appear when the user is not logged in
- Logout and upload file appear when the user is logged in
- Improved error handling
- Changed styling on user files list page
- Changed file list presentation to show user rather than user ID 
- Changed from user id based urls to username based urls
- Required usernames to be unique
- Displayed just the filename, without the extension or other url parts, in the file list of the user blog
- Removed outdated methods
- Changed blog font and narrowed blog width
- Updated the user blog post list formatting
- Moved the user name to the center on a dark grey banner
- Moved the blog post links to the center in a list
- Vertically centered the buttons in the banner
- Changed the logout and upload a file buttons to be of uniform verticaly thickness
- Renamed the upload a file button to upload a post
- Switched boostrap in upload.html 
- Centered the buttons of upload.html
- Upgraded the login UI with bootstrap and centered everything
- Upgaded login.html with bootstrap and centered everything
- Added login and registration flash messages
- Flash on successful upload
- Flash on unsuccesful upload
- Removed extraneous imports
- Renamed header of view.html



## [0.3.0]

### Added

- Added example.env

### Changed

- Extended password length to 255
- Extended username length to 40
- Updated requirements.txt

### Removed
- Removed bcrypt 



## [0.2.0]

### Added

- Registration and login

### Changed

- Refactored into more manageable pieces

## [0.2.0]

### Added

- Added a user page listing the urls of the files uploaded by a user
- Added an API that returns the links as a json
- Required logging in before allowing an upload
- Added a logout button to index.html
- Expanded the README
- Added requirements-dev.txt

### Changed

- Fixed login and registration


## [0.1.0]

### Added
- Basic upload and viewing


## [0.0.1]

### Added

- A main page