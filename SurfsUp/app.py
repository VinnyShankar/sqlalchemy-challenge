# Import the dependencies.
from flask import Flask
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
           f"/api/v1.0/<start><br/>"
           f"/api/v1.0/<start>/<end>")

@app.route("precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Create a query that finds the most recent date in the dataset
    date_query = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
    #Convert the most recent date to a datetime object.
    for date in date_query:
        latest_date = pd.to_datetime(date)
    
    #Create a query that collects only the date and precipitation
    #for the last year of data without passing the date as a variable
    date_one_year_ago = dt.date(latest_date.year-1,latest_date.month,latest_date.day)

    one_year = session.query(Measurement.date,Measurement.prcp).\
                             filter(Measurement.date >= date_one_year_ago).all()