package com.polybixi.utils

import androidx.databinding.ViewDataBinding
import androidx.databinding.library.baseAdapters.BR
import androidx.recyclerview.widget.RecyclerView

/**
 * SPDX-License-Identifier: GPL-2.0-only
 * Copyright (c) 2020 Samuel Charbonneau <samuel-3.charbonneau@polymtl.ca>
 */

class DataBindingViewHolder<T>(private val binding: ViewDataBinding):
        RecyclerView.ViewHolder(binding.root) {

    fun bind(item: T, listener: OnItemClickListener<T>) {
        binding.setVariable(BR.item, item)
        binding.executePendingBindings()
        itemView.setOnClickListener { listener.onItemClick(item) }
    }
}