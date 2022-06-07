package com.polybixi.settings

import android.text.TextUtils
import android.util.Log
import android.view.View
import androidx.databinding.Bindable
import androidx.databinding.library.baseAdapters.BR
import androidx.navigation.Navigation
import com.polybixi.R
import com.polybixi.utils.Utils
import com.polybixi.utils.ObservableViewModel
import com.polybixi.utils.PreferenceService
import com.polybixi.utils.ToastService

/**
 * SPDX-License-Identifier: GPL-2.0-only
 * Copyright (c) 2020 Jean-Olivier Dalphond <jean-olivier.dalphond@polymtl.ca>
 */

class SettingsViewModel: ObservableViewModel() {
    private var _serverAddress = Utils.serverIP
    private var _model: SettingsModel = SettingsModel()
    private lateinit var _view: View

    /** Reference for the View, important for Navigation */
    fun setView(view: View) {
        _view = view
    }

    /** Databinding variables */
    var serverAddress: String
        @Bindable get() {
            return _serverAddress
        }
        set(value) {
            if (value != _serverAddress) {
                _serverAddress = value
                notifyPropertyChanged(BR.serverAddress)
                notifyPropertyChanged(com.polybixi.BR.addressValid)
            }
        }
    val addressValid: Boolean
        @Bindable get() {
            return isInputValid()
        }

    fun saveServerAddress() {
        if (!isInputValid()) {
            ToastService.print(Utils.SettingsWrongFormat, true)
        } else {
            _model.setServerAddress(serverAddress)
            ToastService.print(Utils.SettingsAddressSaved)
        }
    }

    /** Validator for IP Address format */
    @Throws(Exception::class)
    fun isInputValid(): Boolean {
        return !TextUtils.isEmpty(serverAddress) &&
                android.util.Patterns.IP_ADDRESS.matcher(serverAddress).matches()
    }
}