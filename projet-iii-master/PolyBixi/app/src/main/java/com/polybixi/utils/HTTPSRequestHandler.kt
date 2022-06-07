package com.polybixi.utils

import android.app.Application
import com.android.volley.DefaultRetryPolicy
import com.android.volley.Request
import com.android.volley.RequestQueue
import com.android.volley.toolbox.HurlStack
import com.android.volley.toolbox.Volley
import com.polybixi.R
import java.io.BufferedInputStream
import java.io.IOException
import java.io.InputStream
import java.security.KeyManagementException
import java.security.KeyStore
import java.security.KeyStoreException
import java.security.NoSuchAlgorithmException
import java.security.cert.CertificateException
import java.security.cert.CertificateFactory
import java.security.cert.X509Certificate
import javax.net.ssl.SSLContext
import javax.net.ssl.SSLSocketFactory
import javax.net.ssl.TrustManagerFactory

/**
 * Singleton to manage HTTP request queue and interaction with server and data engines
 * Uses Volley Library 1.1.1
 */

class HTTPSRequestHandler: Application() {
    override fun onCreate() {
        super.onCreate()
        instance = this
    }

    private var _requestQueue: RequestQueue? = null
    private val requestQueue: RequestQueue?
        get() {
            if (_requestQueue === null) {
                _requestQueue = Volley.newRequestQueue(applicationContext,
                        HurlStack(null, getSocketFactory()))
            }
            return _requestQueue
        }

    fun <T> addToRequestQueue(request: Request<T>) {
        request.tag = Utils.TAG
        request.retryPolicy = DefaultRetryPolicy(
                20000, 0,
                DefaultRetryPolicy.DEFAULT_BACKOFF_MULT)
        requestQueue?.add(request)
    }

    /** Used to negociate SSL connection to Traefik */
    @Throws(
            CertificateException::class,
            IOException::class,
            KeyStoreException::class,
            NoSuchAlgorithmException::class,
            KeyManagementException::class
    ) fun getSocketFactory(): SSLSocketFactory? {
        val cf = CertificateFactory.getInstance("X.509")
        val caInput: InputStream =
                BufferedInputStream(applicationContext.resources.openRawResource(R.raw.rootca))
        val ca: X509Certificate = caInput.use {
            cf.generateCertificate(it) as X509Certificate
        }
        val keyStore =
                KeyStore.getInstance(KeyStore.getDefaultType()).apply {
                    load(null, null)
                    setCertificateEntry("ca", ca)
                }
        val tmf: TrustManagerFactory =
                TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm()
                ).apply {
                    init(keyStore)
                }
        val sslContext: SSLContext = SSLContext.getInstance("TLS").apply {
            init(null, tmf.trustManagers, null)
        }
        return sslContext.socketFactory
    }

    /** Singleton */
    companion object {
        @get:Synchronized var instance: HTTPSRequestHandler? = null
            private set
    }
}