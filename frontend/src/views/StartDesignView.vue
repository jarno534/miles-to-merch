<template>
  <div class="start-design-page">
    <div class="choice-container">
      <h1>How do you want to create your design?</h1>
      <p>
        Use a past activity from your Strava account or upload a GPX file from
        any device.
      </p>

      <div class="choice-box">
        <h2>Use a Strava Activity</h2>
        <p>
          Connect your Strava account to select from your recent activities.
        </p>
        <button @click="useStrava" class="strava-button">
          Connect with Strava
        </button>
      </div>

      <div class="choice-box">
        <h2>Upload a GPX File</h2>
        <p>
          No account needed to start designing. You can save your work later.
        </p>
        <input
          type="file"
          @change="handleGpxUpload"
          accept=".gpx"
          ref="gpxInput"
          style="display: none"
        />
        <button @click="$refs.gpxInput.click()" class="gpx-button">
          Upload GPX File
        </button>
        <div v-if="gpxError" class="error-message">{{ gpxError }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import { auth } from "../auth";
import gpxParser from "gpxparser";

export default {
  name: "StartDesignView",
  props: {
    productId: {
      type: [String, Number],
      required: true,
    },
  },
  data() {
    return {
      gpxError: null,
    };
  },
  methods: {
    useStrava() {
      localStorage.setItem("selectedProductId", this.productId);
      if (auth.isLoggedIn && auth.user.has_strava_linked) {
        this.$router.push({ name: "Activities" });
      } else {
        window.location.href = "http://localhost:5000/auth/login/strava";
      }
    },
    handleGpxUpload(event) {
      const file = event.target.files[0];
      if (!file) return;

      this.gpxError = null;
      const reader = new FileReader();

      reader.onload = (e) => {
        try {
          const gpx = new gpxParser();
          gpx.parse(e.target.result);

          if (
            !gpx.tracks ||
            gpx.tracks.length === 0 ||
            gpx.tracks[0].points.length < 2
          ) {
            throw new Error(
              "GPX file must contain a track with at least two points."
            );
          }

          const activityData = this.formatGpxData(gpx);

          const gpxSessionKey = `gpx_${Date.now()}`;
          localStorage.setItem(gpxSessionKey, JSON.stringify(activityData));

          this.$router.push({
            name: "Design",
            params: { productId: this.productId, activityId: "gpx" },
            query: { gpx_key: gpxSessionKey },
          });
        } catch (error) {
          console.error("GPX Parsing Error Details:", error);
          this.gpxError =
            "Failed to process GPX file. It might be invalid or missing track data.";
        }
      };

      reader.onerror = () => {
        this.gpxError = "Error reading the file. Please try again.";
      };

      reader.readAsText(file);
    },
    formatGpxData(gpx) {
      const track = gpx.tracks[0];
      const points = track.points;

      // Create streams, ensuring data exists
      const streams = {
        latlng: { data: points.map((p) => [p.lat, p.lon]) },
        altitude: { data: points.map((p) => p.ele || 0) }, // Default to 0 if elevation is missing
        time: { data: points.map((p) => new Date(p.time).getTime() / 1000) },
      };

      // Create details, with fallbacks for missing data
      const details = {
        name: track.name || "My GPX Activity",
        distance: track.distance ? track.distance.total : 0,
        moving_time: track.duration ? track.duration.moving : 0,
        total_elevation_gain: track.elevation ? track.elevation.pos : 0,
        start_date: points[0].time
          ? points[0].time.toISOString()
          : new Date().toISOString(),
        start_latlng: points[0] ? [points[0].lat, points[0].lon] : [0, 0],
      };

      return { details, streams, photos: [] };
    },
  },
};
</script>

<style scoped>
.start-design-page {
  display: flex;
  justify-content: center;
  padding: 50px 20px;
}
.choice-container {
  max-width: 600px;
  text-align: center;
}
.choice-box {
  background: #fff;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  margin-top: 30px;
}
h1 {
  font-size: 2rem;
}
h2 {
  margin-top: 0;
  font-size: 1.5rem;
  color: #333;
}
p {
  color: #666;
  line-height: 1.6;
}
.strava-button,
.gpx-button {
  border: none;
  padding: 12px 25px;
  border-radius: 8px;
  font-weight: bold;
  font-size: 1.1rem;
  cursor: pointer;
  width: 100%;
  margin-top: 10px;
  transition: background-color 0.2s;
}
.strava-button {
  background-color: #fc4c02;
  color: white;
}
.strava-button:hover {
  background-color: #e24300;
}
.gpx-button {
  background-color: #28a745;
  color: white;
}
.gpx-button:hover {
  background-color: #218838;
}
.error-message {
  color: #dc3545;
  margin-top: 15px;
}
</style>
