package com.polybixi.stats

import androidx.databinding.Bindable
import androidx.databinding.library.baseAdapters.BR
import com.github.aachartmodel.aainfographics.aachartcreator.*
import com.github.aachartmodel.aainfographics.aaoptionsmodel.*
import com.polybixi.R
import com.polybixi.utils.Utils
import com.polybixi.utils.ObservableViewModel
import com.polybixi.utils.PreferenceService
import java.util.*

/**
 * SPDX-License-Identifier: GPL-2.0-only
 * Copyright (c) 2020 Jean-Olivier Dalphond <jean-olivier.dalphond@polymtl.ca>
 */

class StatsViewModel: ObservableViewModel() {
    /** DataBinding private attributes */
    private var _requestCounter = 0
    private var _model = StatsModel.instance
    private var _hasData = false
    private var _stationCodeValid = false
    private var _typeRadioValue: Int = R.id.statsRadioUsage
    private var _periodRadioValue: Int = R.id.statsRadioHour

    /** Graph variables */
    private lateinit var aaChartModel: AAChartModel
    private lateinit var _aaChartView: AAChartView
    private var graphTitle = ""
    private var subtitle = ""
    var xLabel = ""
    var yLabel = ""
    var yAltLabel = ""

    fun updateGraphTitle() {
        subtitle = if (allStations) { Utils.GraphAllStations }
        else if (_model.requestType == Utils.RequestType.ERROR) { "" }
        else { "Station: ${_model.stationInfo.name}" }
        graphTitle = when (_model.requestType) {
            Utils.RequestType.USAGE -> "Données classées par: ${_model.requestPeriod.graphString}"
            Utils.RequestType.PREDICTION -> "Données classées par: ${_model.requestPeriod.graphString}"
            Utils.RequestType.ERROR -> Utils.GraphErrorTitle
        }
    }

    /** Graph styling */
    private var titleColor = ""
    private var backgroundColor = ""
    private var axesTextColor = ""
    private var barAndLineColor = ""
    private var dataLabelColor = ""
    private var dataLabelOutlineColor = ""
    private var barAndLineAltColor = ""
    private var style = AAStyle()
    private var subtitleStyle = AAStyle()
    private var dataLabels = AADataLabels()

    /** Unfortunately AAChart doesn't take R.color values
     * Converting the hex int to string is not time well spent
     * It would be a lot more elegant, but ... */
    private fun setGraphColors() {
        if (PreferenceService.isDarkTheme()) {
            titleColor = Utils.LighterGrey
            backgroundColor = Utils.Transparent
            axesTextColor = Utils.LighterGrey
            barAndLineColor = Utils.Blue
            barAndLineAltColor = Utils.DarkerBlue
            dataLabelColor = Utils.LighterGrey
            dataLabelOutlineColor = Utils.LighterGrey
        } else {
            titleColor = Utils.Black
            backgroundColor = Utils.Transparent
            axesTextColor = Utils.Black
            barAndLineColor = Utils.LightBlue
            barAndLineAltColor = Utils.DarkBlue
            dataLabelColor = Utils.DarkerGrey
            dataLabelOutlineColor = Utils.DarkerGrey
        }
        style.color(titleColor).fontSize(Utils.TitleSize)
        subtitleStyle.color(titleColor).fontSize(Utils.SubtitleSize)
        dataLabels.enabled(true)
        dataLabels.color(dataLabelColor)
        dataLabels.borderColor(dataLabelOutlineColor)
    }

    /** DataBinding */
    var aaChartView : AAChartView
        get() {
            return _aaChartView
        }
        set(value) {
            _aaChartView = value
        }

    var typeRadioValue: Int
        @Bindable get() {
            return _typeRadioValue
        }
        set (value) {
            if (value != _typeRadioValue) {
                _typeRadioValue = value
                if (_typeRadioValue == R.id.statsRadioUsage &&
                        (periodRadioValue == R.id.statsRadioTemperature
                                || periodRadioValue == R.id.statsRadioDay)) {
                    periodRadioValue = R.id.statsRadioHour
                } else if (_typeRadioValue != R.id.statsRadioUsage
                        && periodRadioValue == R.id.statsRadioMonth) {
                    periodRadioValue = R.id.statsRadioHour
                }
                notifyPropertyChanged(BR.typeRadioValue)
            }
        }

    var periodRadioValue: Int
        @Bindable get() {
            return _periodRadioValue
        }
        set(value) {
            if (value != _periodRadioValue) {
                _periodRadioValue = value
                notifyPropertyChanged(BR.periodRadioValue)
            }
        }

    init {
        periodRadioValue = R.id.statsRadioHour
        typeRadioValue = R.id.statsRadioUsage
        _model.setViewModel(this)
    }

    var allStations: Boolean
        @Bindable get() {
            return _model.allStations
        }
        set(value) {
            if (value != _model.allStations) {
                _model.allStations = value
                isStationCodeValid()
                notifyPropertyChanged(BR.allStations)
            }
        }

    var hasData: Boolean
        @Bindable get() {
            return _hasData
        }
        set(value) {
            if (value != _hasData) {
                _hasData = value
                notifyPropertyChanged(BR.hasData)
            }
        }

    var requestCounter: Int
        @Bindable get() {
            return _requestCounter
        }
        set(value) {
            if (value != _requestCounter) {
                _requestCounter = value
                notifyPropertyChanged(BR.requestCounter)
            }
        }

    var stationCode: String
        @Bindable get() {
            return _model.stationInfo.code.toString()
        }
        set(value) {
            if (value != _model.stationInfo.code.toString()) {
                if (value.isNotEmpty()) {
                    _model.stationInfo.code = value.toInt()
                    notifyPropertyChanged(BR.stationCode)
                }
            }
            isStationCodeValid()
        }

    var stationCodeValid: Boolean
        @Bindable get() { return _stationCodeValid }
        set (value) {
            if(value != _stationCodeValid) {
                _stationCodeValid = value || allStations
                notifyPropertyChanged(BR.stationCodeValid)
            }
        }

    /** Calls the Model's method to get data from server */
    fun getData() {
        when (periodRadioValue) {
            R.id.statsRadioHour -> { _model.requestPeriod = Utils.RequestPeriod.HOUR }
            R.id.statsRadioWeekday -> { _model.requestPeriod = Utils.RequestPeriod.WEEKDAY }
            R.id.statsRadioMonth -> { _model.requestPeriod = Utils.RequestPeriod.MONTH }
            R.id.statsRadioTemperature -> { _model.requestPeriod = Utils.RequestPeriod.TEMPERATURE }
            R.id.statsRadioDay -> { _model.requestPeriod = Utils.RequestPeriod.DAY }
        }
        when (typeRadioValue) {
            R.id.statsRadioUsage -> {
                _model.requestType = Utils.RequestType.USAGE
                _model.getUsageData()
            }
            R.id.statsRadioPrediction -> {
                _model.requestType = Utils.RequestType.PREDICTION
                _model.getPredictionData()
            }
            R.id.statsRadioError -> {
                _model.requestType = Utils.RequestType.ERROR
                _model.getErrorData()
            }
        }
    }

    /** Validator for station number */
    private fun isStationCodeValid() {
        stationCodeValid = _model.stationInfo.code in 0..10000
    }

    /** Graph generation methods */
    fun createUsageGraph(columnValues: ArrayList<Pair<String, Int>>) {
        setGraphColors()
        val xValues = arrayListOf<String>()
        val yValues = arrayListOf<Int>()
        columnValues.forEach{
            xValues.add(it.first)
            yValues.add(it.second)
        }
        val options = AAOptions()
        val legend = AALegend()
        val itemStyle = AAItemStyle()
        legend.itemStyle(itemStyle)
        options.legend(AALegend())
        val aaChartModel : AAChartModel = AAChartModel()
                .chartType(AAChartType.Column)
                .categories(xValues.toTypedArray())
                .title(graphTitle)
                .subtitle(subtitle)
                .subtitleStyle(subtitleStyle)
                .xAxisLabelsEnabled(true)
                .dataLabelsEnabled(true)
                .legendEnabled(false)
                .yAxisTitle(yLabel)
                .titleStyle(style)
                .backgroundColor(backgroundColor)
                .axesTextColor(axesTextColor)
                .series(arrayOf(
                        AASeriesElement()
                                .dataLabels(dataLabels)
                                .name(yLabel)
                                .color(barAndLineColor)
                                .data(yValues.toArray())
                ))
        aaChartView.aa_drawChartWithChartModel(aaChartModel)
    }

    fun createPredictionGraph(columnValues: ArrayList<Pair<String, Double>>){
        setGraphColors()
        val xValues = arrayListOf<String>()
        val yValues = arrayListOf<Double>()
        columnValues.forEach{
            xValues.add(it.first)
            yValues.add(it.second)
        }
        aaChartModel = AAChartModel()
            .chartType(AAChartType.Line)
            .title(graphTitle)
                .categories(xValues.toTypedArray())
            .subtitle(subtitle)
                .subtitleStyle(subtitleStyle)
            .xAxisLabelsEnabled(true)
            .legendEnabled(false)
            .yAxisTitle(yLabel)
            .titleStyle(style)
            .xAxisLabelsEnabled(true)
            .backgroundColor(backgroundColor)
            .axesTextColor(axesTextColor)
            .series(arrayOf(
                AASeriesElement()
                    .name(yLabel)
                    .dataLabels(dataLabels)
                    .color(barAndLineColor)
                    .data(yValues.toArray()),
            ))
        aaChartView.aa_drawChartWithChartModel(aaChartModel)
    }

    fun createErrorGraph(columnValues: ArrayList<Pair<String, Int>>, lineValues: ArrayList<Pair<String, Double>>) {
        setGraphColors()
        val xValues = arrayListOf<String>()
        val xAltValues = arrayListOf<String>()
        val yValues = arrayListOf<Int>()
        val yAltValues = arrayListOf<Double>()
        columnValues.forEach{
            xValues.add(it.first)
            yValues.add(it.second)
        }
        lineValues.forEach{
            xAltValues.add(it.first)
            yAltValues.add(it.second)
        }
        val options = AAOptions()
        val legend = AALegend()
        val itemStyle = AAItemStyle()
        legend.itemStyle(itemStyle)
        options.legend(AALegend())
        val aaChartModel : AAChartModel = AAChartModel()
            .categories(xValues.toTypedArray())
            .title(graphTitle)
            .subtitle(subtitle)
                .subtitleStyle(subtitleStyle)
            .xAxisLabelsEnabled(true)
            .dataLabelsEnabled(true)
            .legendEnabled(true)
            .yAxisTitle(yLabel)
            .titleStyle(style)
            .backgroundColor(backgroundColor)
            .axesTextColor(axesTextColor)
            .series(arrayOf(
                AASeriesElement()
                    .dataLabels(dataLabels)
                    .type(AAChartType.Line)
                    .name(yLabel)
                    .color(barAndLineColor)
                    .data(yAltValues.toArray())
                    .zIndex(1),
                AASeriesElement()
                    .dataLabels(dataLabels)
                    .type(AAChartType.Column)
                    .name(yAltLabel)
                    .color(barAndLineAltColor)
                    .data(yValues.toArray())
                    .zIndex(0)
            ))
        aaChartView.aa_drawChartWithChartModel(aaChartModel)
    }
}
