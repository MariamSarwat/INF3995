package com.polybixi.utils

import android.content.Context
import android.content.res.Configuration
import android.util.Log
import java.lang.Exception

/**
 * SPDX-License-Identifier: GPL-2.0-only
 * Copyright (c) 2020 Jean-Olivier Dalphond <jean-olivier.dalphond@polymtl.ca>
 */

object PreferenceService {
    private lateinit var context: Context

    fun setContext(_context: Context) {
        context = _context
    }

    /** Retrieves Android Preference value for Survey Fragment */
    fun getSurveyPreference(): Boolean {
        try {
            val pref = context.getSharedPreferences("PolyBixi",
                    Context.MODE_PRIVATE).getBoolean("surveyAlreadySubmitted", false)
            return pref
        } catch (err: Exception) {
            Log.i(Utils.TAG, "error getting preference")
        }
        return false
    }

    /** Sets the above value */
    fun setSurveyPreference(value: Boolean) {
        try {
            val sharedPref =
                    context.getSharedPreferences("PolyBixi", Context.MODE_PRIVATE) ?: return
            with (sharedPref.edit()) {
                putBoolean("surveyAlreadySubmitted", value)
                apply()
            }
        } catch (err: Exception) {
            Log.i(Utils.TAG, "error setting survey preference")
        }
    }

    /** Used for graph styling */
    fun isDarkTheme(): Boolean {
        return context.resources.configuration.uiMode and
                Configuration.UI_MODE_NIGHT_MASK == Configuration.UI_MODE_NIGHT_YES
    }
}