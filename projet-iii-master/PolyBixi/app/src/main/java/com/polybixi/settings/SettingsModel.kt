package com.polybixi.settings

import android.util.Log
import com.polybixi.utils.HTTPSService
import com.polybixi.utils.ToastService
import com.polybixi.utils.Utils
import java.lang.Exception

/**
 * SPDX-License-Identifier: GPL-2.0-only
 * Copyright (c) 2020 Jean-Olivier Dalphond <jean-olivier.dalphond@polymtl.ca>
 */

class SettingsModel {
    fun setServerAddress(address: String) {
        HTTPSService.setServerAddress(address)
    }
}