# import dependencies

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt
from flask import Flask, jsonify

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflecting the tables
Base.prepare(autoload_with=engine)

#saving references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# creating the session from python to the DB
session=Session(engine)

# flask setup
app = Flask(__name__) 

# flask routes
@app.route("/")
def welcome():
    return (
        f"Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/<start><br/>"
        f"/api/v1.0/temps/start/end<br/>"
        f"<p>'start' and 'end' should be replaced with a date in the format YYYY-MM-DD.</p>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # creating session from python to DB
    session = Session(engine)
    # calculating date one year ago from most recent date in DB
    last_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    # query to retrieve data and precipitation scores
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_year).all()
    
    session.close()
    # dictionary to hold date and precipitation scores
    precip_dict = {date: pr for date, pr in precipitation}
    # returning jsonified dictionary
    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
    # querying for all of the stations
    stations_results = session.query(Station.station).all()

    session.close()
    # list of station results
    stations = list(np.ravel(stations_results))
    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def monthly_temp():
    # calculating date one year ago from most recent date in DB
    last_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    # querying for tobs of specific station in specific timeframe
    tobs_year = session.query(Measurement.tobs).\
        filter(Measurement.station == "USC00519281").\
        filter(Measurement.date >= last_year).all()
    
    session.close()

    temps = list(np.ravel(tobs_year))

    return jsonify(temps=temps)

@app.route("/api/v1.0/temp/start/<start>")
@app.route("/api/v1.0/temps/<start>/<end>")
def stats(start=None, end=None):
    # gathering min, avg, and max of tobs
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # start date in yyyy-mm-dd format
        start = dt.datetime.strptime(start, "%Y-%m-%d")
        # query to gather min, avg, max of tobs for start date and above
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        
        session.close()

        temps = list(np.ravel(results))
        return jsonify(temps)
    # start and end in yyyy-mm-dd format 
    start = dt.datetime.strptime(start, "%Y-%m-%d")
    end = dt.datetime.strptime(end, "%Y-%m-%d")
    # query to gather min, avg, max of tobs for specific start and end date
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()

    temps = list(np.ravel(results))
    return jsonify(temps=temps)

if __name__ == '__main__':
    app.run()


