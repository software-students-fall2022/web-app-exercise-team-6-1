[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-c66648af7eb3fe8bc4f294546bfd86ef473780cde1dea487d3c4ff354943c9ae.svg)](https://classroom.github.com/online_ide?assignment_repo_id=8874491&assignment_repo_type=AssignmentRepo)
# Web Application Exercise

A little exercise to build a web application following an agile development process. See the [instructions](instructions.md) for more detail.

## Team members

* Jonason Wu (jw5911): [Github Profile](https://github.com/JonasonWu)
* James Liu (sl8052): [Github Profile](https://github.com/liushuchen2025)
* Ankit Jain (aj2890): [Github Profile](https://github.com/ankit181818)
* Ishana Goyal (ig1102): [Github Profile](https://github.com/ishana-goyal)

## Product vision statement

* Create a mobile app that can store and sort a collection of music that all users collectively keep track of.

## User stories

* [Issues Page](https://github.com/software-students-fall2022/web-app-exercise-team-6-1/issues)

## Task boards

* [Sprint 1](https://github.com/orgs/software-students-fall2022/projects/15)
* [Sprint 2](https://github.com/orgs/software-students-fall2022/projects/33)

## Instructions to Run App

* Follow the instructions on the README.md file of the [flask pymongo repository](https://github.com/nyu-software-engineering/flask-pymongo-web-app-example) to create the local database, make a .env file, make a virtual environment, install dependencies, run flask, etc.
* The general procedure should be as follows:
    * Open command prompt and run the following command to create the database, if you are using docker: 
        ```
        docker run --name mongodb_dockerhub -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=secret -d mongo:latest
        ```
    * Run the following command to make sure that you can access the database:
        ```
        docker exec -ti mongodb_dockerhub mongosh -u admin -p secret
        ```
    * Create a .env file with the following fields (the db name and uri may change based on how you created the local db):
        ```
        FLASK_APP=app.py
        FLASK_ENV=development
        MONGO_DBNAME=example
        MONGO_URI="mongodb://admin:secret@localhost:27017/example?authSource=admin&retryWrites=true&w=majority"
        ```
    * Make a python virtual environment and activate it:
        ```
        python3 -m venv .venv
        source .venv/bin/activate
        ```
    * Activate virtual environment:
        * Mac:
            ```
            source .venv/bin/activate
            ```
        * Windows:    
            ```
            .venv\Scripts\activate.bat
            ```
    * Install dependencies:
        ```
        pip3 install -r requirements.txt
        ```
    * Set environment variables:
        * Mac:
            ```
            export FLASK_APP=app.py
            export FLASK_ENV=development
            ```
        * Windows:
            ```
            set FLASK_APP=app.py
            set FLASK_ENV=development
            ```
    * Run flask:
        * Either:
            ```
            flask run
            ```
        * Or:
            ```
            python3 -m flask run
            ```

---

## Miscellaneous

* [Daily Standup Discord Posts](https://discord.com/channels/1014892538601152572/1031265004298715276)