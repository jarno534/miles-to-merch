<template>
  <div class="activities-page">
    <h1>Your Strava Activities</h1>
    <div v-if="loading">
      <p>Activiteiten aan het laden...</p>
    </div>
    <div v-else>
      <ul class="activities-list" v-if="activities.length > 0">
        <li
          v-for="activity in activities"
          :key="activity.id"
          class="activity-item"
        >
          <h2 class="activity-name">{{ activity.name }}</h2>
          <p>Afstand: {{ (activity.distance / 1000).toFixed(2) }} km</p>
          <p>Type: {{ activity.type }}</p>
        </li>
      </ul>
      <p v-else>Geen activiteiten gevonden.</p>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "ActivitiesView",
  data() {
    return {
      activities: [],
      loading: true,
    };
  },
  async created() {
    try {
      const response = await axios.get("http://localhost:5000/api/activities");
      this.activities = response.data;
    } catch (error) {
      console.error("Fout bij het ophalen van activiteiten:", error);
      this.activities = [];
    } finally {
      this.loading = false;
    }
  },
};
</script>

<style scoped>
.activities-page {
  padding: 20px;
}
.activities-list {
  list-style-type: none;
  padding: 0;
}
.activity-item {
  background-color: #f4f4f4;
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 8px;
}
.activity-name {
  margin: 0 0 10px 0;
  color: #fc4c02;
}
</style>
