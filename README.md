# CSCE 310 - Sample App NoSQL Python-MongoDB

## Introduction ##

This project provides sample code for the project of CSCE 310 of Summer 2024 written following a NoSQL database design. 
Implemented in Python 3, we use MongoDB as our database server, Flask as our backend, and HTML as our frontend. This project essentially builds the same chefs application previously developed using Firebase, but uses MongoDB instead of Firebase.

## Requirements ##

* Python 3.10
* Flask - 2.1.2
* pymongo - 4.2.0
* python-dotenv - 0.20.0


## Installation ##
First, ensure you have MongoDB installed and running on your machine. You can download MongoDB from [MongoDB Community Download](https://www.mongodb.com/try/download/community).Follow the installation instructions for your operating system.


To set up the project, follow these steps:

1. Clone the repository:
```
git clone https://github.com/Summer24-CSCE-310-Database-Systems/project-example-nosql-python-mongodb.git
```

2. Create and activate a virtual environment:
```
python -m venv venv
```
On windows :
```
.\venv\Scripts\activate
```
On macOS/Linux:
```
source venv/bin/activate
```
3. Install the required packages
```
pip install Flask pymongo python-dotenv
```
## Connect to Database ##
Before running the application, ensure that your MongoDB server is running. By default, the application expects the MongoDB server to be accessible at mongodb://localhost:27017/.

## Execute Application ##

To run our web application, simply run the command 

```
flask run
```

in your preferred terminal. The flask application should start automatically. It can be accessed on a browser via the link [http://localhost:5000](http://localhost:5000).

You can also run the application by running the `app.py` file. 

## Support

If you have any issues executing this application, do not hesitate to contact the responsible TA at [vedangibengali@tamu.edu](vedangibengali@tamu.edu), or attend her office hours.