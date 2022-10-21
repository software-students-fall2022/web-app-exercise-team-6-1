#!/usr/bin/env python3

# from crypt import methods
from flask import Flask, render_template, request, redirect, url_for, make_response
from dotenv import dotenv_values

import pymongo
import datetime
from bson.objectid import ObjectId
import sys

# instantiate the app
app = Flask(__name__)

# load credentials and configuration options from .env file
# if you do not yet have a file named .env, make one based on the template in env.example
config = dotenv_values(".env")

# turn on debugging if in development mode
if config['FLASK_ENV'] == 'development':
    # turn on debugging, if in development
    app.debug = True # debug mnode


# connect to the database
cxn = pymongo.MongoClient(config['MONGO_URI'], serverSelectionTimeoutMS=5000)
try:
    # verify the connection works by pinging the database
    cxn.admin.command('ping') # The ping command is cheap and does not require auth.
    db = cxn[config['MONGO_DBNAME']] # store a reference to the database
    print(' *', 'Connected to MongoDB!') # if we get here, the connection worked!
except Exception as e:
    # the ping command failed, so the connection is not available.
    # render_template('error.html', error=e) # render the edit template
    print(' *', "Failed to connect to MongoDB at", config['MONGO_URI'])
    print('Database connection error:', e) # debug


#I think that for the update, search, and delete, you could try adding the query, or something to represent
#Thus, make a speciailzed nav for each method that needs it.
nav = {
    'home': '/',
    'add': '/addRecord',
    'search': '/searchRecord',
    # 'update': '/updateRecord',
    # 'delete': '/deleteRecord',
}
#Example below. Basically, for the musicRecord.html, you can construct the nav object like this:
newnav = {
    'home': '/',
    'add': '/addRecord',
    'search': '/searchRecord?query=2022%20Dancing',
    #When the user clicks on the update link, it will redirect to the /updateRecord method on app.py. Then you can
    #  take the mongoId and place it in the hidden field of the form.
    'update': '/updateRecord?mongoId=14268493482392',
    'delete': '/deleteRecord?mongoId=12987502392839',
}


# set up the routes

# route for the home page
@app.route('/')
def home():
    """
    Route for the home page
    """
    
    # docs = db.exampleapp.find({}).sort("created_at", -1) # sort in descending order of created_at timestamp
    return render_template('home.html', nav=nav) # render the hone template

@app.route('/addRecord')
def addRecord():
    print("Rendering record page")

    # #This commented out section is for updateRecord.html
    # obj = {
    #     'title': 'yes',
    #     'writers': 'writer1\nwriter2',
    #     'producers': 'prod1\nprod2',
    #     'genres': 'genre1\ngenre2',
    #     'releaseDate': "01-30-2022",
    #     'lyrics': "ldsfla;sflsj dlsfjl",
    #     'songHours': None,
    #     'songMinutes': None,
    #     'songSeconds': 10,
    #     #This action parameter is where the submission of the form will redirect to.
    #     #Note: postRecord refers to the method name, not the url path.
    #     'action': url_for('postRecord')
    # }
    # #Let form=obj and the updateRecord.html page should render properly

    return render_template('addRecord.html', form={'action': url_for('postRecord')}, nav=nav)

@app.route('/', methods=['POST'])
def postRecord():
    print("Entered post record method?")
    print(request.form)
    return redirect(url_for('home'))

@app.route('/searchRecord')
def searchRecord():
    return render_template('searchRecord.html', nav=nav)

@app.route('/musicRecord')
def musicRecord():
    #Search for the record
    
    #Test this, comment one and uncomment the other one
    # return render_template('musicRecord.html', exists=False)
    return render_template('musicRecord.html', exists=True, nav=newnav)

@app.route('/updateRecord')
def updateRecord():
    obj = {
        'title': 'yes',
        'writers': 'writer1\nwriter2',
        'producers': 'prod1\nprod2',
        'genres': 'genre1\ngenre2',
        'releaseDate': "01-30-2022",
        'lyrics': "ldsfla;sflsj dlsfjl",
        'songHours': None,
        'songMinutes': None,
        'songSeconds': 10,
        #This action parameter is where the submission of the form will redirect to.
        #Note: postRecord refers to the method name, not the url path.
        'action': url_for('postUpdateRecord')
    }
    return render_template('updateRecord.html', form=obj, nav=nav)

@app.route('/updateRecord', methods=['POST'])
def postUpdateRecord():
    print("Entered postUpdateRecord")
    return redirect(url_for('musicRecord'))

@app.route('/deleteRecord')
def deleteRecord():
    return render_template('deleteRecord.html', form={
        'action': url_for('postDeleteRecord'),
        'deleteId': 'mongodb id',
    }, nav=nav)

@app.route('/deleteRecord', methods=['POST'])
def postDeleteRecord():
    print("Positng delete record")
    return redirect(url_for('musicRecord'))



# # route to accept form submission and create a new post
# @app.route('/create', methods=['POST'])
# def create_post():
#     """
#     Route for POST requests to the create page.
#     Accepts the form submission data for a new document and saves the document to the database.
#     """
#     name = request.form['fname']
#     message = request.form['fmessage']


#     # create a new document with the data the user entered
#     doc = {
#         "name": name,
#         "message": message, 
#         "created_at": datetime.datetime.utcnow()
#     }
#     db.exampleapp.insert_one(doc) # insert a new document

#     return redirect(url_for('home')) # tell the browser to make a request for the / route (the home function)


# # route to view the edit form for an existing post
# @app.route('/edit/<mongoid>')
# def edit(mongoid):
#     """
#     Route for GET requests to the edit page.
#     Displays a form users can fill out to edit an existing record.
#     """
#     doc = db.exampleapp.find_one({"_id": ObjectId(mongoid)})
#     return render_template('edit.html', mongoid=mongoid, doc=doc) # render the edit template


# # route to accept the form submission to delete an existing post
# @app.route('/edit/<mongoid>', methods=['POST'])
# def edit_post(mongoid):
#     """
#     Route for POST requests to the edit page.
#     Accepts the form submission data for the specified document and updates the document in the database.
#     """
#     name = request.form['fname']
#     message = request.form['fmessage']

#     doc = {
#         # "_id": ObjectId(mongoid), 
#         "name": name, 
#         "message": message, 
#         "created_at": datetime.datetime.utcnow()
#     }

#     db.exampleapp.update_one(
#         {"_id": ObjectId(mongoid)}, # match criteria
#         { "$set": doc }
#     )

#     return redirect(url_for('home')) # tell the browser to make a request for the / route (the home function)

# # route to delete a specific post
# @app.route('/delete/<mongoid>')
# def delete(mongoid):
#     """
#     Route for GET requests to the delete page.
#     Deletes the specified record from the database, and then redirects the browser to the home page.
#     """
#     db.exampleapp.delete_one({"_id": ObjectId(mongoid)})
#     return redirect(url_for('home')) # tell the web browser to make a request for the / route (the home function)


# route to handle any errors
@app.errorhandler(Exception)
def handle_error(e):
    """
    Output any errors - good for debugging.
    """
    return render_template('error.html', error=e, nav=nav) # render the edit template


# run the app
if __name__ == "__main__":
    #import logging
    #logging.basicConfig(filename='/home/ak8257/error.log',level=logging.DEBUG)
    app.run(debug = True)
    

