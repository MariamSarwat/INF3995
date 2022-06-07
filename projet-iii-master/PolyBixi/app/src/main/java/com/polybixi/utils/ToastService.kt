package com.polybixi.utils

import android.content.Context
import android.util.Log
import android.widget.Toast
import java.util.logging.Handler

/**
 * SPDX-License-Identifier: GPL-2.0-only
 * Copyright (c) 2020 Jean-Olivier Dalphond <jean-olivier.dalphond@polymtl.ca>
 */

object ToastService {
    private lateinit var context: Context

    fun setContext(input: Context) {
        context = input
    }

    /** Used to print general messages to Android UI */
    fun print(msg: String, long: Boolean? = false) {
        if (long!!) {
            Toast.makeText(context, msg, Toast.LENGTH_LONG).show()
        } else {
            Toast.makeText(context, msg, Toast.LENGTH_SHORT).show()
        }
    }
}
