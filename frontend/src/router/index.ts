import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/",
    redirect: "/dashboard",
  },
  {
    path: "/login",
    component: () => import("../views/auth/Login.vue"),
  },
  {
    path: "/dashboard",
    component: () => import("../views/dashboard/Dashboard.vue"),
  },
  {
    path: "/employee/works",
    component: () => import("../views/employee/Works.vue"),
  },
  {
    path: "/employee/tasks",
    component: () => import("../views/employee/Tasks.vue"),
  },
  {
    path: "/employee/projects",
    component: () => import("../views/employee/Projects.vue"),
  },
  {
    path: "/employee/kpi",
    component: () => import("../views/employee/KPI.vue"),
  },
  {
    path: "/manager/verification",
    component: () => import("../views/manager/Verification.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
