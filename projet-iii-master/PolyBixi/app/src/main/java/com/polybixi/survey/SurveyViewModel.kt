package com.polybixi.survey

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
import java.lang.Integer.parseInt

/**
 * SPDX-License-Identifier: GPL-2.0-only
 * Copyright (c) 2020 Jean-Olivier Dalphond <jean-olivier.dalphond@polymtl.ca>
 */

class SurveyViewModel : ObservableViewModel() {
    private var _model = SurveyModel()
    private lateinit var _view: View
    var _surveyAlreadySent: Boolean = false

    /** Binding to View */
    fun setView(view: View) {
        _view = view
    }

    /** DataBinding */
    val surveyAlreadySent: Boolean
        @Bindable get() {
            return _surveyAlreadySent
        }

    val firstNameValid: Boolean
        @Bindable get() {
            return isNameValid(_model.surveyData.firstName)
        }
    var firstName: String
        @Bindable get() {
            return _model.surveyData.firstName
        }
        set(value) {
            if (value != _model.surveyData.firstName) {
                _model.surveyData.firstName = value
                notifyPropertyChanged(BR.firstNameValid)
            }
        }

    val lastNameValid: Boolean
        @Bindable get() {
            return isNameValid(_model.surveyData.lastName)
        }
    var lastName: String
        @Bindable get() {
            return _model.surveyData.lastName
        }
        set(value) {
            if (value != _model.surveyData.lastName) {
                _model.surveyData.lastName = value
                notifyPropertyChanged(BR.lastNameValid)

            }
        }
    val ageValid: Boolean
        @Bindable get() {
            return isAgeValid(_model.surveyData.age)
        }
    var age: String
        @Bindable get() {
            return _model.surveyData.age.toString()
        }
        set(value) {
            if (value != _model.surveyData.age.toString()) {
                if (value == "")
                    _model.surveyData.age = 0
                else
                    _model.surveyData.age = parseInt(value)
                notifyPropertyChanged(BR.ageValid)
            }
        }
    val emailValid: Boolean
        @Bindable get() {
            return isEmailValid(_model.surveyData.email)
        }

    var email: String
        @Bindable get() {
            return _model.surveyData.email
        }
        set(value) {
            if (value != _model.surveyData.email) {
                _model.surveyData.email = value
                notifyPropertyChanged(BR.emailValid)
            }
        }

    var interest: Boolean
        @Bindable get() {
            return _model.surveyData.interest
        }
        set(value) {
            if (value != _model.surveyData.interest) {
                _model.surveyData.interest = value
            }
        }

    fun resetSurvey() {
        _surveyAlreadySent = false
        PreferenceService.setSurveyPreference(false)
        notifyPropertyChanged(BR.surveyAlreadySent)
    }

    /** Sends survey data to Model */
    fun sendSurvey() {
        if (emailValid && firstNameValid && lastNameValid && ageValid) {
            try {
                _model.sendSurvey(afterSend)
            } catch (err: Error) {
                Log.e(Utils.TAG, "An error occured : $err")
            }
        } else {
            ToastService.print(Utils.SurveyCheckFields, true)
        }
    }

    /** Callback method when server responded to Model */
    private val afterSend: (Int) -> Unit = { msg ->
        Log.i(Utils.TAG, "status code returned : $msg")
        when (msg) {
            200 -> {
                ToastService.print(Utils.SurveySent)
                _surveyAlreadySent = true
                PreferenceService.setSurveyPreference(true)
                notifyPropertyChanged(BR.surveyAlreadySent)
            }
            400 -> { ToastService.print(Utils.SurveyContentError,true) }
            else -> { ToastService.print(Utils.ServerUnknownError, true) }
        }
    }

    /** Called when has sent Survey Data and goes to Map Fragment */
    fun navigateToSearch() {
        Navigation.findNavController(_view).navigate(R.id.action_navigation_survey_to_navigation_search)
    }

    /** User input validators */
    private fun isEmailValid(email: String): Boolean {
        return if (TextUtils.isEmpty(email)) {
            false
        } else {
            android.util.Patterns.EMAIL_ADDRESS.matcher(email).matches()
        }
    }

    private fun isNameValid(name: String): Boolean {
        return !(TextUtils.isEmpty(name) || name.length > 25)
    }

    private fun isAgeValid(age: Int): Boolean {
        return age in 1..150
    }
}