<template>
  <div class="start-design-page">
    <div class="choice-container">
      <h1>How do you want to create your design?</h1>
      <p>
        Use a past activity from your Strava account or upload a GPX file from
        any device.
      </p>

      <!-- This box now changes based on your login status -->
      <div class="choice-box">
        <div v-if="auth.isLoggedIn && auth.user.has_strava_linked">
          <h2>Use a Strava Activity</h2>
          <p>
            Your account is linked. Select an activity to start your design.
          </p>
          <button @click="useStrava" class="strava-button">
            Select a Strava Activity
          </button>
        </div>
        <div v-else>
          <h2>Use a Strava Activity</h2>
          <p>
            Connect your Strava account to select from your recent activities.
          </p>
          <button @click="useStrava" class="strava-button">
            Connect with Strava
          </button>
        </div>
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
import API_BASE_URL from "@/apiConfig";

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
      auth: auth,
    };
  },
  methods: {
    useStrava() {
      localStorage.setItem("selectedProductId", this.productId);
      if (auth.isLoggedIn && auth.user.has_strava_linked) {
        this.$router.push({ name: "Activities" });
      } else {
        window.location.href = `${API_BASE_URL}/auth/login/strava`;
      }
    },

    handleGpxUpload(event) {
      const file = event.target.files[0];
      if (!file) return;

      this.gpxError = null;
      const reader = new FileReader();

      reader.onload = (e) => {
        const gpxText = e.target.result;
        try {
          const gpx = new gpxParser();
          gpx.parse(gpxText);

          if (
            !gpx.tracks ||
            gpx.tracks.length === 0 ||
            gpx.tracks[0].points.length < 2
          ) {
            throw new Error(
              "GPX file must contain a track with at least two points."
            );
          }

          const activityData = this.formatGpxData(gpx, gpxText);

          console.log("Stap 1: Finaal activityData object:", activityData);

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
      reader.readAsText(file);
    },

    // In de 'methods' van StartDesignView.vue
    formatGpxData(gpx, gpxText) {
      const track = gpx.tracks[0];
      const points = track.points;

      const hrRegex = /<ns3:hr>(\d+)</g;
      const cadRegex = /<ns3:cad>(\d+)</g;
      const rawHeartrates = [...gpxText.matchAll(hrRegex)].map((match) =>
        parseInt(match[1])
      );
      const rawCadences = [...gpxText.matchAll(cadRegex)].map((match) =>
        parseInt(match[1])
      );

      const latlng = [],
        altitude = [],
        time = [],
        heartrate = [],
        cadence = [],
        distance = [0],
        velocity_smooth = [0];

      let lastValidPoint = null;
      let totalDistance = 0;
      let validPointsCount = 0;

      // --- 1. Definieer een drempel en initialiseer movingTime ---
      const MIN_SPEED_THRESHOLD = 0.5; // m/s (alles trager dan 1.8 km/u is pauze)
      let movingTime = 0;

      for (let i = 0; i < points.length; i++) {
        const p = points[i];
        if (
          typeof p.lat === "number" &&
          typeof p.lon === "number" &&
          isFinite(p.lat) &&
          isFinite(p.lon)
        ) {
          latlng.push([p.lat, p.lon]);
          altitude.push(p.ele || null);
          time.push(p.time ? new Date(p.time).getTime() / 1000 : null);

          if (rawHeartrates[validPointsCount] !== undefined)
            heartrate.push(rawHeartrates[validPointsCount]);
          if (rawCadences[validPointsCount] !== undefined)
            cadence.push(rawCadences[validPointsCount]);

          if (lastValidPoint) {
            const segmentDistance = gpx.calcDistanceBetween(lastValidPoint, p);
            totalDistance += segmentDistance;
            const timeDiff =
              (new Date(p.time) - new Date(lastValidPoint.time)) / 1000;

            if (timeDiff > 0) {
              const speed = segmentDistance / timeDiff;
              velocity_smooth.push(speed);

              // --- 2. Tel tijd alleen op als er bewogen wordt ---
              if (speed > MIN_SPEED_THRESHOLD) {
                movingTime += timeDiff;
              }
            } else {
              velocity_smooth.push(0);
            }
          } else {
            velocity_smooth.push(0);
          }

          distance.push(totalDistance);
          lastValidPoint = p;
          validPointsCount++;
        }
      }

      if (latlng.length < 2) {
        throw new Error("GPX bevat minder dan twee valide coördinatenpunten.");
      }

      const startTime = time[0];
      const endTime = time[time.length - 1];
      const elapsedTime = startTime && endTime ? endTime - startTime : 0;

      const streams = {};
      if (latlng.length > 0) streams.latlng = { data: latlng };
      if (altitude.length > 0) streams.altitude = { data: altitude };
      if (time.length > 0) streams.time = { data: time };
      if (heartrate.length > 0) streams.heartrate = { data: heartrate };
      if (cadence.length > 0) streams.cadence = { data: cadence };
      if (distance.length > 0) streams.distance = { data: distance };
      if (velocity_smooth.length > 0)
        streams.velocity_smooth = { data: velocity_smooth };

      // --- 3. Gebruik de correcte movingTime voor de gemiddelde snelheid ---
      const averageSpeed = movingTime > 0 ? totalDistance / movingTime : 0;

      const details = {
        name: track.name || "GPX Activity",
        distance: totalDistance,
        moving_time: movingTime, // Nu correct!
        elapsed_time: elapsedTime, // Ook correct
        total_elevation_gain: track.elevation?.pos || 0,
        elev_high: track.elevation?.max || 0,
        average_speed: averageSpeed, // Nu correct!
        max_speed: Math.max(...(velocity_smooth || [0])),
        average_heartrate:
          heartrate.length > 0
            ? heartrate.reduce((a, b) => a + b, 0) / heartrate.length
            : undefined,
        max_heartrate:
          heartrate.length > 0 ? Math.max(...heartrate) : undefined,
        average_cadence:
          cadence.length > 0
            ? cadence.reduce((a, b) => a + b, 0) / cadence.length
            : undefined,
        start_date: points[0]?.time?.toISOString() || new Date().toISOString(),
        start_latlng: latlng[0],
        source: "gpx",
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
