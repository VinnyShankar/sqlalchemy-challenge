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
# Queries to reduce reundant code
#################################################

# Create session (link) from Python to the DB
session = Session(engine)

# Query the latest date in the dataset
date_query = session.query(Measurement.date).\
                           order_by(Measurement.date.desc()).\
                           first()[0]

# Convert the latest date to a datetime object
latest_date = pd.to_datetime(date_query)

# Get the date one year ago
date_one_year_ago = dt.date(latest_date.year-1,
                            latest_date.month,
                            latest_date.day)

# Close the session
session.close()

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
           f"Date and precipitation for latest year:<br/>"
           f"/api/v1.0/precipitation<br/>"
           f"---------------------------------<br/>"
           f"List of unique stations:<br/>"
           f"/api/v1.0/stations<br/>"
           f"---------------------------------<br/>"
           f"Latest year of temperature data for most active station:<br/>"
           f"/api/v1.0/tobs<br/>"
           f"---------------------------------<br/>"
           f"Min, max, and avg temperature for the latest year:<br/>"
           f"(Hint: Replace start in url with start date YYYY-MM-DD format)<br/>"
           f"/api/v1.0/start<br/>"
           "---------------------------------<br/>"
           f"Min, max, and avg temperature for custom date range:<br/>"
           f"(Hint: Replace start and end in url with start and end dates YYYY-MM-DD format)<br/>"
           f"/api/v1.0/start/end"
           )

@app.route("/api/v1.0/precipitation")
def precipitation():

    ####################################################
    # Date and precipitation for latest year
    ####################################################

    # Create session (link) from Python to the DB
    session = Session(engine)

    # Collect the date and precipitation for the latest year of data
    one_year = session.query(Measurement.date,Measurement.prcp).\
                             filter(Measurement.date >= date_one_year_ago).\
                             all()
    
    # Close the session
    session.close()
    
    # Convert query results into dictionaries
    # with date as key and precipitation as value
    year_list = []
    for date, prcp in one_year:
        date_dict = {}
        date_dict[date] = prcp
        year_list.append(date_dict)
    
    # Return json
    return jsonify(year_list)

@app.route("/api/v1.0/stations")
def stations():

    ####################################################
    # List of unique stations
    ####################################################

    # Create session (link) from Python to the DB
    session = Session(engine)

    # Query unique stations from Station table
    stations = session.query(Station.station).distinct()
    
    # Close the session
    session.close()

    # Extract station from each row in the query
    station_list = [station[0] for station in stations]

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
                              filter(Measurement.date >= date_one_year_ago).\
                              filter(Measurement.station == most_active_station).\
                              all()
    
    # Extract date and tobs from each row in the query
    results = [tuple(row) for row in tobs_data]

    # Return json
    return jsonify(results)

@app.route("/api/v1.0/<start>")
def start(start):

    ####################################################
    # MIN, MAX, AVG temp for all dates since start
    ####################################################

    # Create session (link) from Python to the DB
    session = Session(engine)

    summary = session.query(func.min(Measurement.tobs),
                            func.max(Measurement.tobs),
                            func.avg(Measurement.tobs)).\
                            filter(Measurement.date >= start)
    
    # Close the session
    session.close()

    # Extract results from query
    for row in summary:
        summary_list = tuple(row)

    # Return json
    return jsonify(summary_list)

if __name__ == "__main__":
    app.run(debug=True)