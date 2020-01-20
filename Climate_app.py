import sqlalchemy
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify
from functools import reduce
import datetime as dt



app = Flask(__name__)

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"

    )


#-- Need to fix the dictionary to make date the key and prcp the value
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    precip = session.query(Measurement.date, Measurement.prcp).\
                filter(Measurement.date.between('2016-08-23','2017-08-23')).all()
    session.close()

    precip_list = []
    for date, prcp in precip:
        #-- precip_dict = {}
        #-- precip_dict['date'] = date
        #-- precip_dict['prcp'] = prcp
        precip_list.append({str(date): prcp})

    return jsonify(precip_list)


@app.route("/api/v1.0/stations")
def Stations():
    session = Session(engine)
    stations_query = session.query(Station.name).all()

    session.close()

    all_stations = list(np.ravel(stations_query))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def Temp():
    session = Session(engine)
    temp_query = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.date.between('2016-08-23','2017-08-23')).all()

    session.close()

    temp_list = []
    for date, temp in temp_query:
        temp_list.append({str(date): temp})
    return jsonify(temp_list)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end='2017-08-23'):

    '''
    Return the minimum temperature, the average temperature, and the max temperature for a given start or start-end range
    '''
    session = Session(engine)

    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    if end == '2017-08-23':
        end_date = end
    else:
        end_date = dt.datetime.strptime(end, '%Y-%m-%d')

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    temps = session.query(*sel). \
                filter(Measurement.date>=start_date). \
                filter(Measurement.date<=end_date).all()[0]
    
    session.close()

    temps_stats = [{"temp_min": temps[0]}, 
                    {"temp_avg": temps[1]}, 
                    {"temp_max": temps[2]}]
    return jsonify(temps_stats)

if __name__ == "__main__":
    app.run(debug=True)
