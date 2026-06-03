<template>
  <div class="header-inner">
    <div class="header-left">
      <h2 class="page-heading">{{ pageTitle }}</h2>
    </div>

    <div class="header-right">
      <!-- User dropdown -->
      <el-dropdown trigger="click">
        <button class="user-btn">
          <div class="user-avatar-sm">{{ userInitials }}</div>
          <span class="user-name-sm">{{ auth.fullName }}</span>
          <el-icon :size="14"><ArrowDown /></el-icon>
        </button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="router.push('/employee/profile')">
              <el-icon><User /></el-icon>
              Профиль
            </el-dropdown-item>
            <el-dropdown-item divided @click="logout">
              <el-icon><SwitchButton /></el-icon>
              Выход
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/store/auth";
import { ArrowDown, User, SwitchButton } from "@element-plus/icons-vue";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const userInitials = computed(() => {
  const parts = (auth.fullName || 'U').split(' ');
  return parts.map((p) => p[0]).join('').slice(0, 2);
});

const pageTitles: Record<string, string> = {
  "/dashboard": "Главная",
  "/employee/works": "Мои работы",
  "/employee/tasks": "Задачи",
  "/employee/projects": "Проекты",
  "/employee/kpi": "Мой KPI",
  "/manager/verification": "Проверка работ",
  "/manager/kpi-settings": "Веса KPI",
  "/manager/employees": "Сотрудники",
  "/admin/users": "Пользователи",
  "/employee/profile": "Профиль",
};

const pageTitle = computed(() => pageTitles[route.path] || "");

const logout = () => {
  auth.logout();
  router.push("/login");
};
</script>

<style scoped>
.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.page-heading {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* User button */
.user-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 12px 6px 6px;
  border-radius: var(--radius);
  border: 1px solid var(--border);
  background: var(--bg-card);
  cursor: pointer;
  transition: all var(--transition);
}

.user-btn:hover {
  background: var(--bg);
  border-color: var(--text-muted);
}

.user-avatar-sm {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-name-sm {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}
</style>
