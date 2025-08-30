import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";

const routes = [
  {
    path: "/",
    name: "home",
    component: HomeView,
  },
  {
    path: "/product/:productId",
    name: "ProductDetail",
    component: () => import("../views/ProductDetailView.vue"),
    props: true,
  },
  {
    path: "/start-design/:productId",
    name: "StartDesign",
    component: () => import("../views/StartDesignView.vue"),
    props: true,
  },
  {
    path: "/my-designs",
    name: "MyDesigns",
    component: () => import("../views/MyDesignsView.vue"),
  },
  {
    path: "/activities",
    name: "Activities",
    component: () => import("../views/ActivitiesView.vue"),
  },
  {
    path: "/design/:productId/:activityId",
    name: "Design",
    component: () => import("../views/DesignView.vue"),
    props: true,
  },
  {
    path: "/login",
    name: "Login",
    component: () => import("../views/LoginView.vue"),
  },
  {
    path: "/register",
    name: "Register",
    component: () => import("../views/RegisterView.vue"),
  },
  {
    path: "/profile",
    name: "Profile",
    component: () => import("../views/ProfileView.vue"),
  },
  {
    path: "/checkout/:designId",
    name: "Checkout",
    component: () => import("../views/CheckoutView.vue"),
    props: true,
  },
  {
    path: "/order-confirmation/:orderId",
    name: "OrderConfirmation",
    component: () => import("../views/OrderConfirmationView.vue"),
    props: true,
  },
  {
    path: "/my-orders",
    name: "MyOrders",
    component: () => import("../views/MyOrdersView.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
