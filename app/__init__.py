import flask
from flask import Flask, render_template, request, jsonify, url_for
from collections import defaultdict
import pymysql
from array import array
#%% Simple selector (MySQL database)
# import mysql.connector needs to be installed pip install mysql-connector
import mysql.connector
from mysql.connector import MySQLConnection, Error

# Prompt user for mysql username and password
username = raw_input('MySQL Username: ')
password = raw_input('MySQL Password: ')

# Connect to DB
db = pymysql.connect(host='localhost', user=username, password=password, db='top500Info', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor, autocommit=True)

print 'Connected to database!'

# init cursors
cursor1 = db.cursor()
cursor2 = db.cursor()
cursor3 = db.cursor()
cursor4 = db.cursor()
cursor5 = db.cursor()
cursor6 = db.cursor()
filterCursor = db.cursor()
reviewCursor = db.cursor()
visitorCursor = db.cursor()
profileCursor = db.cursor()

# declare app
app = Flask(__name__, instance_relative_config=True)

# Get all continent names
def getContinents():
    continents_stmt = 'SELECT DISTINCT continent_name FROM continent'
    cursor1.execute(continents_stmt)
    continents = cursor1.fetchall()
    continent_names = []
    for row in continents:
        continent_names.append(row['continent_name'])

    return continent_names

# Get all distinct climates
def getClimates():
    climates_stmt = 'SELECT DISTINCT climate FROM continent ORDER BY climate'
    cursor2.execute(climates_stmt)
    climates = cursor2.fetchall()
    climate_names = []
    for row in climates:
        climate_names.append(row['climate'])

    return climate_names

# Get all country names
def getCountries():
    countries_stmt = 'SELECT DISTINCT cname FROM country ORDER BY cname'
    cursor3.execute(countries_stmt)
    countries = cursor3.fetchall()
    country_names = []
    for row in countries:
        country_names.append(row['cname'])

    return country_names

# Get all distinct categories
def getCategories():
    categories_stmt = 'SELECT DISTINCT category FROM attraction ORDER BY category'
    cursor4.execute(categories_stmt)
    categories = cursor4.fetchall()
    category_names = []
    for row in categories:
        category_names.append(row['category'])

    return category_names

# Get all distinct origins
def getOrigins():
    origins_stmt = 'SELECT DISTINCT origin FROM attraction'
    cursor5.execute(origins_stmt)
    origins = cursor5.fetchall()
    origin_names = []
    for row in origins:
        origin_names.append(row['origin'])

    return origin_names

# Get all attraction names
def getAttractionNames():
    names_stmt = 'SELECT name FROM attraction ORDER BY name'
    cursor6.execute(names_stmt)
    names = cursor6.fetchall()
    att_names = []
    for row in names:
        att_names.append(row['name'])

    return att_names


# index page (homepage)
@app.route('/')
def db():
    continents = getContinents()
    climates = getClimates()
    countries = getCountries()
    categories = getCategories()
    origins = getOrigins()

    return render_template('index.html', continents=continents, climates=climates, countries=countries, categories=categories, origins=origins)

# Filter results page
@app.route('/filter', methods=['GET', 'POST'])
def filter():
    continent = str(request.form.get('continent'))
    climate = str(request.form.get('climate'))
    country = str(request.form.get('country'))
    category = str(request.form.get('category'))
    origin = str(request.form.get('origin'))

    filterItems = [continent, climate, country, category, origin]

    params = []
    for item in filterItems:
        if 'All' in item:
            item = ''
            params.append(item)
        else:
            params.append(item)

    results = filterAttractions( params )
    return render_template('filter.html', filterItems=filterItems, results=results)


def filterAttractions( params ):
    continent = params[0]
    climate = params[1]
    country = params[2]
    category = params[3]
    origin = params[4]
    headers = [' continent = ', ' climate = ', ' countryN = ', ' category = ', ' origin = ']

    conditions = ''
    i = 0
    for col in params:
        if col != '':
            conditions += headers[i]
            conditions += '"' + col + '"'
            conditions += ' AND'
        i += 1

    stmt = "SELECT * FROM attraction WHERE "
    cond = conditions[:-4]
    orderby = " ORDER BY attract_id"


    # concat strings to create full select statement based on user inputs
    select_stmt = stmt + cond + orderby
    filterCursor.execute(select_stmt)
    results = filterCursor.fetchall()
    result_arr = []
    for row in results:
        values = row.values()
        result_arr.append(values)

    return result_arr


# Create a visitor page
@app.route('/visitor')
def visitor():
    countries = getCountries()
    return render_template('visitor.html', countries=countries)


# Get a visitor based on visitorID
def getVisitor(visitorID):
    stmt = 'SELECT * FROM visitor WHERE visitor_id = ' + visitorID
    profileCursor.execute(stmt)
    results = profileCursor.fetchall()
    visitors = []
    for row in results:
        values = row.values()
        visitors.append(values)

    return visitors[0]


# Create visitor
@app.route('/profile', methods=['GET', 'POST'])
def createVisitor():
    firstname = str(request.form.get('firstname'))
    lastinitial = str(request.form.get('lastinitial'))
    age = str(request.form.get('age'))
    homecountry = str(request.form.get('homecountry'))

    # Call new_visitor procedure
    sql = "CALL new_visitor('"+ firstname +"', '"+ lastinitial +"', "+ age +", '"+ homecountry +"')"
    visitorCursor.execute(sql)
    results = visitorCursor.fetchall()
    visitorIDs = []
    for row in results:
        visitorIDs.append(row['your_id'])

    visitorID = str(visitorIDs[0])

    visitorInfo = getVisitor(visitorID)

    homecountry = visitorInfo[0]
    age         = visitorInfo[1]
    firstname   = visitorInfo[2]
    idNum       = visitorInfo[3]
    lastinitial = visitorInfo[4]

    countries = getCountries()

    return render_template('profile.html', visitorID = visitorID, firstname = firstname, lastinitial = lastinitial, age = age, homecountry = homecountry, countries = countries)


# Update visitor
@app.route('/updateVisitor', methods=['GET', 'POST'])
def updateVisitor():
    visitorID = str(request.form.get('visitorid'))
    firstname = str(request.form.get('firstname'))
    lastinitial = str(request.form.get('lastinitial'))
    age = str(request.form.get('age'))
    homecountry = str(request.form.get('homecountry'))

    # Call update_visitor procedure
    sql = "CALL update_visitor('"+ visitorID +"', '"+ firstname +"', '"+ lastinitial +"', "+ age +", '"+ homecountry +"')"
    visitorCursor.execute(sql)

    visitorInfo = getVisitor(visitorID)

    homecountry = visitorInfo[0]
    age         = visitorInfo[1]
    firstname   = visitorInfo[2]
    visitorID   = visitorInfo[3]
    lastinitial = visitorInfo[4]

    countries = getCountries()

    return render_template('profile.html', visitorID = visitorID, firstname = firstname, lastinitial = lastinitial, age = age, homecountry = homecountry, countries = countries)


# Delete visitor
@app.route('/deleteVisitor', methods=['POST'])
def deleteVisitor():
    visitorID = str(request.form.get('visitorid'))

    # Call update_visitor procedure
    sql = "CALL delete_visitor('"+ visitorID +"')"
    visitorCursor.execute(sql)

    countries = getCountries()
    return render_template('visitor.html', countries=countries)


# Write a review page
@app.route('/review')
def review():
    attractions = getAttractionNames()
    return render_template('review.html', attractions=attractions)


# Get a visitor based on visitorID
def getReviews(visitorID):
    stmt = 'SELECT * FROM review WHERE author = ' + visitorID
    reviewCursor.execute(stmt)
    results = reviewCursor.fetchall()
    reviews = []
    for row in results:
        values = row.values()
        reviews.append(values)

    print results

    # return reviews[0]


# Get an attraction ID based on attraction name
def getAttractionID(name):
    stmt = "SELECT attract_id FROM attraction WHERE name = '"+ name +"'"
    reviewCursor.execute(stmt)
    results = reviewCursor.fetchall()
    attID = []
    for row in results:
        attID.append(row['attract_id'])

    return attID[0]


# New review page
@app.route('/reviews', methods=['GET', 'POST'])
def createReview():
    visitorID = str(request.form.get('visitorID'))
    location = str(request.form.get('location'))
    dateVisited = str(request.form.get('dateVisited'))
    overall = str(request.form.get('overall'))
    family = str(request.form.get('family'))
    adventure = str(request.form.get('adventure'))

    attraction_id = str(getAttractionID(location))

    # Call new_visitor procedure
    sql = "CALL new_review('"+ dateVisited +"', '"+ visitorID +"', '"+ attraction_id +"', '"+ overall +"', '"+ family +"', '"+ adventure +"')"
    reviewCursor.execute(sql)

    reviews = getReviews(visitorID)
    # print reviews

    return render_template('reviews.html')



# In-class presentation page
@app.route('/presentation')
def presentation():
    return render_template('presentation.html')



# Load the config file
app.config.from_object('config')
