# Import the dependencies.
from flask import Flask, jsonify
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Functions to reduce redundant code
#################################################

# Find the latest date in the dataset
def latest_date():

    # Create session (link) from Python to the DB
    session = Session(engine)

    # Query the latest date in the dataset
    date_query = session.query(func.max(Measurement.date))[0][0]

    # Close the session
    session.close()

    # Return the latest date
    return date_query

# Find the date one year before lastest date
def year_ago_date(date_query):

    # Convert the latest date to a datetime object
    latest_date = pd.to_datetime(date_query)

    # Calculate the date one year ago
    date_one_year_ago = dt.date(latest_date.year-1,
                                latest_date.month,
                                latest_date.day)
    
    # Return the date one year before latest date
    return date_one_year_ago

# Dictionary function
def summary_dict(summary,start,some_date):

    # Empty list
    tlist = []

    # Construct and return dictionary
    for min, max, avg in summary:
        tdict = {}
        tdict["Start"] = start
        tdict["End"] = some_date
        tdict["TAVG"] = avg
        tdict["TMAX"] = max
        tdict["TMIN"] = min
        tlist.append(tdict)
    return tlist

# Define summary statistics
mma = [func.min(Measurement.tobs),
       func.max(Measurement.tobs),
       func.avg(Measurement.tobs)]

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available routes."""
    return(f"Welcome to the Home Page, Surfer!<br/>"
           f"---------------------------------<br/>"
           f"Available Routes:<br/>"
           f"---------------------------------<br/>"
           f"Route: /api/v1.0/precipitation<br/>"
           f"Description: Date and precipitation for latest year<br/>"
           f"---------------------------------<br/>"
           f"Route: /api/v1.0/stations<br/>"
           f"Description: List of unique stations<br/>"
           f"---------------------------------<br/>"
           f"Route: /api/v1.0/tobs<br/>"
           f"Description: Latest year of temperature data for most active station<br/>"
           f"---------------------------------<br/>"
           f"Route: /api/v1.0/start<br/>"
           f"Description: Min, max, and avg temperature from start to latest date<br/>"
           f"Hint: Replace 'start' in url with YYYY-MM-DD format<br/>"
           f"---------------------------------<br/>"
           f"Route: /api/v1.0/start/end<br/>"
           f"Description: Min, max, and avg temperature for custom date range<br/>"
           f"Hint: Replace 'start' and 'end' in url with YYYY-MM-DD format<br/>"
           )

@app.route("/api/v1.0/precipitation")
def precipitation():

    ####################################################
    # Date and precipitation for latest year
    ####################################################

    # Create session (link) from Python to the DB
    session = Session(engine)

    # Collect the date and precipitation for the latest year of data
    one_year = session.query(Measurement.date,
                             Measurement.prcp).\
                             filter(Measurement.date >= year_ago_date(latest_date())).\
                             all()
    
    # Close the session
    session.close()
    
    # Convert query results into a dictionary
    # with date as key and precipitation as value
    year_prcp_data = dict(one_year)
    
    # Return json
    return jsonify(year_prcp_data)

@app.route("/api/v1.0/stations")
def stations():

    ####################################################
    # List of stations
    ####################################################

    # Create session (link) from Python to the DB
    session = Session(engine)

    # Query stations from Station table
    stations = session.query(Station.latitude,
                             Station.id,
                             Station.elevation,
                             Station.station,
                             Station.name,
                             Station.longitude)
    
    # Close the session
    session.close()

    # Extract station from each row in the query
    station_list = []
    for latitude,id,elevation,station,name,longitude in stations:
        station_dict = {"latitude":latitude,
                        "id":id,
                        "elevation":elevation,
                        "station":station,
                        "name":name,
                        "longitude":longitude}
        station_list.append(station_dict)
    
    # Return json
    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():

    ####################################################
    # Latest year of tobs data for most active station
    ####################################################

    # Create session (link) from Python to the DB
    session = Session(engine)

    # Query for most active station id
    most_active_station = session.query(Measurement.station,
                                        func.count(Measurement.station)).\
                                        group_by(Measurement.station).\
                                        order_by(func.count(Measurement.station).\
                                        desc())[0][0]

    # Query date and tobs data for most active station
    tobs_data = session.query(Measurement.date,
                              Measurement.tobs).\
                              filter(Measurement.date >= year_ago_date(latest_date())).\
                              filter(Measurement.station == most_active_station).\
                              all()
    
    # Extract date and tobs from each row in the query
    #results = [tuple(row) for row in tobs_data]
    #results = [row[1] for row in tobs_data]
    results = [dict(tobs_data)]

    # Return json
    return jsonify(results)

@app.route("/api/v1.0/<start>")
def start(start):

    ####################################################
    # MIN, MAX, AVG temps for all dates since start
    ####################################################

    # Error mesage
    
    if latest_date() < start:
        return("Error! Check the following:<br/>"
               "Dates must be in YYYY-MM-DD format.<br/>"
               f"Your start date must be >= {latest_date()}")
    
    else:

        # Create session (link) from Python to the DB
        session = Session(engine)

        # Query for summary statistics
        summary = session.query(*mma).\
                                filter(Measurement.date >= start)
        
        # Close the session
        session.close()

        # Return json
        return jsonify(summary_dict(summary,start,latest_date()))

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):

    ####################################################
    # MIN, MAX, AVG temp for all dates since start
    ####################################################

    # Error mesage
    
    if end < start:
        return("Error! Check the following:<br/>"
               "Dates must be in YYYY-MM-DD format.<br/>"
               "Your start date must be earlier than your end date.")
    
    else:

        # Create session (link) from Python to the DB
        session = Session(engine)

        # Query for summary statistics
        summary = session.query(*mma).\
                                filter(Measurement.date >= start).\
                                filter(Measurement.date <= end)
        
        # Close the session
        session.close()

        # Return json
        return jsonify(summary_dict(summary,start,end))

# Debug mode
if __name__ == "__main__":
    app.run(debug=True)