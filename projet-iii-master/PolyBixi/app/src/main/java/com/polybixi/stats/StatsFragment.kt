package com.polybixi.stats

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.databinding.DataBindingUtil
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import com.github.aachartmodel.aainfographics.aachartcreator.AAChartView
import com.polybixi.R
import com.polybixi.databinding.FragmentStatsBinding
import com.polybixi.utils.Utils

/**
 * SPDX-License-Identifier: GPL-2.0-only
 * Copyright (c) 2020 Jean-Olivier Dalphond <jean-olivier.dalphond@polymtl.ca>
 */

class StatsFragment: Fragment() {
    lateinit var statsFragmentView: View

    override fun onCreateView(
            inflater: LayoutInflater,
            container: ViewGroup?,
            savedInstanceState: Bundle?
    ): View? {
        /** DataBinding */
        val binding: FragmentStatsBinding = DataBindingUtil.inflate(
                inflater, R.layout.fragment_stats, container, false
        )
        statsFragmentView = binding.root
        binding.viewModel = ViewModelProvider(this).get(StatsViewModel::class.java)
        val vm = (binding.viewModel) as StatsViewModel

        /** Passing Chart Object to ViewModel */
        vm.aaChartView = statsFragmentView.findViewById(R.id.chartView) as AAChartView

        /** Argument coming from Search Fragment / Navigation */
        var stationCode = arguments?.getInt(Utils.StatsArg)
        if (stationCode == 0 ) { stationCode = Utils.DefaultStationCode } else {
            vm.stationCode = stationCode.toString()
            vm.allStations = false
            vm.getData()
        }
        vm.stationCode = stationCode.toString()

        return statsFragmentView
    }
}