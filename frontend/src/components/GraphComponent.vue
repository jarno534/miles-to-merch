<template>
  <Line :data="chartData" :options="chartOptions" />
</template>

<script>
import { Line } from "vue-chartjs";
import { settings } from "../settings";
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Filler,
} from "chart.js";

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Filler
);

export default {
  name: "GraphComponent",
  components: { Line },
  props: {
    activityData: { type: Object, required: true },
    options: { type: Object, required: true },
  },
  emits: ["autorange-updated"],
  methods: {
    hexToRgba(hex, alpha = 0.3) {
      if (!hex || hex.length < 7) return `rgba(200, 200, 200, ${alpha})`;
      const r = parseInt(hex.slice(1, 3), 16);
      const g = parseInt(hex.slice(3, 5), 16);
      const b = parseInt(hex.slice(5, 7), 16);
      return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    },
    formatPace(seconds) {
      if (isNaN(seconds) || !isFinite(seconds) || seconds <= 0) return "—";
      const minutes = Math.floor(seconds / 60);
      const remainingSeconds = Math.round(seconds % 60);
      return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`;
    },
  },
  computed: {
    processedData() {
      const dataSourceKey = this.options.selectedDataSource;
      let dataStream = [];
      let yAxisLabel = "";
      let yTickFormatter = (value) => value.toLocaleString();
      let yAxisReverse = false;

      const isImperial = settings.units === "imperial";

      const streamLabels = {
        heartrate: "Heart Rate (bpm)",
        velocity_smooth: `Speed (${isImperial ? "mph" : "km/h"})`,
        altitude: `Altitude (${isImperial ? "ft" : "m"})`,
        pace: `Pace (${isImperial ? "min/mi" : "min/km"})`,
        cadence: "Cadence (rpm)",
        watts: "Power (W)",
      };

      yAxisLabel = streamLabels[dataSourceKey] || "";

      if (this.activityData && this.activityData.streams) {
        const speedStream =
          this.activityData.streams.velocity_smooth?.data || [];
        if (dataSourceKey === "pace") {
          const paceConversionFactor = isImperial ? 1.60934 : 1;
          dataStream = speedStream.map((speed) => {
            if (speed < 0.5) return null;
            const paceInSeconds = (1000 / speed) * paceConversionFactor;
            return Math.min(paceInSeconds, 1200);
          });
          yTickFormatter = (value) => this.formatPace(value);
          yAxisReverse = true;
        } else if (dataSourceKey === "velocity_smooth") {
          const speedConversionFactor = isImperial ? 2.23694 : 3.6;
          dataStream = speedStream.map((speed) =>
            parseFloat((speed * speedConversionFactor).toFixed(1))
          );
        } else if (dataSourceKey === "altitude") {
          const altitudeStream = this.activityData.streams.altitude?.data || [];
          const altConversionFactor = isImperial ? 3.28084 : 1;
          dataStream = altitudeStream.map((alt) =>
            Math.round(alt * altConversionFactor)
          );
        } else {
          dataStream = this.activityData.streams[dataSourceKey]?.data || [];
        }
      }

      const windowSize = 5;
      const halfWindow = Math.floor(windowSize / 2);
      const smoothedStream = dataStream.map((_, index) => {
        const start = Math.max(0, index - halfWindow);
        const end = Math.min(dataStream.length, index + halfWindow + 1);
        const window = dataStream
          .slice(start, end)
          .filter((v) => typeof v === "number" && isFinite(v));

        if (window.length === 0) {
          return null;
        }

        const sum = window.reduce((a, b) => a + b, 0);
        return sum / window.length;
      });
      return {
        dataStream: smoothedStream,
        yAxisLabel,
        yTickFormatter,
        yAxisReverse,
      };
    },

    chartData() {
      if (!this.activityData?.streams) return { datasets: [] };
      const isImperial = settings.units === "imperial";
      const distConversionFacter = isImperial ? 0.000621371 : 0.001;
      const distanceStream = (
        this.activityData.streams.distance?.data || []
      ).map((d) => d * distConversionFacter);

      const { dataStream, yAxisLabel } = this.processedData;

      const mainDataPoints = dataStream.map((value, index) => ({
        x: distanceStream[index],
        y: value,
      }));

      const datasets = [];

      if (
        this.options.showAltitudeInBackground &&
        this.options.selectedDataSource !== "altitude" &&
        this.activityData.streams.altitude
      ) {
        const altConversionFactor = isImperial ? 3.28084 : 1;
        const altitudeDataPoints = this.activityData.streams.altitude.data.map(
          (value, index) => ({
            x: distanceStream[index],
            y: value * altConversionFactor,
          })
        );
        datasets.push({
          label: "Altitude",
          data: altitudeDataPoints,
          backgroundColor: "rgba(200, 200, 200, 0.4)",
          borderColor: "transparent",
          fill: true,
          pointRadius: 0,
          yAxisID: "y1",
          order: 2,
        });
      }

      datasets.push({
        label: yAxisLabel,
        data: mainDataPoints,
        backgroundColor: this.options.transparentFill
          ? "transparent"
          : this.hexToRgba(this.options.fillColor),
        borderColor: this.options.lineColor,
        fill:
          this.options.selectedDataSource === "pace"
            ? { target: "start" }
            : true,
        tension: 0.4,
        pointRadius: 0,
        borderWidth: this.options.lineThickness,
        yAxisID: "y",
        order: 1,
        spanGaps: true,
      });

      return { datasets };
    },

    chartOptions() {
      const { yTickFormatter, yAxisLabel, yAxisReverse } = this.processedData;
      const isImperial = settings.units === "imperial";
      const distConversionFacter = isImperial ? 0.000621371 : 0.001;
      const distanceStream = this.activityData.streams.distance?.data || [0];
      const maxDistance =
        (distanceStream[distanceStream.length - 1] || 0) * distConversionFacter;

      const yAxisOptions = {
        reverse: yAxisReverse,
        display: this.options.showYAxisTitle || this.options.showYAxisLabels,
        grid: { display: this.options.showGrid },
        ticks: {
          display: this.options.showYAxisLabels,
          maxTicksLimit: this.options.yAxisTicks,
          font: { size: this.options.tickFontSize },
          callback: yTickFormatter,
        },
        title: {
          display: this.options.showYAxisTitle,
          text: yAxisLabel,
          font: { size: this.options.titleFontSize },
        },
      };

      if (
        typeof this.options.yAxisMin === "number" &&
        isFinite(this.options.yAxisMin)
      ) {
        yAxisOptions.min = this.options.yAxisMin;
      }
      if (
        typeof this.options.yAxisMax === "number" &&
        isFinite(this.options.yAxisMax)
      ) {
        yAxisOptions.max = this.options.yAxisMax;
      }

      return {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            type: "linear",
            display:
              this.options.showXAxisLabels || this.options.showXAxisTitle,
            max: maxDistance,
            grid: { display: this.options.showGrid },
            ticks: {
              display: this.options.showXAxisLabels,
              maxTicksLimit: this.options.xAxisTicks,
              font: { size: this.options.tickFontSize },
              callback: function (value) {
                if (value % 1 === 0) {
                  return value;
                }
                return null;
              },
            },
            title: {
              display: this.options.showXAxisTitle,
              text: `Distance (${isImperial ? "mi" : "km"})`,
            },
          },
          y: yAxisOptions,
          y1: {
            display:
              (this.options.showY1AxisTitle || this.options.showY1AxisLabels) &&
              this.options.showAltitudeInBackground &&
              this.options.selectedDataSource !== "altitude",
            position: "right",
            grid: { display: false },
            ticks: {
              display: this.options.showY1AxisLabels,
              maxTicksLimit: 5,
              font: {
                size: this.options.tickFontSize
                  ? this.options.tickFontSize - 2
                  : 10,
              },
            },
            title: {
              display: this.options.showY1AxisTitle,
              text: `Altitude (${isImperial ? "ft" : "m"})`, // Dynamisch label
              font: { size: this.options.titleFontSize },
            },
          },
        },
        plugins: {
          legend: { display: false },
          title: {
            display: this.options.showLegend,
            text: yAxisLabel,
            position: "top",
            align: "end",
            padding: { bottom: 10 },
          },
          tooltip: { enabled: false },
        },
      };
    },
  },
};
</script>
