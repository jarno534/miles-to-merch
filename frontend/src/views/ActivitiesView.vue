<template>
  <div class="activities-page">
    <h1>Your Strava Activities</h1>
    <div v-if="loading">
      <p>Loading activities...</p>
    </div>
    <div v-else>
      <ul class="activities-list" v-if="activities.length > 0">
        <li
          v-for="activity in activities"
          :key="activity.id"
          class="activity-item"
        >
          <h2 class="activity-name">{{ activity.name }}</h2>
          <p class="activity-info">
            <strong>Date:</strong> {{ formatDate(activity.start_date) }}
          </p>
          <p class="activity-info">
            <strong>Time:</strong> {{ formatTime(activity.start_date) }}
          </p>
          <p class="activity-info">
            <strong>Type:</strong> {{ activity.type }}
          </p>
        </li>
      </ul>
      <p v-else>No activities found.</p>
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
      console.error("Error fetching activities:", error);
      this.activities = [];
    } finally {
      this.loading = false;
    }
  },
  methods: {
    formatDate(dateString) {
      const options = { year: "numeric", month: "long", day: "numeric" };
      return new Date(dateString).toLocaleDateString("en-US", options);
    },
    formatTime(dateString) {
      const options = { hour: "2-digit", minute: "2-digit" };
      return new Date(dateString).toLocaleTimeString("en-US", options);
    },
  },
};
</script>

<style scoped>
.activities-page {
  padding: 20px;
  font-family: Arial, sans-serif;
}
.activities-list {
  list-style-type: none;
  padding: 0;
}
.activity-item {
  background-color: #f9f9f9;
  padding: 20px;
  margin-bottom: 15px;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.activity-name {
  margin: 0 0 10px 0;
  color: #fc4c02;
  font-size: 1.8em;
  font-weight: bold;
}
.activity-info {
  margin: 5px 0;
  font-size: 1em;
  line-height: 1.4;
}
</style>
