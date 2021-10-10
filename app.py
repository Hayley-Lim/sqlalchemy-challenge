import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
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
    """List all available api routes."""
    return (
        f"Welcome to the Hawaii API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2015-01-01<br/>"
        f"/api/v1.0/2015-01-01/2015-01-15"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all dates and prcp
    date_prcp = session.query(Measurement.date,Measurement.prcp).all()

    session.close()

    # Convert list of tuples into normal list
    all_date_prcp = list(np.ravel(date_prcp))

    return jsonify(all_date_prcp)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations IDs and names"""
    # Query all stations
    stations_tuple = session.query(Station.station,Station.name).all()

    session.close()

    # Convert list of tuples into normal list
    stations_list = list(np.ravel(stations_tuple))

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Latest Date
    latest_date_str=session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Change the date in string format to datatime.date
    latest_date = dt.datetime.strptime(latest_date_str.date, '%Y-%m-%d').date()
    
    # Calculate the date 1 year ago from the last data point in the database
    last_year = latest_date - dt.timedelta(days=365)

    # List the stations and the counts in descending order.
    active_station=session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()

    most_active_station=active_station[0][0]

    # Query the dates and temperature observations of the most active station for the last year of data.    
    date_tobs_most_active_station=session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= last_year).\
        filter(Measurement.station == most_active_station).all()

    session.close()

    # Convert list of tuples into normal list
    date_tobs_most_active_station = list(np.ravel(date_tobs_most_active_station))

    return jsonify(date_tobs_most_active_station)


@app.route("/api/v1.0/<start>")
def date_start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Change the date in string format to datatime.date
    query_start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()

    # Query TMIN, TAVG, and TMAX for all dates greater than and equal to the start date
    date_temp = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
                filter(func.strftime('%Y-%m-%d', Measurement.date) >= query_start_date).all()
    
    # Close Session
    session.close()

    return (
        f"Analysis of temperature from {start} to 2017-08-23 (the latest date):<br/>"
        f"Minimum temperature: {round(date_temp[0][0], 1)} °F<br/>"
        f"Maximum temperature: {round(date_temp[0][1], 1)} °F<br/>"
        f"Average temperature: {round(date_temp[0][2], 1)} °F"
    )

@app.route("/api/v1.0/<start>/<end>" )
def date_start_end(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Change the start date in string format to datatime.date
    query_start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()

    # Change the start date in string format to datatime.date
    query_end_date = dt.datetime.strptime(end, '%Y-%m-%d').date()

    # Query the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    date_temp = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
                filter(func.strftime('%Y-%m-%d', Measurement.date) >= query_start_date, func.strftime('%Y-%m-%d', Measurement.date) <= query_end_date).all()
    
    # Close Session
    session.close()

    return (
        f"Analysis of temperature from {start} to {end}:<br/>"
        f"Minimum temperature: {round(date_temp[0][0], 1)} °F<br/>"
        f"Maximum temperature: {round(date_temp[0][1], 1)} °F<br/>"
        f"Average temperature: {round(date_temp[0][2], 1)} °F"
    )

if __name__ == "__main__":
    app.run(debug=True)