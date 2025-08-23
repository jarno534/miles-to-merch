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
  methods: {
    hexToRgba(hex, alpha = 0.3) {
      if (!hex || hex.length < 7) return `rgba(200, 200, 200, ${alpha})`;
      const r = parseInt(hex.slice(1, 3), 16);
      const g = parseInt(hex.slice(3, 5), 16);
      const b = parseInt(hex.slice(5, 7), 16);
      return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    },
  },
  computed: {
    chartData() {
      if (!this.activityData || !this.activityData.streams) {
        return { datasets: [] };
      }

      const dataSourceKey = this.options.selectedDataSource;
      if (!dataSourceKey) return { datasets: [] };

      const dataStream = this.activityData.streams[dataSourceKey]?.data || [];
      const distanceStream = this.activityData.streams.distance?.data || [];

      const mainDataPoints = dataStream.map((value, index) => ({
        x: distanceStream[index],
        y: value,
      }));

      const datasets = [];

      if (
        this.options.showAltitudeInBackground &&
        dataSourceKey !== "altitude" &&
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
        label: this.options.yAxisTitle,
        data: mainDataPoints,
        backgroundColor: this.options.transparentFill
          ? "transparent"
          : this.hexToRgba(this.options.fillColor),
        borderColor: this.options.lineColor,
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        borderWidth: this.options.lineThickness,
        yAxisID: "y",
        order: 1,
      });

      return { datasets };
    },
    chartOptions() {
      const distanceStream = this.activityData.streams.distance?.data || [0];
      const maxDistance = distanceStream[distanceStream.length - 1] || 0;

      const rawStep = maxDistance / this.options.xAxisTicks;
      const niceSteps = [
        100, 250, 500, 1000, 2000, 2500, 5000, 10000, 25000, 50000,
      ];
      const stepSize =
        niceSteps.find((step) => step >= rawStep) ||
        niceSteps[niceSteps.length - 1];

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
              // --- DE FIX ---
              // De callback-functie krijgt nu extra parameters mee.
              callback: function (value, index, ticks) {
                // Als de huidige 'tick' de laatste in de array is, toon dan geen label.
                if (index === ticks.length - 1) {
                  return null;
                }
                // Voor alle andere ticks, toon het label zoals voorheen.
                const km = value / 1000;
                return km.toLocaleString() + " km";
              },
            },
            title: {
              display: this.options.showXAxisTitle,
              text: this.options.xAxisTitle,
            },
          },
          y: {
            display:
              this.options.showYAxisLabels || this.options.showYAxisTitle,
            grid: { display: this.options.showGrid },
            ticks: {
              display: this.options.showYAxisLabels,
              maxTicksLimit: this.options.yAxisTicks,
              font: { size: this.options.tickFontSize },
            },
            title: {
              display: this.options.showYAxisTitle,
              text: this.options.yAxisTitle,
            },
          },
          y1: {
            display: false,
            grid: { display: false },
            position: "right",
          },
        },
        plugins: {
          legend: { display: false },
          title: {
            display: this.options.showLegend,
            text: this.options.yAxisTitle,
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
