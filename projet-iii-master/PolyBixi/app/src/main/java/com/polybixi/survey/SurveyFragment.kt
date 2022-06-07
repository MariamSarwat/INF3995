package com.polybixi.survey

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
import com.polybixi.databinding.FragmentSurveyBinding
import com.polybixi.utils.Utils
import com.polybixi.utils.PreferenceService

/**
 * SPDX-License-Identifier: GPL-2.0-only
 * Copyright (c) 2020 Jean-Olivier Dalphond <jean-olivier.dalphond@polymtl.ca>
 */

class SurveyFragment: Fragment() {
    private lateinit var surveyFragmentView: View

    override fun onCreateView(
            inflater: LayoutInflater,
            container: ViewGroup?,
            savedInstanceState: Bundle?
    ): View? {
        /** Binding to ViewModel */
        val binding: FragmentSurveyBinding = DataBindingUtil.inflate(
                inflater, R.layout.fragment_survey, container, false)
        surveyFragmentView = binding.root
        binding.viewModel = ViewModelProvider(this).get(SurveyViewModel::class.java)
        val vm = (binding.viewModel) as SurveyViewModel
        vm.setView(surveyFragmentView)
        vm._surveyAlreadySent = PreferenceService.getSurveyPreference()
        return surveyFragmentView
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        offKeyboardAreaListen(surveyFragmentView)
    }

    /** Called when use presses outside the keyboard area */
    private fun hideSoftKeyboard(activity: Activity) {
        val inputMethodManager = activity.getSystemService(
                Activity.INPUT_METHOD_SERVICE) as InputMethodManager
        try {
            inputMethodManager.hideSoftInputFromWindow(
                    activity.currentFocus!!.windowToken, 0)
        } catch (err: Exception) {
            Log.i(Utils.TAG, "Error hiding keyboard: $err")
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