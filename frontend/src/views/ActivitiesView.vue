<template>
  <div class="activities-page">
    <h1>Choose an Activity</h1>
    <div v-if="loading">
      <p>Loading activities...</p>
    </div>
    <div v-else>
      <ul class="activities-list" v-if="activities.length > 0">
        <li
          v-for="activity in activities"
          :key="activity.id"
          class="activity-item"
          @click="selectActivity(activity.id)"
        >
          <h2 class="activity-name">{{ activity.name }}</h2>
          <p class="activity-info">
            <strong>Date:</strong> {{ formatDate(activity.start_date) }}
          </p>
          <p class="activity-info">
            <strong>Distance:</strong> {{ formatDistance(activity.distance) }}
          </p>
          <p class="activity-info">
            <strong>Duration:</strong>
            {{ formatDuration(activity.moving_time) }}
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
      productId: null,
    };
  },
  async created() {
    this.productId = localStorage.getItem("selectedProductId");
    if (!this.productId) {
      console.error("No product selected. Redirecting to home.");
      this.$router.push({ name: "home" });
      return;
    }

    try {
      const response = await axios.get("http://localhost:5000/api/activities", {
        withCredentials: true,
      });
      this.activities = response.data;
    } catch (error) {
      console.error("Error fetching activities:", error);
      if (error.response && error.response.status === 401) {
        this.$router.push({ name: "home" });
      }
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
    formatDistance(meters) {
      return `${(meters / 1000).toFixed(2)} km`;
    },
    formatDuration(seconds) {
      const hours = Math.floor(seconds / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      return `${hours}h ${minutes}m`;
    },
    selectActivity(activityId) {
      // Navigate to the design page, passing BOTH IDs
      this.$router.push({
        name: "Design",
        params: {
          productId: this.productId,
          activityId: activityId,
        },
      });
      // Clean up the stored ID, we don't need it anymore
      localStorage.removeItem("selectedProductId");
    },
  },
};
</script>

<style scoped>
.activities-page {
  padding: 40px;
  max-width: 800px;
  margin: 0 auto;
}
.activities-list {
  list-style-type: none;
  padding: 0;
}
.activity-item {
  background-color: #fff;
  padding: 20px;
  margin-bottom: 15px;
  border-radius: 12px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}
.activity-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}
.activity-name {
  margin: 0 0 10px 0;
  color: #fc4c02;
  font-size: 1.5em;
}
.activity-info {
  margin: 5px 0;
}
</style>
