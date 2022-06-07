package com.polybixi

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.navigation.fragment.NavHostFragment
import androidx.navigation.ui.AppBarConfiguration
import androidx.navigation.ui.setupActionBarWithNavController
import androidx.navigation.ui.setupWithNavController
import com.google.android.material.bottomnavigation.BottomNavigationView
import com.polybixi.utils.*

/**
 * SPDX-License-Identifier: GPL-2.0-only
 * Copyright (c) 2020 Jean-Olivier Dalphond <jean-olivier.dalphond@polymtl.ca>,
 * Samuel Charbonneau <samuel-3.charbonneau@polymtl.ca
 */

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        /** Passing context to services */
        ToastService.setContext(this)
        PreferenceService.setContext(this)

        setContentView(R.layout.activity_main)
        val navView: BottomNavigationView = findViewById(R.id.nav_view)
        val navHostFragment =
                supportFragmentManager.findFragmentById(R.id.nav_host_fragment) as NavHostFragment
        val navController = navHostFragment.navController
        val appBarConfiguration = AppBarConfiguration(
                setOf(
                        R.id.navigation_survey, R.id.navigation_search,
                        R.id.navigation_stats, R.id.navigation_settings
                )
        )
        setupActionBarWithNavController(navController, appBarConfiguration)
        navView.setupWithNavController(navController)
    }

    override fun onResume() {
        super.onResume()
        EngineStatusHandler.instance?.onResume()
    }

    override fun onPause() {
        EngineStatusHandler.instance?.onPause()
        super.onPause()
    }

    override fun onDestroy() {
        EngineStatusHandler.instance?.onPause()
        super.onDestroy()
    }
}