<template>
  <div class="header-inner">
    <div class="header-left">
      <h2 class="page-heading">{{ pageTitle }}</h2>
    </div>

    <div class="header-right">
      <!-- Notifications -->
      <el-popover placement="bottom-end" :width="320" trigger="click">
        <template #reference>
          <button class="icon-btn">
            <el-badge :value="3" :max="9">
              <el-icon :size="20"><Bell /></el-icon>
            </el-badge>
          </button>
        </template>
        <div class="notif-header">
          <span class="notif-title">Уведомления</span>
          <el-button link type="primary" size="small">Прочитать все</el-button>
        </div>
        <div class="notif-list">
          <div class="notif-item">
            <div class="notif-dot success"></div>
            <div>
              <p class="notif-text">Работа "Статья в журнале" подтверждена</p>
              <span class="notif-time">5 мин назад</span>
            </div>
          </div>
          <div class="notif-item">
            <div class="notif-dot warning"></div>
            <div>
              <p class="notif-text">Вам назначена новая задача</p>
              <span class="notif-time">1 час назад</span>
            </div>
          </div>
          <div class="notif-item">
            <div class="notif-dot danger"></div>
            <div>
              <p class="notif-text">Работа "Отчёт" отклонена</p>
              <span class="notif-time">2 часа назад</span>
            </div>
          </div>
        </div>
      </el-popover>

      <!-- User dropdown -->
      <el-dropdown trigger="click">
        <button class="user-btn">
          <div class="user-avatar-sm">{{ userInitials }}</div>
          <span class="user-name-sm">{{ userName }}</span>
          <el-icon :size="14"><ArrowDown /></el-icon>
        </button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item>
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
import { Bell, ArrowDown, User, SwitchButton } from "@element-plus/icons-vue";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const userName = computed(() => auth.user?.name || "User");
const userInitials = computed(() => {
  const parts = (auth.user?.name || "U").split(" ");
  return parts.map((p) => p[0]).join("").slice(0, 2);
});

const pageTitles: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/employee/works": "Мои работы",
  "/employee/tasks": "Задачи",
  "/employee/projects": "Проекты",
  "/employee/kpi": "Мой KPI",
  "/manager/verification": "Проверка работ",
  "/manager/employees": "Сотрудники",
  "/admin/users": "Пользователи",
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

/* Icon button */
.icon-btn {
  width: 40px;
  height: 40px;
  border-radius: var(--radius);
  border: 1px solid var(--border);
  background: var(--bg-card);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  transition: all var(--transition);
}

.icon-btn:hover {
  background: var(--bg);
  color: var(--text-primary);
  border-color: var(--text-muted);
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

/* Notifications popover */
.notif-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.notif-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.notif-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.notif-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 8px;
  border-radius: var(--radius-sm);
  transition: background var(--transition);
}

.notif-item:hover {
  background: var(--bg);
}

.notif-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-top: 6px;
  flex-shrink: 0;
}

.notif-dot.success { background: var(--success); }
.notif-dot.warning { background: var(--warning); }
.notif-dot.danger { background: var(--danger); }

.notif-text {
  font-size: 13px;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.4;
}

.notif-time {
  font-size: 11px;
  color: var(--text-muted);
}
</style>
