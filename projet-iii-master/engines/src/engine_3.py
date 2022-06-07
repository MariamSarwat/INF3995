import datetime
import json
from http import HTTPStatus

import src.initialization
from src.routes import Route
from src.dataframe import getdataframe
from src.prediction import getprediction
from src.utils import Times, format_date

cache = { }

@Route.get('/prediction/usage/<time:str>/<station:str>')
def get_prediction_with_time_station(response, time, station):

    if not is_valid_time(time):
        response['body'] = {'error':'Invalid time provided'}
        return HTTPStatus.BAD_REQUEST

    if not is_valid_station(station):
        response['body'] = {'error':'Invalid type of station code'}
        return HTTPStatus.BAD_REQUEST

    sqlResult        = temperature_prediction(time,station)
    if not sqlResult:
        return HTTPStatus.NOT_FOUND
    response['body'] = {"donnees" : sqlResult}

    return HTTPStatus.OK

@Route.get('/prediction/usage/<time:str>')
def get_prediction_with_time(response, time):

    if not is_valid_time(time):
        response['body'] = {'error':'Invalid time provided'}

    return HTTPStatus.BAD_REQUEST

@Route.get('/prediction/erreur')
def get_prediction_erreur(response):

    # check if there's a entry in dictionary
    if src.initialization.last_prediction:
        if "partemperature" in src.initialization.last_prediction:
            request=src.initialization.last_prediction.split('/')
            time=request[0]
            station=request[1]
            cache.pop(src.initialization.last_prediction)
            sqlResult=get_result(time, station,False)
        sqlResult        = valid_prediction()
        response['body'] = {"donnees" : sqlResult}
        return HTTPStatus.OK

    return HTTPStatus.NOT_FOUND

def valid_prediction():

    data = cache[src.initialization.last_prediction][0]
    data = data.dropna(axis=0, subset=['prediction'])
    data = data.dropna(axis=0, subset=['actuel'])
    json_obj   = json.loads(data.to_json(orient="records"))
    sorted_obj = sortData(json_obj)

    return sorted_obj

def temperature_prediction(time,station):
    if time == Times.PerTemperature.value:
        return get_result(time,station,True)
    return get_result(time,station,False)

def is_valid_station(stationCode):
    return (str(stationCode).isnumeric() or
            stationCode == "toutes")

def is_valid_time(time):
    return time in (Times.PerHours.value,
                    Times.PerDayOfWeek.value,
                    Times.PerTemperature.value,
                    Times.PerDay.value)

def get_result(time,station,do_prediction):

    getRequest = f"{time}/{station}"

    #check if prediction exist in dictionary
    if getRequest in cache:
        data, thunk = cache[getRequest]
        thunk()
        data = data.drop(columns=['actuel'])
    #if not, do the prediction
    else:
        #extract right data
        actual= getdataframe(station, time)
        if actual.empty:
            return False
        if do_prediction:
            actual=actual.drop(columns='Temperature')
            actual=actual.rename(columns={'Temp2018':'Temperature'})
        actual = actual.dropna(axis=0, subset=['Actual'])
        print(actual)

        if time == Times.PerDay.value:
            years  = actual['Year']
            months = actual['Month']
            days   = actual['Day']

            dates = [format_date(year, month, day)
                     for year, month, day
                     in zip(years, months, days)]

            dates = [datetime.datetime.strptime(date, '%Y-%m-%d')
                     for date
                     in dates]

        elif time == Times.PerHours.value:
            dates = actual['Hour']

        elif time == Times.PerDayOfWeek.value:
            dates = actual['Weekday']

        elif time == Times.PerTemperature.value:
            dates = actual['Temperature']

        data, thunk       = getprediction(actual, dates, time)
        cache[getRequest] = (data, thunk)
        data              = data.drop(columns=['actuel'])

    data       = data.dropna(axis=0, subset=['prediction'])
    json_obj   = json.loads(data.to_json(orient="records"))
    sorted_obj = sortData(json_obj)

    src.initialization.last_prediction = getRequest

    return sorted_obj

def sortData(data):
    return sorted(data, key=lambda k: k['temps'])
