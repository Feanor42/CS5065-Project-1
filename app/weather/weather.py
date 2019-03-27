import csv
import os.path
from api_errors import *
import datetime
from functools import reduce

csv_data = {}
data_without_year = {}
my_path = os.path.abspath(os.path.dirname(__file__))
path = os.path.join(my_path, "./dailyweather.csv")
with open(path, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        date_text = row['DATE']
        tmax = float(row['TMAX'])
        tmin = float(row['TMIN'])
        csv_data[row['DATE']] = { 'DATE':date_text,
                                'TMAX':tmax, 
                                'TMIN':tmin}
        date_without_year = date_text[4:]
        if date_without_year in data_without_year:
            data_without_year[date_without_year].append({'TMAX':tmax, 
                                                        'TMIN':tmin})
        else:
            data_without_year[date_without_year] = [{'TMAX':tmax, 
                                                        'TMIN':tmin}]
def get_historical():
    return [date for date, value in csv_data.items()]

def get_date(date):
    if date in csv_data:
        return csv_data[date]
    else:
        raise ApiError("Weather information for this date does not exist.", 404)
    

def add_date(date, tmax, tmin):
    csv_data[date] = {'DATE':date,
                      'TMAX':tmax, 
                      'TMIN':tmin}
    return csv_data[date]

def delete_date(date):
    if date in csv_data:
        del csv_data[date]
    else:
        raise ApiError("Weather information for this date does not exist.", 404)

def get_forecast(start_date_text):
    forecast = []
    date = datetime.datetime.strptime(start_date_text, r'%Y%m%d')
    for i in range(0, 7): 
        date_text = date.strftime(r'%Y%m%d')
        date_text_no_year = date_text[4:]
        if  date_text in csv_data:
            forecast.append(csv_data[date_text])
        else:
            # Generate forecast
            past_weather = data_without_year[date_text_no_year]
            average_tmax = sum(weather['TMAX'] for weather in past_weather) / len(past_weather)
            average_tmin = sum(weather['TMIN'] for weather in past_weather) / len(past_weather)
            forecast.append({'DATE':date_text,
                            'TMAX':average_tmax, 
                            'TMIN':average_tmin})
        date += datetime.timedelta(days=1)
    return forecast