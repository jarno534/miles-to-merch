import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import ActivitiesView from "../views/ActivitiesView.vue";

const routes = [
  {
    path: "/",
    name: "home",
    component: HomeView,
  },
  {
    path: "/activities",
    name: "activities",
    component: ActivitiesView,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
