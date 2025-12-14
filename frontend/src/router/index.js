import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import { auth } from "../auth";

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
  // --- BEVEILIGDE ROUTES ---
  {
    path: "/profile",
    name: "Profile",
    component: () => import("../views/ProfileView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/my-designs",
    name: "MyDesigns",
    component: () => import("../views/MyDesignsView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/checkout/:designId",
    name: "Checkout",
    component: () => import("../views/CheckoutView.vue"),
    props: true,
    meta: { requiresAuth: true },
  },
  {
    path: "/order-confirmation/:sessionId",
    name: "OrderConfirmation",
    component: () => import("../views/OrderConfirmationView.vue"),
    props: true,
    meta: { requiresAuth: true },
  },
  {
    path: "/my-orders",
    name: "MyOrders",
    component: () => import("../views/MyOrdersView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/admin",
    name: "AdminProducts",
    component: () => import("../views/AdminProducts.vue"),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

router.beforeEach(async (to, from, next) => {
  if (!auth.isAuthCheckComplete) {
    await auth.checkAuthStatus();
  }

  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    next({ name: "Login", query: { redirect: to.fullPath } });
  } else if (to.meta.requiresAdmin && (!auth.user || !auth.user.is_admin)) {
    next({ name: "home" }); // Redirect non-admins to home
  } else {
    next();
  }
});

export default router;
