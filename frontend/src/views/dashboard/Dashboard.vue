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
            <span class="stat-value">{{ latestIpi?.toFixed(1) ?? '—' }}</span>
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
            <span class="stat-value">{{ totalWorks }}</span>
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
            <span class="stat-value">{{ pendingCount }}</span>
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
            <span class="stat-value">{{ activeTasks }}</span>
            <span class="stat-sub">активных</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Chart + Notifications -->
    <div class="bottom-grid">
      <!-- IPI dynamics chart -->
      <div class="chart-card">
        <div class="card-header">
          <h3>Динамика IPI</h3>
          <span v-if="chartData.length" class="card-sub">
            {{ chartData.length }} {{ pluralPeriod(chartData.length) }}
          </span>
        </div>
        <div class="chart-placeholder">
          <div v-if="chartData.length" class="chart-bars">
            <div
              v-for="r in chartData"
              :key="`${r.year}-${r.quarter}`"
              class="chart-bar-wrap"
            >
              <div class="chart-bar-value">{{ r.total_ipi.toFixed(1) }}</div>
              <div
                class="chart-bar"
                :style="{ height: barHeight(r.total_ipi) + '%' }"
                :title="periodTooltip(r)"
              ></div>
              <div class="chart-label">{{ r.year }} Q{{ r.quarter }}</div>
            </div>
          </div>
          <div v-else class="chart-empty">Нет данных за прошлые периоды</div>
        </div>
      </div>

      <!-- Recent works -->
      <div class="notif-card">
        <div class="card-header">
          <h3>Последние работы</h3>
        </div>
        <div class="notif-list">
          <div v-for="w in recentWorks" :key="w.id" class="notif-item">
            <div class="notif-dot" :class="w.verified ? 'success' : 'warning'"></div>
            <div class="notif-body">
              <p class="notif-text">{{ w.title }}</p>
              <span class="notif-time">{{ w._date }}</span>
            </div>
          </div>
          <div v-if="!recentWorks.length" class="chart-empty">Нет работ</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useAuthStore } from "@/store/auth";
import { TrendCharts, Document, Clock, Finished } from "@element-plus/icons-vue";
import { worksApi } from "@/api/works";
import { tasksApi } from "@/api/tasks";
import { kpiApi } from "@/api/kpi";
import type { ScientificWork, OrganizationalWork, TechnicalWork, KPIResult, Task } from "@/types/work";

const auth = useAuthStore();
const firstName = computed(() => (auth.fullName || '').split(' ')[0]);

const scientificWorks = ref<ScientificWork[]>([]);
const orgWorks = ref<OrganizationalWork[]>([]);
const techWorks = ref<TechnicalWork[]>([]);
const tasks = ref<Task[]>([]);
const kpiHistory = ref<KPIResult[]>([]);

const totalWorks = computed(() =>
  scientificWorks.value.length + orgWorks.value.length + techWorks.value.length
);
const pendingCount = computed(() =>
  [...scientificWorks.value, ...orgWorks.value, ...techWorks.value]
    .filter((w) => !w.verified).length
);
const activeTasks = computed(() =>
  tasks.value.filter((t) => t.status === 'assigned' || t.status === 'in_progress').length
);
const myKpiHistory = computed(() =>
  kpiHistory.value.filter((r) => r.employee === auth.employeeId)
);

const chartData = computed(() => {
  const sorted = [...myKpiHistory.value].sort((a, b) => {
    if (a.year !== b.year) return a.year - b.year;
    return a.quarter - b.quarter;
  });
  return sorted.slice(-8);
});

const latestIpi = computed(() => {
  if (!chartData.value.length) return null;
  return chartData.value[chartData.value.length - 1].total_ipi;
});

const barHeight = (value: number) => {
  const max = Math.max(...chartData.value.map((r) => r.total_ipi), 1);
  return Math.max((value / max) * 85, 5);
};

const periodTooltip = (r: KPIResult) => {
  return `${r.year} Q${r.quarter}\n`
    + `Научная: ${r.scientific_score.toFixed(1)}\n`
    + `Организационная: ${r.organizational_score.toFixed(1)}\n`
    + `Техническая: ${r.technical_score.toFixed(1)}\n`
    + `Итог: ${r.total_ipi.toFixed(1)}`;
};

const pluralPeriod = (n: number) => {
  const mod10 = n % 10;
  const mod100 = n % 100;
  if (mod10 === 1 && mod100 !== 11) return 'период';
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return 'периода';
  return 'периодов';
};

const recentWorks = computed(() => {
  const all = [
    ...scientificWorks.value.map((w) => ({ id: w.id, title: w.title, verified: w.verified, _date: w.created_at?.slice(0, 10) || '' })),
    ...orgWorks.value.map((w) => ({ id: w.id, title: w.title, verified: w.verified, _date: w.event_date || '' })),
    ...techWorks.value.map((w) => ({ id: w.id, title: w.title, verified: w.verified, _date: w.work_date || '' })),
  ];
  return all.sort((a, b) => b._date.localeCompare(a._date)).slice(0, 5);
});

onMounted(async () => {
  const [sw, ow, tw, t, k] = await Promise.allSettled([
    worksApi.getScientificWorks(),
    worksApi.getOrganizationalWorks(),
    worksApi.getTechnicalWorks(),
    tasksApi.getTasks(),
    kpiApi.getResults(),
  ]);
  if (sw.status === 'fulfilled') scientificWorks.value = sw.value.data;
  if (ow.status === 'fulfilled') orgWorks.value = ow.value.data;
  if (tw.status === 'fulfilled') techWorks.value = tw.value.data;
  if (t.status === 'fulfilled') tasks.value = t.value.data;
  if (k.status === 'fulfilled') kpiHistory.value = k.value.data;
});
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

.card-sub {
  font-size: 12px;
  color: var(--text-muted);
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

.chart-bar-value {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  margin-top: 6px;
}

.chart-label {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 2px;
}

.chart-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  color: var(--text-muted);
  font-size: 14px;
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
