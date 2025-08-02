<template>
  <div class="home">
    <h1>Log in met Strava</h1>
    <a href="http://localhost:5000" class="strava-button">Login with Strava</a>
  </div>
</template>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
}

.strava-button {
  background-color: #fc4c02;
  color: white;
  padding: 10px 20px;
  border-radius: 5px;
  text-decoration: none;
  font-size: 1.2em;
}
</style>

<script>
export default {
  name: "HomeView",
};
</script>
