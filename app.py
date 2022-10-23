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


# set up the routes

# route for the home page
@app.route('/')
def home():
    return render_template('home.html', nav={
        'home': url_for('home'),
        'add': url_for('renderAddRecord'),
        'search': url_for('renderSearchRecord')
    })

@app.route('/addRecord')
def renderAddRecord():
    return render_template('addRecord.html', form={
        'action': url_for('postRecord')
    }, nav={
        'home': url_for('home'),
        'add': url_for('postAddRecord'),
        'search': url_for('renderSearchRecord')
    })

@app.route('/addRecord', methods=['POST'])
def postAddRecord():
    title = request.form['title']

    #To Do (Time permitting): Make a more robust way of searching for duplicates
    num_dupe = db.songs.count_documents({"title": title})

    if num_dupe >= 1:
        print("DUPLICATE SONG FOUND, not adding to db")

        #Until we work out another way to deal with duplicate songs,
        # I will just route to home page
        # Perhaps we can route to the corresponding page for
        # Update/Delete?

    else:
        writers = request.form['writers']
        producers = request.form['producers']
        genres = request.form['genres']
        release_date = request.form['releaseDate']
        song_hours = request.form['songHours']
        song_minutes = request.form['songMinutes']
        song_seconds = request.form['songSeconds']
        links = request.form['links']
        lyrics = request.form['lyrics']

        new_record = {
            "title": title,
            "writers": writers,
            "producers": producers,
            "genres": genres,
            "Release Date": release_date,
            "Song Hours": song_hours,
            "Song Minutes": song_minutes,
            "Song Seconds": song_seconds,
            "Links": links,
            "lyrics": lyrics
        }

        db.songs.insert_one(new_record) #Collection within our database will be called songs from now on
        print("Inserted a new song called: ", new_record['title'])
    return redirect(url_for('home'))





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
    #print("Entered post record method?")
    #print(request.form)

    

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

@app.route('/searchByTitle/<title>')
def searchByTitle(title):

    #Idea used to check that songs are being added to the db:
    # Print each song's title, author as a list to the webpage 
    # Temporary, just to ensure that db operations are working as intended

    songs = db.songs.find({"title": title})

    if (songs.count() == 0):
        return "No songs found with that title"

    print("Printing songs with title: ", title)

    return songs[0]['title']

@app.route('/searchByAuthor/<author>')
def searchByAuthor(author):

    songs = db.songs.find({"writers": author})

    if (songs.count() == 0):
        return "No songs found with that author"

    print(author + " wrote following songs: \n")

    for song in songs:

        print(song['title'])

    return song['writers']

@app.route('/musicRecord')
def musicRecord():
    #Search for the record
    
    #Test this, comment one and uncomment the other one
    # return render_template('musicRecord.html', exists=False)
    return render_template('musicRecord.html', exists=True, nav=newnav)

@app.route('/updateRecord/<mongoId>')
def updateRecord(mongoId):
    docs = db.songs.find_one({"_id": ObjectId(mongoId)})
    obj = {
        'title': docs['title'],
        'writers': docs['writers'],
        'producers': docs['producers'],
        'genres': docs['genres'],
        'releaseDate': docs['Release Date'],
        'lyrics': docs['lyrics'],
        'songHours': docs['Song Hours'],
        'songMinutes': docs['Song Minutes'],
        'songSeconds': docs['Song Seconds'],
        #This action parameter is where the submission of the form will redirect to.
        #Note: postRecord refers to the method name, not the url path.
        'action': url_for('postUpdateRecord')
    }
    return render_template('updateRecord.html', form=obj, nav=nav)

@app.route('/updateRecord', methods=['POST'])
def postUpdateRecord():

    return redirect(url_for('musicRecord'))

@app.route('/records', methods=['GET'])
def getRecords():
    """
    Route for the records page
    """

    docs = db.songs.find({}).sort("title", 1)  # sort in ascending alphabetical order of title
    # convert the cursor to dictionary
    for doc in docs:

        response = {
            'title': doc['title'],
            'writers': doc['writers'],
            'producers': doc['producers'],
            'genres': doc['genres'],
            'releaseDate': doc['Release Date'],
            'lyrics': doc['lyrics'],
            'songHours': doc['Song Hours'],
            'songMinutes': doc['Song Minutes'],
            'songSeconds': doc['Song Seconds'],
            'links': doc['Links']
        }

        print(response)

    return response


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

@app.route('/deleteRecord/<title>', methods=['DELETE'])
def delete(title):
    print("Deleting record id: " + title)

    try:   # delete the record with the given title from the database
         db.songs.delete_one({'title': title})

    except Exception as e:
        print(' *', "Failed to delete record with title: " + title)
        print("\n" + e)

    return "Deleted record id: " + title


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
    

