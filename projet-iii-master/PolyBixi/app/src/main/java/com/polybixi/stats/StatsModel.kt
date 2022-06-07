package com.polybixi.stats

import android.util.Log
import com.polybixi.utils.Utils
import com.polybixi.utils.HTTPSService
import com.polybixi.utils.ToastService
import org.json.JSONArray
import org.json.JSONObject
import java.lang.Exception
import java.text.SimpleDateFormat
import kotlin.collections.ArrayList

/**
 * SPDX-License-Identifier: GPL-2.0-only
 * Copyright (c) 2020 Jean-Olivier Dalphond <jean-olivier.dalphond@polymtl.ca>
 */

class StatsModel {
    private lateinit var _vm : StatsViewModel
    var stationInfo = Utils.StationInfo(code = Utils.DefaultStationCode)
    var allStations = false
    var requestType: Utils.RequestType = Utils.RequestType.PREDICTION
    var requestPeriod: Utils.RequestPeriod = Utils.RequestPeriod.HOUR

    /** Reference of the ViewModel instance */
    fun setViewModel(vm:StatsViewModel) {
        _vm = vm
    }

    /** Path constructor for HTTP requests */
    private fun getPath(): String {
        when (requestType) {
            Utils.RequestType.PREDICTION -> {
                var path = "prediction/usage/${requestPeriod.pathString}/"
                if (allStations) {
                    path += "toutes"
                    _vm.updateGraphTitle()
                } else {
                    getStationInfo()
                    path += _vm.stationCode
                }
                return path
            }
            Utils.RequestType.USAGE -> {
                var path = "donnees/usage/${requestPeriod.pathString}/"
                if (allStations) {
                    path += "toutes"
                    _vm.updateGraphTitle()
                } else {
                    getStationInfo()
                    path += _vm.stationCode
                }
                return path
            }
            Utils.RequestType.ERROR -> {
                _vm.updateGraphTitle()
                return "prediction/erreur"
            }
        }
    }

    /** Used to obtain Station name for Graph */
    private fun getStationInfo() {
        _vm.requestCounter += 1
        HTTPSService.get("station/${stationInfo.code}", JSONObject()) { response, _, statusCode ->
            when (statusCode) {
                200 -> {
                    val jsonArray = response?.getJSONArray(Utils.JSONStations)
                    if (jsonArray!!.length() != 1) {
                        ToastService.print(Utils.ErrorMultipleStations)
                        return@get
                    }
                    val jsonID = jsonArray.getJSONObject(0)
                    stationInfo.name = jsonID.optString(Utils.JSONName)
                    stationInfo.lat = jsonID.optDouble(Utils.JSONLat)
                    stationInfo.lng = jsonID.optDouble(Utils.JSONLng)
                    _vm.updateGraphTitle()
                }
                400 -> { Log.w(Utils.TAG, "code:+ $statusCode") }
                404 -> { Log.w(Utils.TAG, "code:+ $statusCode") }
                else -> { ToastService.print(Utils.ErrorUnknownOrNoResponse, true) }
            }
            _vm.requestCounter -= 1
        }
    }

    /** HTTP Request method to get Usage data from server
     * Populates an ArrayList of Pair<String, Int> where:
     * String is the label or descriptor of the data item
     * Int is the usage data itself (Y Axis) */
    fun getUsageData() {
        _vm.requestCounter += 1
        HTTPSService.get(getPath(), JSONObject()) {
            response, _, statusCode ->
            val list: ArrayList<Pair<String, Int>> = arrayListOf()
            when (statusCode) {
                /** HTTP response code */
                200 -> {
                    val data = response?.getJSONArray(Utils.JSONObjLabel)
                    Log.i(Utils.TAG, response.toString())
                    for(i in 0 until data!!.length()) {
                        val item = data.get(i) as JSONObject
                        when (requestPeriod) {
                            Utils.RequestPeriod.HOUR -> {
                                list.add(Pair("${item.getInt(requestPeriod.jsonString)}:00",
                                        item.getInt(Utils.JSONGraphY)))
                            }
                            Utils.RequestPeriod.WEEKDAY -> {
                                list.add(
                                    Pair(Utils.Weekdays.
                                getOrDefault(item.getInt(requestPeriod.jsonString), ""),
                                        item.getInt(Utils.JSONGraphY))
                                )
                            }
                            Utils.RequestPeriod.MONTH -> {
                                list.add(Pair(Utils.Months.
                                getOrDefault(item.getInt(requestPeriod.jsonString), ""),
                                        item.getInt(Utils.JSONGraphY)))
                            }
                            else -> { Log.e(Utils.TAG, Utils.ErrorLogBadRequestType) }
                        }
                    }
                    _vm.xLabel = requestPeriod.graphString
                    _vm.yLabel = Utils.GraphY
                    _vm.createUsageGraph(list)
                }
                400 -> { ToastService.print(Utils.Error400) }
                404 -> { ToastService.print(Utils.Error404) }
                else -> { ToastService.print(Utils.Error500orOther) }
            }
            _vm.hasData = list.isNotEmpty()
            _vm.requestCounter -= 1
        }
    }

    /** HTTP Request method to get Prediction data from server
     * Populates an ArrayList of Pair<String, Int> where:
     * String is the label or descriptor of the data item
     * Double is the prediction data itself (Y Axis) */
    fun getPredictionData() {
        _vm.requestCounter += 1
        Log.i(Utils.TAG, getPath())
        HTTPSService.get(getPath(), JSONObject()) {
            response, _, statusCode ->
            val list: ArrayList<Pair<String, Double>> = arrayListOf()
            when (statusCode) {
                /** HTTP response code */
                200 -> {
                    val data = response?.getJSONArray(Utils.JSONObjLabel)
                    for(i in 0 until data!!.length()) {
                        val item = data.get(i) as JSONObject
                        val time = item.getLong(Utils.JSONTime)
                        var prediction: Double
                        try {
                            prediction = item.getDouble(Utils.JSONPrediction)
                            when (requestPeriod) {
                                Utils.RequestPeriod.HOUR -> {
                                    list.add(Pair("$time:00", prediction))
                                }
                                Utils.RequestPeriod.WEEKDAY -> {
                                    list.add(Pair(Utils.Weekdays.
                                    getOrDefault(time.toInt(), ""), prediction))
                                }
                                Utils.RequestPeriod.DAY -> {
                                    val sdf = SimpleDateFormat(Utils.DATE_FORMAT)
                                    val netDate = sdf.format(time)
                                    list.add(Pair(netDate, prediction))
                                }
                                Utils.RequestPeriod.TEMPERATURE -> {
                                    list.add(Pair("$time°C", prediction))
                                }
                                else -> { Log.e(Utils.TAG, Utils.ErrorLogBadRequestType) }
                            }
                        } catch (err: Exception) { Log.e(Utils.TAG, Utils.ErrorNullJSON) }
                    }
                    _vm.xLabel = requestPeriod.graphString
                    _vm.yLabel = Utils.GraphAltY
                    _vm.createPredictionGraph(list)
                }
                400 -> { ToastService.print(Utils.Error400) }
                404 -> { ToastService.print(Utils.Error404) }
                else -> { ToastService.print(Utils.Error500orOther) }
            }
            _vm.hasData = list.isNotEmpty()
            _vm.requestCounter -= 1
        }
    }

    /** HTTP Request method to get Error data from server
     * Populates two ArrayLists of Pairs where:
     * String is the label or descriptor of each value
     * Int is the usage data (Y Axis)
     * Double is the prediction data (alternate Y Axis) */
    fun getErrorData() {
        _vm.requestCounter += 1
        HTTPSService.get(getPath(), JSONObject()) { response, _, statusCode ->
            val columnList: ArrayList<Pair<String, Int>> = arrayListOf()
            val lineList: ArrayList<Pair<String, Double>> = arrayListOf()
            when (statusCode) {
                /** HTTP response code */
                200 -> {
                    try {
                        val data: JSONArray? = response?.getJSONArray(Utils.JSONObjLabel)
                        for (i in 0 until data!!.length()) {
                            val item = data.get(i) as JSONObject
                            val time = item.getLong(Utils.JSONTime)
                            var prediction: Double
                            var actuel: Int
                            prediction = item.getDouble(Utils.JSONPrediction)
                            actuel = item.getInt(Utils.JSONActual)
                            when (requestPeriod) {
                                Utils.RequestPeriod.HOUR -> {
                                    lineList.add(Pair("$time:00", prediction))
                                    columnList.add(Pair("$time:00", actuel))
                                }
                                Utils.RequestPeriod.WEEKDAY -> {
                                    lineList.add(Pair(Utils.Weekdays.
                                    getOrDefault(time.toInt(), ""), prediction))
                                    columnList.add(Pair(Utils.Weekdays.
                                    getOrDefault(time.toInt(), ""), actuel))
                                }
                                Utils.RequestPeriod.DAY -> {
                                    val sdf = SimpleDateFormat(Utils.DATE_FORMAT)
                                    val netDate = sdf.format(time)
                                    lineList.add(Pair(netDate, prediction))
                                    columnList.add(Pair(netDate, actuel))
                                }
                                Utils.RequestPeriod.TEMPERATURE -> {
                                    lineList.add(Pair("$time°C", prediction))
                                    columnList.add(Pair("$time°C", actuel))
                                }
                                else -> { Log.e(Utils.TAG, Utils.ErrorLogBadRequestType) }
                            }
                        }
                    } catch (err: Exception) {
                        Log.e(Utils.TAG, Utils.ErrorNoPredictionLog)
                    }
                    _vm.xLabel = requestPeriod.graphString
                    _vm.yLabel = Utils.GraphAltY
                    _vm.yAltLabel = Utils.GraphYExplicit
                    _vm.createErrorGraph(columnList, lineList)
                }
                400 -> { ToastService.print(Utils.Error400) }
                404 -> { ToastService.print(Utils.ErrorNoPrediction) }
                else -> { ToastService.print(Utils.Error500orOther) }
            }
            _vm.hasData = (columnList.isNotEmpty() && lineList.isNotEmpty())
            _vm.requestCounter -= 1
        }
    }

    /** Singleton */
    companion object {
        @get:Synchronized var instance: StatsModel = StatsModel()
            private set
    }
}
