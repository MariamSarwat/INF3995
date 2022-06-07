package com.polybixi.search

import androidx.recyclerview.widget.DiffUtil
import com.polybixi.utils.DataBindingAdapter
import com.polybixi.utils.Utils
import com.polybixi.R
import com.polybixi.utils.OnItemClickListener

/**
 * SPDX-License-Identifier: GPL-2.0-only
 * Copyright (c) 2020 Samuel Charbonneau <samuel-3.charbonneau@polymtl.ca>
 */

class StationsAdapter(listener: OnItemClickListener<Utils.StationInfo>):
        DataBindingAdapter<Utils.StationInfo>(DiffCallback(), listener) {
    class DiffCallback: DiffUtil.ItemCallback<Utils.StationInfo>() {
        override fun areItemsTheSame(oldItem: Utils.StationInfo, newItem: Utils.StationInfo):
                Boolean {
            return oldItem == newItem
        }

        override fun areContentsTheSame(oldItem: Utils.StationInfo, newItem: Utils.StationInfo):
                Boolean {
            return oldItem.name == newItem.name &&
                    oldItem.code == newItem.code &&
                    oldItem.lat == newItem.lat &&
                    oldItem.lng == newItem.lng
        }
    }

    override fun getItemViewType(position: Int) = R.layout.layout_station_search
}