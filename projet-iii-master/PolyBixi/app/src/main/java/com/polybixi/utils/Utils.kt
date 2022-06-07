package com.polybixi.utils

import kotlinx.serialization.Serializable

/**
 * SPDX-License-Identifier: GPL-2.0-only
 * Copyright (c) 2020 Jean-Olivier Dalphond <jean-olivier.dalphond@polymtl.ca>,
 * Samuel Charbonneau <samuel-3.charbonneau@polymtl.ca>
 */

/** Data Classes and enums */
object Utils {
    /** Timer configuration */
    const val StatusTimerInterval: Long = 10000
    const val StatusAllUP = "STATUS: All data engines UP"
    /** Google Maps config values */
    const val TAG = "POLYBIXI_TAG"
    const val lat = 45.504916
    const val lng = -73.613415
    const val minZoom = 10.0f
    const val focusZoom = 13.0f
    /** Configuration for HTTP Service */
    var serverIP = "172.105.99.131"
    const val StatusErrorMessage = "STATUS: Cannot get data engines status!"
    /** Stats Error and Miscellaneous messages */
    const val DefaultStationCode = 6114
    const val ErrorMultipleStations = "Plus d'une station correspondante. Veuillez vérifier le code entré."
    const val ErrorUnknownOrNoResponse = "Erreur lors de la récupération des informations sur la station!"
    const val ErrorLogBadRequestType = "Error: wrong request type/period combination, should not happen!"
    const val Error400 = "Erreur dans le format de la requête."
    const val Error404 = "No data found for station."
    const val Error500orOther = "Erreur interne du serveur, ou le serveur ne répond pas."
    const val ErrorNullJSON = "Error: prediction is null!"
    const val ErrorNoPredictionLog = "Server error: No prediction data"
    const val ErrorNoPrediction = "Aucune prédiction effectuée. Veuillez d'abord soumettre une requête de catégorie Prédiction."
    const val JSONObjLabel = "donnees"
    const val JSONTime = "temps"
    const val JSONActual = "actuel"
    const val JSONPrediction = "prediction"
    const val JSONGraphY = "nombre_depart"
    const val JSONStations = "stations"
    const val JSONName = "nom"
    const val JSONLat = "latitude"
    const val JSONLng = "longitude"
    const val JSONCode = "code"
    const val GraphAltY = "Départs prévus"
    const val GraphY = "Départs"
    const val GraphYExplicit = "Départs réels"
    const val GraphAllStations = "Toutes les stations"
    const val StatsArg = "stationCode"
    const val GraphErrorTitle = "Erreurs de l'engin de prédiction"
    const val DATE_FORMAT = "MM/dd"
    /** Survey Messages */
    const val SurveySent = "Sondage envoyé. Merci!"
    const val SurveyContentError = "Sondage refusé par le serveur. Veuillez vérifier les données."
    const val ServerUnknownError = "Le serveur ne répond pas. Est-ce que l'adresse est valide?"
    const val SurveyCheckFields = "Veuillez vérifier les données."
    /** Settings Messages */
    const val SettingsWrongFormat = "Veuillez vérifier le format de l'adresse."
    const val SettingsAddressSaved = "Adresse enregistrée."
    @Serializable
    data class StationInfo(var code:Int=DefaultStationCode,var name: String="", var lat: Double=0.0, var lng: Double=0.0)
    @Serializable
    data class SurveyData(var email: String ="", var firstName: String="", var lastName: String="", var age: Int=1, var interest: Boolean=false)
    enum class RequestPeriod(val pathString: String, val jsonString: String, val graphString: String) {
        HOUR("parheure", "heure", "Heure"),
        WEEKDAY("parjourdelasemaine", "jour_de_la_semaine", "Jour de la semaine"),
        MONTH("parmois", "mois", "Mois"),
        TEMPERATURE("partemperature", "temperature", "Température"),
        DAY("parjour", "", "Jour de l'année")
    }
    enum class RequestType {
        USAGE, PREDICTION, ERROR
    }
    val Months: Map<Int, String> = mapOf(
            0 to "Janvier",
            1 to "Février",
            2 to "Mars",
            3 to "Avril",
            4 to "Mai",
            5 to "Juin",
            6 to "Juillet",
            7 to "Août",
            8 to "Septembre",
            9 to "Octobre",
            10 to "Novembre",
            11 to "Décembre"
    )
    val Weekdays: Map<Int, String> = mapOf(
            0 to "Lundi",
            1 to "Mardi",
            2 to "Mercredi",
            3 to "Jeudi",
            4 to "Vendredi",
            5 to "Samedi",
            6 to "Dimanche"
    )
    /** Graph colors - Dark mode */
    const val LighterGrey = "#EBEBEB"
    const val Transparent = "#00000000"
    const val Blue = "#2687EB"
    const val DarkerBlue = "#13385E"
    /** Graph colors - Light mode */
    const val Black = "#000000"
    const val LightBlue = "#A5D1FF"
    const val DarkBlue = "#215F9E"
    const val DarkerGrey = "#3C3C3C"
    /** Graph styling */
    const val TitleSize = 20.0f
    const val SubtitleSize = 18.0f
}