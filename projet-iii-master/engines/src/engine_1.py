import logging
from http import HTTPStatus

from src import db
from src.routes import Route

# Search stations by string
@Route.post('/station/recherche')
def search_station(response,body):

    if "chaine" not in body:

        logging.error("Invalid data format")

        response['body'] = {'error':'Invalid data format'}

        return HTTPStatus.BAD_REQUEST

    response["body"] = {"stations" : db.get_station_id(body['chaine'])}

    if not response["body"]["stations"]:
        return HTTPStatus.NOT_FOUND

    return HTTPStatus.OK

# Get a station by code
@Route.get('/station/<code:int>')
def get_station(response, code):

    if not str(code).isnumeric():

        response['body'] = {'error':'Invalid type of code'}

        logging.error("Invalid type of code")

        return HTTPStatus.BAD_REQUEST

    response['body'] = {"stations" : get_station_from_db(code)}

    if not response["body"]["stations"]:
        return HTTPStatus.NOT_FOUND

    return HTTPStatus.OK

@Route.get('/station')
def get_all_stations(response):

    response['body'] = {"stations" : get_station_from_db()}

    return HTTPStatus.OK

def get_station_from_db(station=""):
    return db.get_station(station)
