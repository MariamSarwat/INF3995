package com.polybixi.search

import androidx.databinding.Bindable
import androidx.databinding.library.baseAdapters.BR
import com.polybixi.utils.Utils
import com.polybixi.utils.GoogleMapService
import com.polybixi.utils.ObservableViewModel

/**
 * SPDX-License-Identifier: GPL-2.0-only
 * Copyright (c) 2020 Samuel Charbonneau <samuel-3.charbonneau@polymtl.ca>
 */

class SearchViewModel : ObservableViewModel() {
    private var _searchString:String = ""
    private var _searchResultCounter = 0
    private var _model = SearchModel.instance
    private var _searchFocus = false
    private var _requestCounter = 0
    private val _googleMapHandler = GoogleMapService()

    init {
        _model.setViewModel(this)
    }

    fun googleMapHandler(): GoogleMapService {
        return _googleMapHandler
    }

    /** DataBinding */
    var searchResultCounter:Int
    get(){
        return _searchResultCounter
    }
    set(value){
        if(value!= _searchResultCounter){
            _searchResultCounter = value
            notifyPropertyChanged(BR.showNoResult)
        }
    }
    var searchString: String
        @Bindable get() {
            return _searchString
        }
        set(value) {
            if (value != _searchString) {
                _searchString = value
                notifyPropertyChanged(BR.searchString)
                 if(_searchString.isNotEmpty()){
                    _model.searchForStation(searchString)
                } else{
                    _model.emptyStations()
                }
                notifyPropertyChanged(BR.showNoResult)
                searchFocus = true
            }
        }
    var searchFocus: Boolean
        @Bindable get() {
            return _searchFocus
        }
        set(value) {
            if (value != _searchFocus) {
                _searchFocus = value
                notifyPropertyChanged(BR.searchFocus)
                notifyPropertyChanged(BR.showNoResult)
            }
        }

    var requestCounter: Int
        @Bindable get() {
            return _requestCounter
        }
        set(value) {
            if (value != _requestCounter) {
                _requestCounter = value
                notifyPropertyChanged(BR.showNoResult)
                notifyPropertyChanged(BR.requestCounter)
            }
        }

    val showNoResult: Boolean
        @Bindable get() {
            return searchFocus &&
                    searchString.isNotEmpty() &&
                    _searchResultCounter  == 0 &&
                    requestCounter == 0
        }

    /** Methods used to modify the View */
    fun locateStation(station: Utils.StationInfo){
        searchString = station.name
        _model.getStationInfo(station)
        searchFocus = false
    }

    fun updateMap(stations: List<Utils.StationInfo>) {
        _googleMapHandler.setStations(stations)
    }

    fun setSearchBoxFocus(hasFocus: Boolean){
        searchFocus = hasFocus
    }

    fun setSearchBoxFocus(){
        searchFocus = true
    }
}