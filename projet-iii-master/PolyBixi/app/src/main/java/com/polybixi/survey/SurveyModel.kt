package com.polybixi.survey

import com.polybixi.utils.Utils
import com.polybixi.utils.HTTPSService
import org.json.JSONObject

/**
 * SPDX-License-Identifier: GPL-2.0-only
 * Copyright (c) 2020 Jean-Olivier Dalphond <jean-olivier.dalphond@polymtl.ca>
 */

class SurveyModel {
    var surveyData: Utils.SurveyData = Utils.SurveyData()

    /** Sends survey data to server
     * @param: callback function
     */
    fun sendSurvey(callback: (code: Int) -> Unit) {
        val params = JSONObject()
        params.put("courriel", surveyData.email)
        params.put("prenom", surveyData.firstName)
        params.put("nom", surveyData.lastName)
        params.put("age", surveyData.age)
        params.put("interet", surveyData.interest)
        HTTPSService.put("sondage", params) { _, _, statusCode ->
            if (statusCode != null) { callback(statusCode) }
                else { callback(404) }
        }
    }
}
