<template>
  <Line :data="chartData" :options="chartOptions" />
</template>

<script>
import { Line } from "vue-chartjs";
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

      const streamLabels = {
        heartrate: "Heart Rate (bpm)",
        velocity_smooth: "Speed (km/h)",
        altitude: "Altitude (m)",
        pace: "Pace (min/km)",
        cadence: "Cadence (rpm)",
        watts: "Power (W)",
      };

      yAxisLabel = streamLabels[dataSourceKey] || "";

      if (this.activityData && this.activityData.streams) {
        if (dataSourceKey === "pace") {
          const speedStream =
            this.activityData.streams.velocity_smooth?.data || [];
          const maxPaceSeconds = 800;

          dataStream = speedStream.map((speed) => {
            if (speed < 0.5) return null;
            const paceInSeconds = 1000 / speed;
            return Math.min(paceInSeconds, maxPaceSeconds);
          });

          yTickFormatter = (value) => this.formatPace(value);
          yAxisReverse = true;
        } else if (dataSourceKey === "velocity_smooth") {
          const speedStream =
            this.activityData.streams.velocity_smooth?.data || [];
          dataStream = speedStream.map((speed) =>
            parseFloat((speed * 3.6).toFixed(1))
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
      const distanceStream = this.activityData.streams.distance?.data || [];
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
        const altitudeDataPoints = this.activityData.streams.altitude.data.map(
          (value, index) => ({
            x: distanceStream[index],
            y: value,
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
          this.options.selectedDataSource === "pace" ? { target: "end" } : true,
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
      const distanceStream = this.activityData.streams.distance?.data || [0];
      const maxDistance = distanceStream[distanceStream.length - 1] || 0;

      const rawStep = maxDistance / this.options.xAxisTicks;
      const niceSteps = [
        100, 250, 500, 1000, 2000, 2500, 5000, 10000, 25000, 50000,
      ];
      const stepSize =
        niceSteps.find((step) => step >= rawStep) ||
        niceSteps[niceSteps.length - 1];

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
              stepSize: stepSize,
              font: { size: this.options.tickFontSize },
              callback: function (value, index, ticks) {
                if (index === ticks.length - 1) {
                  return null;
                }
                const km = value / 1000;
                return km.toLocaleString();
              },
            },
            title: {
              display: this.options.showXAxisTitle,
              text: "Distance (km)",
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
              text: "Altitude (m)",
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
