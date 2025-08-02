<template>
  <div class="activities-page">
    <h1>Your Strava Tokens</h1>
    <p>Access Token: {{ accessToken }}</p>
    <p>Refresh Token: {{ refreshToken }}</p>
  </div>
</template>

<script>
export default {
  name: "ActivitiesView",
  data() {
    return {
      accessToken: "",
      refreshToken: "",
    };
  },
  mounted() {
    const urlParams = new URLSearchParams(window.location.search);
    this.accessToken = urlParams.get("access_token");
    this.refreshToken = urlParams.get("refresh_token");
  },
};
</script>

<style scoped>
.activities-page {
  padding: 20px;
}
</style>
