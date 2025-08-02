<template>
  <div class="home">
    <h1>Miles To Merch</h1>
    <a href="http://localhost:5000" class="strava-button">Login with Strava</a>
  </div>
</template>

<script>
export default {
  name: "HomeView",
};
</script>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  font-family: "Inter", sans-serif;
}
.strava-button {
  background-color: #fc4c02;
  color: white;
  padding: 10px 20px;
  border-radius: 5px;
  text-decoration: none;
  font-size: 1.2em;
  font-weight: bold;
  transition: background-color 0.3s ease;
}
.strava-button:hover {
  background-color: #e24300;
}
</style>
