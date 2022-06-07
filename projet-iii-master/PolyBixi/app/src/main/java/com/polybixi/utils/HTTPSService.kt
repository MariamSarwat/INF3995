/*
 * SPDX-License-Identifier: GPL-2.0-only
 *
 * Copyright (c) 2020 Jean-Olivier Dalphond <jean-olivier.dalphond@polymtl.ca>
 *
 * Adapted from https://www.varvet.com/blog/kotlin-with-volley/
 *
 */

package com.polybixi.utils

import android.util.Log
import com.android.volley.AuthFailureError
import com.android.volley.Request
import com.android.volley.Response
import com.android.volley.toolbox.JsonArrayRequest
import com.android.volley.toolbox.JsonObjectRequest
import org.json.JSONArray
import org.json.JSONObject
import java.io.IOException
import java.security.KeyManagementException
import java.security.KeyStoreException
import java.security.NoSuchAlgorithmException
import java.security.cert.CertificateException
import java.util.*


/**
 * SPDX-License-Identifier: GPL-2.0-only
 * Copyright (c) 2020 Jean-Olivier Dalphond <jean-olivier.dalphond@polymtl.ca>
 * Adapted from https://www.varvet.com/blog/kotlin-with-volley/
 */
object HTTPSService {
    /** Server Address */
    fun setServerAddress(address: String) {
        Utils.serverIP = address
    }

    fun getServerBasePath(): String {
        return "https://" + Utils.serverIP + ":443/"
    }

    /** Main method to interact with Volley Library */
    @Throws(
            CertificateException::class,
            IOException::class,
            KeyStoreException::class,
            NoSuchAlgorithmException::class,
            KeyManagementException::class
    )
    fun request(
            method: Int,
            path: String,
            params: JSONObject,
            completionHandler: (response: JSONObject?, array: JSONArray?, statusCode: Int?) -> Unit
    ) {
        try {
            val jsonObjReq = object : JsonObjectRequest(
                    method, getServerBasePath() + path, params,
                    Response.Listener { response ->
                        when (response) {
                            is JSONObject -> completionHandler(response, null, 200)
                            is JSONArray -> completionHandler(null, response, 200)
                            else -> completionHandler(response, null, 200)
                        }
                    },
                    Response.ErrorListener { error ->
                        val code = error.networkResponse?.statusCode
                        Log.w(Utils.TAG, "Request fail status code is: $code")
                        Log.w(Utils.TAG, "error is: $error")
                        completionHandler(null, null, code)
                    }) {
                @Throws(AuthFailureError::class)
                override fun getHeaders(): Map<String, String> {
                    val headers = HashMap<String, String>()
                    headers["Content-Type"] = "application/json"
                    return headers
                }
            }
            HTTPSRequestHandler.instance?.addToRequestQueue(jsonObjReq)
        } catch (e: Exception) {
            Log.e(Utils.TAG, "Exception caught in HTTP request: $e")
        }
    }

    /** Same method as above, to get a JSONArray rather than a JSONObject */
    @Throws(
            CertificateException::class,
            IOException::class,
            KeyStoreException::class,
            NoSuchAlgorithmException::class,
            KeyManagementException::class
    )
    fun requestStatusArray(completionHandler: (array: JSONArray?) -> Unit) {
        try {
            val jsonArrReq = object: JsonArrayRequest(Method.GET,
                    getServerBasePath() + "status", JSONArray(),
                    Response.Listener { response ->
                        when (response) {
                            is JSONArray -> completionHandler(response)
                        }
                    }, Response.ErrorListener { error ->
                        if (error.networkResponse != null) {
                            val jsonError = JSONArray(String(error.networkResponse.data))
                            completionHandler(jsonError)
                        } else {
                            Log.e(Utils.TAG, Utils.StatusErrorMessage)
                            completionHandler(null)
                        }
            }) {
                @Throws(AuthFailureError::class)
                override fun getHeaders(): Map<String, String> {
                    val headers = HashMap<String, String>()
                    headers["Content-Type"] = "application/json"
                    return headers
                }
            }
            HTTPSRequestHandler.instance?.addToRequestQueue(jsonArrReq)
        } catch (err: Exception) {
            Log.e(Utils.TAG, Utils.StatusErrorMessage)
            completionHandler(null)
        }
    }

    /** Simplifies coding in calling classes */
    fun get(
            path: String,
            params: JSONObject,
            completionHandler: (response: JSONObject?, array: JSONArray?, statusCode: Int?) -> Unit
    ) {
        request(Request.Method.GET, path, params, completionHandler)
    }

    fun put(
            path: String,
            params: JSONObject,
            completionHandler: (response: JSONObject?, array: JSONArray?, statusCode: Int?) -> Unit
    ) {
        request(Request.Method.PUT, path, params, completionHandler)
    }

    fun post(
            path: String,
            params: JSONObject,
            completionHandler: (response: JSONObject?, array: JSONArray?, statusCode: Int?) -> Unit
    ) {
        request(Request.Method.POST, path, params, completionHandler)
    }
}