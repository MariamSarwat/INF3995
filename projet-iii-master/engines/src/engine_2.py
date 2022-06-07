import datetime
import logging
from http import HTTPStatus

import src.db as db
from src.routes import Route
from src.utils import Times

# pylint: disable=line-too-long
@Route.get('/donnees/usage/<time:str>/<station:str>/<start_date:str>/<end_date:str>')
def get_data_with_date_range(response, time, station, start_date, end_date):

    if not is_valid_date(start_date) or not is_valid_date(end_date):
        response['body'] = {'error':'Invalid date format'}

        logging.error("Invalid date format provided")

        return HTTPStatus.BAD_REQUEST

    if not is_valid_station(station):
        response['body'] = {'error':'Invalid type of station code'}

        logging.error("Invalid code of station provided")

        return HTTPStatus.BAD_REQUEST

    if not is_valid_time(time):
        response['body'] = {'error':'Invalid time provided'}

        logging.error("Invalid time provided")

        return HTTPStatus.BAD_REQUEST

    sqlResult = get_data_from_db(time, station, start_date, end_date)

    response['body'] = {"donnees" : sqlResult}

    return HTTPStatus.OK

@Route.get('/donnees/usage/<time:str>/<station:str>/<date:str>')
def get_data_with_date(response, time, station, date):

    if not is_valid_date(date):
        response['body'] = {'error':'Invalid date format'}

        logging.error("Invalid date format provided")

        return HTTPStatus.BAD_REQUEST

    if not is_valid_station(station):
        response['body'] = {'error':'Invalid type of station code'}

        logging.error("Invalid code of station provided")

        return HTTPStatus.BAD_REQUEST

    if not is_valid_time(time):
        response['body'] = {'error':'Invalid time provided'}

        logging.error("Invalid time provided")

        return HTTPStatus.BAD_REQUEST

    sqlResult = get_data_from_db(time, station, date)

    response['body'] = {"donnees" : sqlResult}

    if not sqlResult:
        return HTTPStatus.NOT_FOUND

    return HTTPStatus.OK

@Route.get('/donnees/usage/<time:str>/<station:str>')
def get_data_by_station(response, time, station):

    if not is_valid_station(station):
        response['body'] = {'error':'Invalid type of station code'}

        logging.error("Invalid code of station provided")

        return HTTPStatus.BAD_REQUEST

    if not is_valid_time(time):
        response['body'] = {'error':'Invalid time provided'}

        logging.error("Invalid time provided")

        return HTTPStatus.BAD_REQUEST

    sqlResult = get_data_from_db(time, station)

    response['body'] = {"donnees" : sqlResult}

    if not sqlResult:
        return HTTPStatus.NOT_FOUND

    return HTTPStatus.OK


@Route.get('/donnees/usage/<time:str>')
def get_data(response, time):

    if not is_valid_time(time):
        response['body'] = {'error':'Invalid time provided'}

        logging.error("Invalid time provided")

        return HTTPStatus.BAD_REQUEST

    sqlResult = get_data_from_db(time)

    response['body'] = {"donnees" : sqlResult}

    if not sqlResult:
        return HTTPStatus.NOT_FOUND

    return HTTPStatus.OK

def is_valid_date(date):
    try:
        datetime.datetime.strptime(date, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def is_valid_station(stationCode):
    return str(stationCode).isnumeric() or stationCode == "toutes"

def is_valid_time(time):
    return time in (Times.PerHours.value,
                    Times.PerDayOfWeek.value,
                    Times.PerMonth.value)

def get_data_from_db(time, station="", date_1 = "", date_2 =""):

    fields =""
    groupBy =""
    whereClause=""

    if station and station != "toutes":
        fields += " Station as station, "
        whereClause = "WHERE station = %d" % int(station)

    if time == Times.PerHours.value:
        fields += "Hour as heure,"
        groupBy = "GROUP BY Hour"

    elif time == Times.PerMonth.value:
        fields += "Month as mois,"
        groupBy = "GROUP BY Month"

    elif time == Times.PerDayOfWeek.value:
        fields += "Weekday as jour_de_la_semaine,"
        groupBy = "GROUP BY Weekday"

    fields += "COUNT(Station) as nombre_depart"

    if date_1:
        if not whereClause:
            whereClause = "WHERE "
        else:
            whereClause += " and "

        if not date_2:
            convertedDate = datetime.datetime.strptime(date_1, '%Y-%m-%d')
            # pylint: disable=line-too-long
            whereClause += f"Year = {convertedDate.year} and Month = {convertedDate.month} and Day = {convertedDate.day} "
        else :
            convertedDate_1 = datetime.datetime.strptime(date_1, '%Y-%m-%d')
            convertedDate_2 = datetime.datetime.strptime(date_2, '%Y-%m-%d')
            # pylint: disable=line-too-long
            whereClause += f"Year BETWEEN {convertedDate_1.year} and {convertedDate_2.year} and Month BETWEEN {convertedDate_1.month} and {convertedDate_2.month} and Day BETWEEN {convertedDate_1.day} and convertedDate_2.day "

    return db.make_json_from_sql(f"SELECT {fields} FROM BIXIDATA {whereClause} {groupBy}")
