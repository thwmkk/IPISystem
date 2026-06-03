import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const routes = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/login',
    component: () => import('../views/auth/Login.vue'),
    meta: { guest: true },
  },
  {
    path: '/dashboard',
    component: () => import('../views/dashboard/Dashboard.vue'),
  },
  {
    path: '/employee/works',
    component: () => import('../views/employee/Works.vue'),
  },
  {
    path: '/employee/tasks',
    component: () => import('../views/employee/Tasks.vue'),
  },
  {
    path: '/employee/projects',
    component: () => import('../views/employee/Projects.vue'),
  },
  {
    path: '/employee/projects/:id',
    component: () => import('../views/employee/ProjectDetail.vue'),
  },
  {
    path: '/employee/kpi',
    component: () => import('../views/employee/KPI.vue'),
  },
  {
    path: '/employee/profile',
    component: () => import('../views/employee/Profile.vue'),
  },
  {
    path: '/manager/department',
    component: () => import('../views/manager/Department.vue'),
    meta: { requiresManager: true },
  },
  {
    path: '/manager/verification',
    redirect: '/manager/department?tab=verification',
  },
  {
    path: '/manager/kpi-settings',
    component: () => import('../views/manager/KPISettings.vue'),
    meta: { requiresManager: true },
  },
  {
    path: '/manager/employees',
    component: () => import('../views/manager/Employees.vue'),
    meta: { requiresManager: true },
  },
  {
    path: '/admin/references',
    component: () => import('../views/admin/References.vue'),
    meta: { requiresAdmin: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('access_token')
  const isLoggedIn = !!token

  // Guest-only pages (login) — redirect to dashboard if already authenticated
  if (to.meta.guest && isLoggedIn) {
    return next('/dashboard')
  }

  // Protected pages — redirect to login if not authenticated
  if (!to.meta.guest && !isLoggedIn) {
    return next('/login')
  }

  // Role-gated pages
  if (isLoggedIn && (to.meta.requiresManager || to.meta.requiresAdmin)) {
    const auth = useAuthStore()
    if (to.meta.requiresAdmin && !auth.isAdmin) {
      return next('/dashboard')
    }
    if (to.meta.requiresManager && !auth.isManager) {
      return next('/dashboard')
    }
  }

  next()
})

export default router
