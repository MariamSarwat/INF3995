package com.polybixi.utils

import android.os.Handler
import android.os.Looper
import android.util.Log

class EngineStatusHandler {
    private var getStatusHandler: Handler = Handler(Looper.getMainLooper())
    private val getEngineStatus = object : Runnable {
        override fun run() {
            getStatus()
            getStatusHandler.postDelayed(this, Utils.StatusTimerInterval)
        }
    }

    fun onResume(){
        getStatusHandler.post(getEngineStatus)
    }

    fun onPause(){
        getStatusHandler.removeCallbacks(getEngineStatus)
    }

    /** Obtains and documents Data Engines' status from Server */
    fun getStatus() {
        HTTPSService.requestStatusArray { engines ->
            if (engines != null) {
                var toast = "Veuillez contacter un administrateur: engin(s) #"
                var allUp = true
                for (i in 0 until engines!!.length()) {
                    if (engines[i] != true) {
                        var engine = 0
                        /** Array is upside down */
                        when (i) {
                            0 -> engine = 3
                            1 -> engine = 2
                            2 -> engine = 1
                        }
                        Log.w(Utils.TAG, "Engine #${engine} is DOWN!")
                        toast += "$engine, "
                        allUp = false
                    }
                }
                if(allUp) {
                    Log.i(Utils.TAG, Utils.StatusAllUP)
                } else {
                    ToastService.print("$toast en problème!",true)
                }
            } else {
                ToastService.print(Utils.ServerUnknownError, true)
            }
        }
    }

    /** Singleton */
    companion object {
        @get:Synchronized var instance: EngineStatusHandler? = EngineStatusHandler()
            private set
    }
}