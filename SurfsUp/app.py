import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt
from flask import Flask, jsonify

engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(autoload_with=engine)

Station = Base.classes.station
Measurement = Base.classes.measurement

session=Session(engine)

app = Flask(__name__) 

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
        f"<p>'start' and 'end' date should be in the format YYYY-MM-DD.</p>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    last_year = dt.date(207,8,23) - dt.timedelta(days=365)

    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_year).all()
    
    session.close()

    precip_dict = {date: pr for date, pr in precipitation}
    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
    stations_results = session.query(Station.station).all()

    session.close()

    stations = list(np.ravel(stations_results))
    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def monthly_temp():
    last_year = dt.date(207,8,23) - dt.timedelta(days=365)
    tobs_year = session.query(Measurement.tobs).\
        filter(Measurement.station == "USC00519281").\
        filter(Measurement.date >= last_year).all()
    
    session.close()

    temps = list(np.ravel(tobs_year))

    return jsonify(temps=temps)

@app.route("/api/v1.0/temp/start/<start>")
@app.route("/api/v1.0/temps/<start>/<end>")
def stats(start=None, end=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        start = dt.datetime.strptime(start, "%Y-%m-%d")
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        
        session.close()

        temps = list(np.ravel(results))
        return jsonify(temps)

    start = dt.datetime.strptime(start, "%Y-%m-%d")
    end = dt.datetime.strptime(end, "%Y-%m-%d")

    results = session.queyr(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()

    temps = list(np.ravel(results))
    return jsonify(temps=temps)

if __name__ == '__main__':
    app.run()


