package com.polybixi.settings

import android.app.Activity
import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.view.inputmethod.InputMethodManager
import androidx.constraintlayout.widget.ConstraintLayout
import androidx.databinding.DataBindingUtil
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import com.polybixi.R
import com.polybixi.databinding.FragmentSettingsBinding
import com.polybixi.utils.Utils

/**
 * SPDX-License-Identifier: GPL-2.0-only
 * Copyright (c) 2020 Jean-Olivier Dalphond <jean-olivier.dalphond@polymtl.ca>
 */

class SettingsFragment: Fragment() {
    lateinit var settingsFragmentView: View

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        /** DataBinding with ViewModel */
        val binding: FragmentSettingsBinding = DataBindingUtil.inflate(
            inflater, R.layout.fragment_settings, container, false)
        settingsFragmentView = binding.root
        binding.viewModel = ViewModelProvider(this).get(SettingsViewModel::class.java)
        ((binding.viewModel) as SettingsViewModel).setView(settingsFragmentView)
        return settingsFragmentView
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        offKeyboardAreaListen(settingsFragmentView)
    }

    /** Called when use presses outside the keyboard area */
    private fun hideSoftKeyboard(activity: Activity) {
        val inputMethodManager = activity.getSystemService(
            Activity.INPUT_METHOD_SERVICE) as InputMethodManager
        try {
            inputMethodManager.hideSoftInputFromWindow(
                    activity.currentFocus!!.windowToken, 0)
        } catch (err: Exception) {
            Log.w(Utils.TAG, "Error hiding keyboard: $err")
        }
    }

    private fun offKeyboardAreaListen(view: View) {
        if (view is ConstraintLayout) {
            view.setOnTouchListener { v, _ ->
                v.performClick()
                hideSoftKeyboard(this.requireActivity())
                false
            }
        }
    }
}