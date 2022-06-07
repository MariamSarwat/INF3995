package com.polybixi.search

import android.util.Log
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import com.polybixi.utils.Utils
import com.polybixi.utils.HTTPSService
import com.polybixi.utils.ToastService
import org.json.JSONArray
import org.json.JSONObject

/**
 * SPDX-License-Identifier: GPL-2.0-only
 * Copyright (c) 2020 Samuel Charbonneau <samuel-3.charbonneau@polymtl.ca>
 */

class SearchModel {
    private lateinit var _vm: SearchViewModel
    private val _stationsSearch: MutableLiveData<List<Utils.StationInfo>> by lazy {
        MutableLiveData(arrayListOf())
    }

    /** DataBinding */
    fun setViewModel(vm:SearchViewModel) {
        _vm = vm
    }

    fun emptyStations() {
         _stationsSearch.value = arrayListOf()
    }

    fun getStations(): LiveData<List<Utils.StationInfo>> {
        return _stationsSearch
    }

    /**
     *  Function to get list of Bixi station IDs
     *  Parameter is search string entered by user
     *  If empty, should get all stations
     */
    fun searchForStation(searchText: String) {
        _vm.requestCounter += 1
        HTTPSService.post("station/recherche", JSONObject().put("chaine", searchText)) {
            response, _, statusCode ->
            val stations:MutableList<Utils.StationInfo> = arrayListOf()
            _stationsSearch.value = arrayListOf()
            when (statusCode) {
                200 -> {
                val stationsArray = response?.getJSONArray(Utils.JSONStations)
                if (stationsArray != null) {
                    stations.clear()
                    for(i in 0 until stationsArray.length()) {
                        val jsonID = stationsArray.getJSONObject(i)
                        val stationInfo = Utils.StationInfo(jsonID.optInt(Utils.JSONCode),
                                jsonID.optString(Utils.JSONName),
                                jsonID.optDouble(Utils.JSONLat),
                                jsonID.optDouble(Utils.JSONLng))
                        stations.add(stationInfo)
                    }
                }
            }
                400 -> { ToastService.print(Utils.Error400) }
                404 -> { Log.i(Utils.TAG, Utils.Error404) }
                else ->{ Log.e(Utils.TAG, "POST Error from server code : $statusCode") }
            }
            _stationsSearch.value = arrayListOf()
            _stationsSearch.value = stations.distinct()
            _vm.searchResultCounter = _stationsSearch.value!!.size
            _vm.requestCounter -= 1
        }
    }

    /**
     *  Function to get stationInfo (name and coordinates)
     *  Parameter is the information of the station (especially station number)
    */
    fun getStationInfo(station: Utils.StationInfo) {
        _vm.requestCounter += 1
        HTTPSService.get("station/${station.code}", JSONObject()) { response, _, statusCode ->
            var stations:ArrayList<Utils.StationInfo> = arrayListOf()
            when (statusCode) {
                200 -> {
                stations = retrieveStationsInfo(response?.getJSONArray(Utils.JSONStations))
            }
                400 -> { Log.w(Utils.TAG, "GET station info code:+ $statusCode") }
                404 -> { Log.w(Utils.TAG, "GET station info code:+ $statusCode") }
            }
            _vm.updateMap(stations.distinct())
            _vm.requestCounter -= 1
        }
    }

    /**
     * Function to get all stations' info to populate map markers
     */
    fun getAllStationInfo() {
        _vm.requestCounter += 1
        HTTPSService.get("station", JSONObject()) { response, _, statusCode ->
            var stations:ArrayList<Utils.StationInfo> = arrayListOf()
            when (statusCode) { 200 -> {
                stations = retrieveStationsInfo(response?.getJSONArray(Utils.JSONStations))
            }
                400 -> { Log.w(Utils.TAG, "GET all stations code:+ $statusCode") }
                404 -> { Log.w(Utils.TAG, "GET all stations code:+ $statusCode") }
            }
            _vm.updateMap(stations.distinct())
            _vm.requestCounter -= 1
        }
    }

    private fun retrieveStationsInfo(stationsArray: JSONArray?):ArrayList<Utils.StationInfo> {
        val stations:ArrayList<Utils.StationInfo> = arrayListOf()
        if (stationsArray != null) {
            stations.clear()
            for(i in 0 until stationsArray.length()) {
                val jsonID = stationsArray.getJSONObject(i)
                val stationInfo = Utils.StationInfo(jsonID.optInt(Utils.JSONCode),
                        jsonID.optString(Utils.JSONName),
                        jsonID.optDouble(Utils.JSONLat),
                        jsonID.optDouble(Utils.JSONLng))
                stations.add(stationInfo)
            }
        }
        return stations
    }

    companion object {
        @get:Synchronized var instance: SearchModel = SearchModel()
            private set
    }
}