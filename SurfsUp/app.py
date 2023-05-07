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
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available routes."""
    return(f"Welcome to the Home Page!<br/>"
           f"Available Routes:<br/>"
           f"/api/v1.0/precipitation<br/>"
           f"/api/v1.0/stations<br/>"
           f"/api/v1.0/tobs<br/>"
           f"Replace <start> in url with start date YYYY-MM-DD format: /api/v1.0/<start><br/>"
           f"Replace <start> and <end> in url with start date YYYY-MM-DD format: /api/v1.0/<start>/<end>")

@app.route("precipitation")
def precipitation():

    ####################################################
    # Present the date and precipitation for latest year
    ####################################################

    # Create session (link) from Python to the DB
    session = Session(engine)

    # Query the latest date in the dataset
    date_query = session.query(Measurement.date).\
                               order_by(Measurement.date.desc()).first()
    
    # Convert the latest date to a datetime object
    for date in date_query:
        latest_date = pd.to_datetime(date)
    
    # Get the date one year ago
    date_one_year_ago = dt.date(latest_date.year-1,
                                latest_date.month,
                                latest_date.day)

    # Collect the date and precipitation for the latest year of data
    one_year = session.query(Measurement.date,Measurement.prcp).\
                             filter(Measurement.date >= date_one_year_ago).all()
    
    # Close the session
    session.close()
    
    # Convert query results into dictionaries
    # with date as key and precipitation as value
    year_list = []
    for date, prcp in one_year:
        date_dict = {}
        date_dict[date] = prcp
        year_list.append(date_dict)
    
    return jsonify(year_list)

    