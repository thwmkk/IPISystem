<template>
  <div class="sidebar-inner">
    <!-- Logo -->
    <div class="logo">
      <div class="logo-icon">
        <el-icon :size="24"><TrendCharts /></el-icon>
      </div>
      <div class="logo-text">
        <span class="logo-title">IPI System</span>
        <span class="logo-sub">Scientific KPI</span>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="nav">
      <div class="nav-section">
        <span class="nav-label">Основное</span>
        <router-link to="/dashboard" class="nav-item" :class="{ active: isActive('/dashboard') }">
          <el-icon><Odometer /></el-icon>
          <span>Dashboard</span>
        </router-link>
        <router-link to="/employee/works" class="nav-item" :class="{ active: isActive('/employee/works') }">
          <el-icon><Document /></el-icon>
          <span>Мои работы</span>
        </router-link>
        <router-link to="/employee/tasks" class="nav-item" :class="{ active: isActive('/employee/tasks') }">
          <el-icon><Finished /></el-icon>
          <span>Задачи</span>
        </router-link>
        <router-link to="/employee/projects" class="nav-item" :class="{ active: isActive('/employee/projects') }">
          <el-icon><Folder /></el-icon>
          <span>Проекты</span>
        </router-link>
        <router-link to="/employee/kpi" class="nav-item" :class="{ active: isActive('/employee/kpi') }">
          <el-icon><DataLine /></el-icon>
          <span>Мой KPI</span>
        </router-link>
      </div>

      <!-- Manager section -->
      <div v-if="isManager" class="nav-section">
        <span class="nav-label">Управление</span>
        <router-link to="/manager/verification" class="nav-item" :class="{ active: isActive('/manager/verification') }">
          <el-icon><CircleCheck /></el-icon>
          <span>Проверка работ</span>
        </router-link>
        <router-link to="/manager/employees" class="nav-item" :class="{ active: isActive('/manager/employees') }">
          <el-icon><User /></el-icon>
          <span>Сотрудники</span>
        </router-link>
      </div>

      <!-- Admin section -->
      <div v-if="isAdmin" class="nav-section">
        <span class="nav-label">Администрирование</span>
        <router-link to="/admin/users" class="nav-item" :class="{ active: isActive('/admin/users') }">
          <el-icon><Setting /></el-icon>
          <span>Пользователи</span>
        </router-link>
      </div>
    </nav>

    <!-- User card at bottom -->
    <div class="user-card">
      <div class="user-avatar">
        {{ userInitials }}
      </div>
      <div class="user-info">
        <span class="user-name">{{ auth.user.name }}</span>
        <span class="user-role">{{ roleLabel }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import { useAuthStore } from "@/store/auth";
import {
  Odometer,
  Document,
  Finished,
  Folder,
  DataLine,
  CircleCheck,
  User,
  Setting,
  TrendCharts,
} from "@element-plus/icons-vue";

const route = useRoute();
const auth = useAuthStore();

const isActive = (path: string) => route.path === path;
const isManager = computed(() => auth.role === "manager" || auth.role === "admin");
const isAdmin = computed(() => auth.role === "admin");

const userInitials = computed(() => {
  const parts = auth.user.name.split(" ");
  return parts.map((p) => p[0]).join("").slice(0, 2);
});

const roleLabel = computed(() => {
  const labels: Record<string, string> = {
    employee: "Сотрудник",
    manager: "Менеджер",
    admin: "Администратор",
  };
  return labels[auth.role] || auth.role;
});
</script>

<style scoped>
.sidebar-inner {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 0;
}

/* Logo */
.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 24px 24px 32px;
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.logo-text {
  display: flex;
  flex-direction: column;
}

.logo-title {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.3px;
}

.logo-sub {
  font-size: 11px;
  color: var(--text-muted);
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

/* Navigation */
.nav {
  flex: 1;
  padding: 0 12px;
  overflow-y: auto;
}

.nav-section {
  margin-bottom: 24px;
}

.nav-label {
  display: block;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  padding: 0 12px;
  margin-bottom: 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 10px;
  color: var(--text-sidebar);
  font-size: 14px;
  font-weight: 450;
  text-decoration: none;
  transition: all var(--transition);
  margin-bottom: 2px;
}

.nav-item:hover {
  background: var(--bg-sidebar-hover);
  color: #fff;
}

.nav-item.active {
  background: var(--bg-sidebar-active);
  color: #fff;
  font-weight: 500;
}

.nav-item.active .el-icon {
  color: var(--primary);
}

.nav-item .el-icon {
  font-size: 18px;
  color: var(--text-muted);
  transition: color var(--transition);
}

.nav-item:hover .el-icon {
  color: #fff;
}

/* User Card */
.user-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  margin-top: auto;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 13px;
  font-weight: 500;
  color: #fff;
}

.user-role {
  font-size: 11px;
  color: var(--text-muted);
}
</style>
