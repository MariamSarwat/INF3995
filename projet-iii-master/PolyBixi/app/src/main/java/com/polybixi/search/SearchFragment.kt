package com.polybixi.search

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.View.OnFocusChangeListener
import android.view.ViewGroup
import android.widget.EditText
import androidx.databinding.DataBindingUtil
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.DefaultItemAnimator
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.gms.common.GooglePlayServicesNotAvailableException
import com.google.android.gms.maps.MapView
import com.google.android.gms.maps.MapsInitializer
import com.polybixi.R
import com.polybixi.databinding.FragmentSearchBinding
import com.polybixi.utils.Utils
import com.polybixi.utils.OnItemClickListener

/**
 * SPDX-License-Identifier: GPL-2.0-only
 * Copyright (c) 2020 Samuel Charbonneau <samuel-3.charbonneau@polymtl.ca>
 */

class SearchFragment: Fragment() {
    private lateinit var searchFragmentView: View
    private lateinit var mMapView: MapView
    private lateinit var _vm: SearchViewModel

    override fun onResume() {
        super.onResume()
        mMapView.onResume()
    }

    override fun onDestroy() {
        super.onDestroy()
        mMapView.onDestroy()
    }

    override fun onLowMemory() {
        super.onLowMemory()
        mMapView.onLowMemory()
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        /** DataBinding */
        val binding: FragmentSearchBinding = DataBindingUtil.inflate(
            inflater, R.layout.fragment_search, container, false
        )
        searchFragmentView = binding.root
        binding.viewModel = ViewModelProvider(this).get(SearchViewModel::class.java)
        _vm = (binding.viewModel) as SearchViewModel

        /** Google Map */
        _vm.googleMapHandler().setView(searchFragmentView)
        mMapView = searchFragmentView.findViewById(R.id.mapView) as MapView
        try {
            MapsInitializer.initialize(this.activity)
        } catch (e: GooglePlayServicesNotAvailableException) {
            e.printStackTrace()
        }
        mMapView.onCreate(savedInstanceState)
        mMapView.getMapAsync(_vm.googleMapHandler())

        initializeRecycleView(searchFragmentView.findViewById(R.id.station_list) as RecyclerView)

        /** Set the focus state of the text box */
        searchFragmentView.findViewById<EditText>(R.id.search_box).onFocusChangeListener =
            OnFocusChangeListener { _, hasFocus ->
                _vm.setSearchBoxFocus(hasFocus)
            }

        return searchFragmentView
    }

    private fun initializeRecycleView(recyclerView: RecyclerView){
        recyclerView.layoutManager = LinearLayoutManager(activity)
        val listener: OnItemClickListener<Utils.StationInfo> =
                object : OnItemClickListener<Utils.StationInfo> {
                    override fun onItemClick(station: Utils.StationInfo) {
                        _vm.locateStation(station)
                    }
                }
        val adapter = StationsAdapter(listener)
        recyclerView.adapter = adapter
        SearchModel.instance.getStations().observe(viewLifecycleOwner, {
            it?.let(adapter::submitList)
        })
        recyclerView.itemAnimator = DefaultItemAnimator()
    }
}
