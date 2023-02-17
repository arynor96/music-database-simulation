# Solving	Heat	Equation	in	2D


### Short description

This project was done for the Information Management & Systems Engineering class at the University of Vienna.
The main purpose of this project is to try to simulate a streaming platform where users can rate albums. There should be also be possible to migrate all the MySQL database to MongoDB using only one button on the website. More details can be found in: IMSE Guidelines SS2022.pdf

###  Configuration of Infrastructure

This project uses: Docker, Python, Flask, MySQL, MongoDB, Nginx.

To start the container, go to the unzipped folder and run: $ docker-compose up
Go to https://127.0.0.1

Containers:
* web - The name of the container is flask, it contains all the backend.
* db - The name of the container is sql, it contains mysql:5.7 image. The used port for MySQL is 3306.
* mongodb - The name of the container is mongo, and it contains the MongoDB
database, the used port is 27017.
* nginx - container name nginx. Uses a self signed certificate.


More information about the project can be found inside the pdf files from the root directory.


### Entity–relationship model

### What it can do

- Create account.
- Login.
- Post a review to an album or update a review.
- Search and add a song to favorites.
- Display each artist's top rated album.
- Display albums with the most reviews from accounts created last year.
- Migrate from MySQL to MongoDB. All use cases work on both databases.

More details about use cases including swimlanes are provided inside the team27_description.pdf file.

### Data import

To be able to import data, we have decided to use Pandas. Pandas is a Python library which makes data manipulation and analysis easier. Our data for each table is stored as csv files inside /helpers/db_data folder. Using those csv files and the Pandas library, we have created a function fill_sql_tables inside sql_functions.py which reads each csv file.

### How to use

After the website is up and running, the user has to go to : https://127.0.0.1 and press the Initialize DB button. The user is not able to do anything until the database is initialized. After the database is initialized, a message will be displayed to inform the user that the database is initialized. The user can scroll using the navbar through Artists, Songs, Albums, Reviews, Top Albums by each Artist and The Most Reviewed Albums. Additionally, the user can migrate the SQL database to NoSQL and also completely reset the website. Other than that, the user can also log in or logout. On the Albums page, the user may post a review. To do so, the user has to be logged in. A user to test how it works is:
<br>
Email: adrian@gmail.com
Password: 123aaa123
<br>
Besides that, a new account can be created from the login page. After the user is logged in, posting a review is possible. To post a review, an album name is required. If the album is not found, the user will be informed that the albums does not exist in our database. If the user has already reviewed that album, the review will be updated and the user will be informed that the review was updated. In the MongoDB tab, the user can decide to Migrate to NoSQL. This should take no longer than 10 seconds. Anyway, the user will be informed when the migration is done. After the migration happen, everything should work like on the SQL version. If the user decides to do the initialization again, he may press the ResetWebsite button and everything will start once again with an empty database.


More details in: team27_report.pdf