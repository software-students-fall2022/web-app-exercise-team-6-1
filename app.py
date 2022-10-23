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
        'action': url_for('postAddRecord')
    }, nav={
        'home': url_for('home'),
        'add': url_for('postAddRecord'),
        'search': url_for('renderSearchRecord')
    })

#This method processes _musicForm.html and returns a dictionary with the 
# parameters to save to the db.
def getForm(form):
    #Get the title of the record.
    title = form['title'].strip()
    #Only include writers if we have a non-empty string. Get list of writers.
    writers = [writer for writer in form['writers'].split('\n') if len(writer) != 0]
    #Only include writers if we have a non-empty string. Get list of producers.
    producers = [producer for producer in form['producers'].split('\n') if len(producer) != 0]
    #Only include writers if we have a non-empty string
    genres = [genre for genre in form['genres'].split('\n') if len(genre) != 0]
    #The releaseDate is of type string and is formatted in YYYY-MM-DD
    releaseDate = form['releaseDate']
    #Get the song hours in HH format
    songHours = form['songHours'].zfill(2) if form['songHours'] != '' else '00'
    #Get the song minutes in MM format
    songMinutes = form['songMinutes'].zfill(2) if form['songMinutes'] !=  '' else '00'
    #Get the song seconds in SS format
    songSeconds = form['songSeconds'].zfill(2) if form['songSeconds'] != '' else '00'
    #The duration of the song is HH:MM:SS
    duration = songHours + ':' + songMinutes + ':' + songSeconds    
    #Get the links for the song
    links = [link for link in form['links'].split('\n') if len(link) != 0]
    #There is no need to process the lyrics.
    lyrics = form['lyrics']
    return {
        'title': title, 
        'writers': writers, 
        'producers': producers, 
        'genres': genres, 
        'releaseDate': releaseDate, 
        'duration': duration, 
        'links': links, 
        'lyrics': lyrics
    }

@app.route('/addRecord', methods=['POST'])
def postAddRecord():
    form = request.form

    #Debug statement
    print(form)
    
    save = getForm(form)

    print("The dictionary object to save:", save)

    print("Starting save operation")

    #Note: We do not need to make sure that the record is unique. If someone adds a non-unique
    #  record, then it is the job of other users to remove the record (this would be a good
    #  purpose of the delete function).
    record = db.songs.insert_one(save)

    #Debug statement
    print("This is whether save opeartion succeeded or not:", record.acknowledged)
    print("This is the result of the save operation:", record.inserted_id)

    if (record.acknowledged):
        print('Record saved successfully')
        return redirect(url_for('renderMusicRecord') + '?mongoId=' + str(record.inserted_id))
    else:
        print("The save was not successful")
        raise Exception("The save was not successful")

@app.route('/musicRecord')
def renderMusicRecord():
    mongoId = request.args['mongoId']
    record = db.songs.find_one({'_id': ObjectId(mongoId)})
    if (record):
        return render_template('musicRecord.html', nav={
            'home': url_for('home'),
            'add': url_for('renderAddRecord'),
            'search': url_for('renderSearchRecord'),
            'update': url_for('renderUpdateRecord') + '?mongoId=' + mongoId,
            'delete': url_for('renderDeleteRecord') + '?mongoId=' + mongoId
        }, doc=record, exists = True)
    else:
        return render_template('musicRecord.html', nav={
            'home': url_for('home'),
            'add': url_for('renderAddRecord'),
            'search': url_for('renderSearchRecord')
        }, exists = False)

@app.route('/updateRecord')
def renderUpdateRecord():
    print("Entered render update record method")
    mongoId = request.args['mongoId']
    try:
        record = db.songs.find_one({'_id': ObjectId(mongoId)})
    except:
        raise Exception("Cannot find music record.")
    print(record)
    form = {
        'mongoId': mongoId,
        'title': record['title'],
        'writers': '\n'.join(record['writers']),
        'producers': '\n'.join(record['producers']),
        'genres': '\n'.join(record['genres']),
        'releaseDate': record['releaseDate'],
        'songHours': record['duration'][:2],
        'songMinutes': record['duration'][3:5],
        'songSeconds': record['duration'][-2:],
        'links': '\n'.join(record['links']),
        'lyrics': record['lyrics'],
        'action': url_for('postUpdateRecord')
    }
    return render_template('updateRecord.html', form=form, nav={
        'home': url_for('home'),
        'add': url_for('renderAddRecord'),
        'search': url_for('renderSearchRecord')
    })

@app.route('/updateRecord', methods=['POST'])
def postUpdateRecord():
    print("Entered post update record")
    form = request.form
    print(form)
    print("This is mongoId:", form['mongoId'])
    update = getForm(form)
    print(update)
    db.songs.update_one({
        '_id': ObjectId(form['mongoId'])
    }, {
        '$set': update
    })
    print('Update is completed')
    return redirect(url_for('renderMusicRecord') + '?mongoId=' + form['mongoId'])
    
@app.route('/deleteRecord')
def renderDeleteRecord():
    return render_template('deleteRecord.html', form={
        'action': url_for('postDeleteRecord'),
        'mongoId': request.args['mongoId']
    }, nav={
        'home': url_for('home'),
        'add': url_for('renderAddRecord'),
        'search': url_for('renderSearchRecord')
    })

@app.route('/deleteRecord', methods=['POST'])
def postDeleteRecord():
    form = request.form
    print(form)
    db.songs.delete_one({
        '_id': ObjectId(form['mongoId'])
    })
    return redirect(url_for('renderMusicRecord') + '?mongoId=' + form['mongoId'])


@app.route('/searchRecord')
def renderSearchRecord():
    title = request.args.get('title')
    writer = request.args.get('writer')
    year = request.args.get('year')
    if title != None and len(title) != 0:
        docs = db.songs.find({
            'title': title,
        })
    else:
        docs = db.songs.find({})
    parsed = []
    for doc in docs:
        doc['path'] = url_for('renderMusicRecord') + '?mongoId=' + str(doc['_id'])
        parsed += [doc]
    if (writer != None and writer != ""):
        parsed = [doc for doc in parsed if writer in doc['writers']]
    if (year != None and year != ""):
        parsed = [doc for doc in parsed if year == doc['releaseDate'][:4]]
    for doc in parsed:
        doc['year'] = doc['releaseDate'][:4]
    return render_template('searchRecord.html', nav={
        'home': url_for('home'),
        'add': url_for('renderAddRecord'),
        'search': url_for('renderSearchRecord'),
    }, docs=parsed)

# route to handle any errors
@app.errorhandler(Exception)
def handle_error(e):
    """
    Output any errors - good for debugging.
    """
    return render_template('error.html', error=e, nav={
        'home': url_for('home'),
        'add': url_for('renderAddRecord'),
        'search': url_for('renderSearchRecord')
    }) # render the edit template


# run the app
if __name__ == "__main__":
    #import logging
    #logging.basicConfig(filename='/home/ak8257/error.log',level=logging.DEBUG)
    app.run(debug = True)
