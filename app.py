import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify


# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
#################################################
app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all passengers
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()
#Convert the query results to a dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.

    # Create a dictionary from the row data and append to a list of all_temps
    all_temps = []
    for date,prcp in results:
        temps_dict = {}
        temps_dict["date"] = date
        temps_dict["prcp"] = prcp
        all_temps.append(temps_dict)

    return jsonify(all_temps)


@app.route("/api/v1.0/stations")
def stations():
       # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations names"""
    # Query all passengers
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)


#Query the dates and temperature observations of the most active station for the last year of data.
#Return a JSON list of temperature observations (TOBS) for the previous year.


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all temp data
    station_data = session.query(Measurement.station,func.count(Measurement.station),func.max(Measurement.date)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()

    station_id = station_data[0]

    max_date= station_data[2]
    
    query_date= dt.datetime.strptime(max_date,'%Y-%m-%d') - dt.timedelta(days=365)

    results= session.query(Measurement.station,Measurement.date,Measurement.tobs).filter(Measurement.station==station_id).filter(Measurement.date>=query_date).all()

    session.close()
    
    all_names = list(np.ravel(results))

    return jsonify(all_names)


#/api/v1.0/<start> and /api/v1.0/<start>/<end>
##Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

@app.route(f"/api/v1.0/<start>")
def start(start):
       # Create our session (link) from Python to the DB
    session = Session(engine)

    query_date= dt.datetime.strptime(start,'%Y-%m-%d')

    results= session.query(Measurement.date,func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).group_by(Measurement.date).filter(Measurement.date>=query_date).all()

    session.close()
    
    all_names = list(np.ravel(results))

    return jsonify(all_names)


@app.route(f"/api/v1.0/<start>/<end>")
def start_end(start,end):
       # Create our session (link) from Python to the DB
    session = Session(engine)

    query_date= dt.datetime.strptime(start,'%Y-%m-%d')

    query_end_date= dt.datetime.strptime(end,'%Y-%m-%d')

    results= session.query(Measurement.date,func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).group_by(Measurement.date).filter(Measurement.date>=query_date).filter(Measurement.date<=query_end_date).all()

    session.close()
    
    all_names = list(np.ravel(results))

    return jsonify(all_names)


if __name__ == '__main__':
    app.run(debug=True)

