<template>
  <div class="dashboard">
    <!-- Welcome + IPI Score -->
    <div class="welcome-row">
      <div class="welcome-text">
        <h1 class="greeting">
          Добро пожаловать, {{ firstName }}
        </h1>
        <p class="greeting-sub">Вот обзор вашей активности</p>
      </div>
    </div>

    <!-- Stat cards -->
    <div class="stats-grid">
      <div class="stat-card ipi-card">
        <div class="stat-icon ipi">
          <el-icon :size="22"><TrendCharts /></el-icon>
        </div>
        <div class="stat-body">
          <span class="stat-label">Индекс IPI</span>
          <div class="stat-row">
            <span class="stat-value">87.5</span>
            <span class="stat-delta positive">+5.2</span>
          </div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon works">
          <el-icon :size="22"><Document /></el-icon>
        </div>
        <div class="stat-body">
          <span class="stat-label">Работы</span>
          <div class="stat-row">
            <span class="stat-value">12</span>
            <span class="stat-sub">всего</span>
          </div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon pending">
          <el-icon :size="22"><Clock /></el-icon>
        </div>
        <div class="stat-body">
          <span class="stat-label">На проверке</span>
          <div class="stat-row">
            <span class="stat-value">3</span>
            <span class="stat-sub">ожидают</span>
          </div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon tasks">
          <el-icon :size="22"><Finished /></el-icon>
        </div>
        <div class="stat-body">
          <span class="stat-label">Задачи</span>
          <div class="stat-row">
            <span class="stat-value">5</span>
            <span class="stat-sub">активных</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Chart + Notifications -->
    <div class="bottom-grid">
      <!-- Chart placeholder -->
      <div class="chart-card">
        <div class="card-header">
          <h3>Динамика IPI</h3>
          <el-radio-group v-model="period" size="small">
            <el-radio-button value="month">Месяц</el-radio-button>
            <el-radio-button value="quarter">Квартал</el-radio-button>
            <el-radio-button value="year">Год</el-radio-button>
          </el-radio-group>
        </div>
        <div class="chart-placeholder">
          <div class="chart-bars">
            <div v-for="(val, i) in chartData" :key="i" class="chart-bar-wrap">
              <div class="chart-bar" :style="{ height: val + '%' }"></div>
              <span class="chart-label">{{ chartLabels[i] }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Notifications -->
      <div class="notif-card">
        <div class="card-header">
          <h3>Уведомления</h3>
          <el-button link type="primary" size="small">Все</el-button>
        </div>
        <div class="notif-list">
          <div v-for="(n, i) in notifications" :key="i" class="notif-item">
            <div class="notif-dot" :class="n.type"></div>
            <div class="notif-body">
              <p class="notif-text">{{ n.text }}</p>
              <span class="notif-time">{{ n.time }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useAuthStore } from "@/store/auth";
import { TrendCharts, Document, Clock, Finished } from "@element-plus/icons-vue";

const auth = useAuthStore();
const firstName = computed(() => auth.user.name.split(" ")[0]);

const period = ref("month");

const chartData = [45, 62, 55, 78, 65, 82, 87];
const chartLabels = ["Сен", "Окт", "Ноя", "Дек", "Янв", "Фев", "Мар"];

const notifications = [
  { type: "success", text: 'Работа "Статья в журнале" подтверждена', time: "5 мин назад" },
  { type: "warning", text: "Вам назначена новая задача", time: "1 час назад" },
  { type: "danger", text: 'Работа "Отчёт по гранту" отклонена', time: "2 часа назад" },
  { type: "info", text: "Обновлены критерии KPI", time: "вчера" },
];
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

/* Welcome */
.greeting {
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.greeting-sub {
  font-size: 15px;
  color: var(--text-secondary);
  margin-top: 4px;
}

/* Stats grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 24px;
  display: flex;
  align-items: flex-start;
  gap: 16px;
  transition: all var(--transition);
}

.stat-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon.ipi {
  background: var(--primary-light);
  color: var(--primary);
}

.stat-icon.works {
  background: #ecfdf5;
  color: var(--success);
}

.stat-icon.pending {
  background: #fffbeb;
  color: var(--warning);
}

.stat-icon.tasks {
  background: #f5f3ff;
  color: var(--accent);
}

.stat-body {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

.stat-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.5px;
}

.stat-delta {
  font-size: 13px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 20px;
}

.stat-delta.positive {
  background: #ecfdf5;
  color: var(--success);
}

.stat-sub {
  font-size: 13px;
  color: var(--text-muted);
}

.ipi-card {
  border-left: 3px solid var(--primary);
}

/* Bottom grid */
.bottom-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 20px;
}

.chart-card,
.notif-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.card-header h3 {
  font-size: 16px;
  font-weight: 600;
}

/* Chart bars */
.chart-placeholder {
  height: 200px;
  display: flex;
  align-items: flex-end;
}

.chart-bars {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  width: 100%;
  height: 100%;
}

.chart-bar-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  justify-content: flex-end;
}

.chart-bar {
  width: 100%;
  max-width: 40px;
  background: linear-gradient(to top, var(--primary), var(--accent));
  border-radius: 6px 6px 0 0;
  transition: height 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  min-height: 4px;
}

.chart-label {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 8px;
}

/* Notifications */
.notif-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.notif-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 12px;
  border-radius: var(--radius);
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
.notif-dot.info { background: var(--primary); }

.notif-body {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

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
