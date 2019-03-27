from flask import Flask
from flask import request
from flask import jsonify
from flask import Response
from flask import abort
from flask_cors import CORS
from weather import weather
from api_errors import *
import datetime

app = Flask(__name__)
app.url_map.strict_slashes = False
cors = CORS(app)

@app.errorhandler(ApiError)
def handle_api_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.route('/api/historical', methods=['GET'])
def historical():
    dates = weather.get_historical()
    date_dict_array = [{'DATE':date} for date in dates]
    return jsonify(date_dict_array), 200

@app.route('/api/historical/<date>', methods=['GET'])
def get_date(date):
    validate_date(date)
    date_info = weather.get_date(date)
    return jsonify(date_info), 200

@app.route('/api/historical', methods=['POST'])
def add_date():
    content = request.get_json()
    if 'DATE' not in content or 'TMAX' not in content or 'TMIN' not in content:
        raise ApiError('A parameter is missing.', status_code=400)

    validate_date(content['DATE'])
    date_text = content['DATE']

    tmax = 0.0
    try:
        tmax = float(content['TMAX'])
    except ValueError:
        raise ApiError('TMAX cannot be converted to a float.', status_code=400)

    tmin = 0.0
    try:
        tmin = float(content['TMIN'])
    except ValueError:
        raise ApiError('TMIN cannot be converted to a float.', status_code=400)
    
    date = weather.add_date(date_text, tmax, tmin)
    return jsonify({'DATE':date['DATE']}), 201

@app.route('/api/forecast/<start_date>', methods=['GET'])
def get_forecast(start_date):
    validate_date(start_date)
    forecast = weather.get_forecast(start_date)
    return jsonify(forecast), 200

@app.route('/api/historical/<date>', methods=['DELETE'])
def delete_date(date):
    validate_date(date)
    weather.delete_date(date)
    return ('', 204)

def validate_date(date_text):
    if type(date_text) is not str:
        raise ApiError("Incorrect data type.", 400)
    try:
        if date_text != datetime.datetime.strptime(date_text, r'%Y%m%d').strftime(r'%Y%m%d'):
            raise ValueError
    except ValueError:
        raise ApiError("Incorrect date format, should be YYYYMMDD.", 400)

# Start flask server when calling on the file
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=80)
