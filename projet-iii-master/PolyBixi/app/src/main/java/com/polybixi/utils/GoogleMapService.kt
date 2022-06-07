package com.polybixi.utils

import android.view.View
import androidx.core.os.bundleOf
import androidx.navigation.Navigation
import com.google.android.gms.maps.CameraUpdateFactory
import com.google.android.gms.maps.GoogleMap
import com.google.android.gms.maps.OnMapReadyCallback
import com.google.android.gms.maps.model.LatLng
import com.google.android.gms.maps.model.Marker
import com.google.android.gms.maps.model.MarkerOptions
import com.polybixi.R
import com.polybixi.search.SearchModel

/**
 * SPDX-License-Identifier: GPL-2.0-only
 * Copyright (c) 2020 Samuel Charbonneau <samuel-3.charbonneau@polymtl.ca>
 */

class GoogleMapService: OnMapReadyCallback, GoogleMap.OnInfoWindowClickListener {
    private lateinit var _googleMap:GoogleMap
    private val markers: ArrayList<Marker> = arrayListOf()
    private var _stations = listOf<Utils.StationInfo>()
    private lateinit var _view: View
    private var _onlyOneStationIsShown = false

    fun setView(view: View) {
        _view = view
    }

    override fun onMapReady(googleMap: GoogleMap) {
        _googleMap = googleMap
        _googleMap.mapType = GoogleMap.MAP_TYPE_NORMAL
        _googleMap.moveCamera(CameraUpdateFactory.newLatLngZoom(LatLng(Utils.lat,Utils.lng),
                Utils.minZoom))
        _googleMap.setOnInfoWindowClickListener(this)
        _googleMap.setOnMapLoadedCallback {
            SearchModel.instance.getAllStationInfo()
        }
    }

    /** Set stations after server response */
    fun setStations(stations: List<Utils.StationInfo>) {
        _stations = stations
        updateMap()
    }

    private fun updateMap() {
        if (this::_googleMap.isInitialized && _stations.isNotEmpty()) {
            removeMarker()
            _onlyOneStationIsShown = _stations.size == 1
            for (station in _stations) {
                addMarker(station)
            }
        }
    }

    private fun removeMarker() {
        if(markers.isNotEmpty()) {
            for (marker in markers) {
                marker.remove()
            }
        }
    }

    private fun addMarker(station: Utils.StationInfo) {
        val position = LatLng(station.lat, station.lng)
        val marker = _googleMap.addMarker(MarkerOptions().position(position).title(station.name))
        marker.snippet = "Code de station : ${station.code}"
        marker.tag = station.code
        if(_onlyOneStationIsShown) {
            _googleMap.moveCamera(CameraUpdateFactory.newLatLngZoom(position, Utils.focusZoom))
        }
        markers.add(marker)
    }

    /** Called when user selects a station from the map */
    override fun onInfoWindowClick(marker: Marker) {
        for(m in markers) {
            if(m == marker) {
                val bundle = bundleOf(Utils.StatsArg to marker.tag.toString().toInt())
                Navigation.findNavController(_view).navigate(R.id.action_navigation_search_to_navigation_stats,
                        bundle)
            }
        }
    }
}