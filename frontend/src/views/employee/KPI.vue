<template>
  <div class="kpi-page">
    <div class="page-top">
      <div>
        <h2 class="page-title">Мой KPI</h2>
        <p class="page-subtitle">Индивидуальный показатель эффективности</p>
      </div>
    </div>

    <!-- Main IPI card -->
    <div class="ipi-hero" v-loading="loading">
      <div class="ipi-circle">
        <svg viewBox="0 0 120 120" class="ipi-ring">
          <circle cx="60" cy="60" r="52" fill="none" stroke="#e2e8f0" stroke-width="8" />
          <circle
            cx="60" cy="60" r="52"
            fill="none"
            stroke="url(#gradient)"
            stroke-width="8"
            stroke-linecap="round"
            :stroke-dasharray="circumference"
            :stroke-dashoffset="circumference - (circumference * Math.min(latestResult?.total_ipi || 0, 100)) / 100"
            transform="rotate(-90 60 60)"
          />
          <defs>
            <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="var(--primary)" />
              <stop offset="100%" stop-color="var(--accent)" />
            </linearGradient>
          </defs>
        </svg>
        <div class="ipi-value-wrap">
          <span class="ipi-value">{{ latestResult?.total_ipi?.toFixed(1) ?? '—' }}</span>
        </div>
      </div>
      <div class="ipi-info">
        <h3>Индекс IPI</h3>
        <p class="ipi-desc">Совокупный показатель за текущий период</p>
      </div>
    </div>

    <!-- Breakdown cards (collapsible) -->
    <div v-if="latestResult" class="breakdown-section-wrap">
      <div class="breakdown-toggle" @click="showBreakdownCards = !showBreakdownCards">
        <span class="breakdown-toggle-label">Разбивка по категориям</span>
        <el-icon :class="{ rot: showBreakdownCards }"><ArrowDown /></el-icon>
      </div>
      <div v-show="showBreakdownCards" class="breakdown-grid">
        <div class="breakdown-card scientific">
          <div class="breakdown-icon">
            <el-icon :size="20"><Document /></el-icon>
          </div>
          <div class="breakdown-body">
            <span class="breakdown-label">Научные</span>
            <span class="breakdown-value">{{ latestResult.scientific_score?.toFixed(1) }}</span>
          </div>
          <div class="breakdown-bar">
            <div class="bar-fill" :style="{ width: safePercent(latestResult.scientific_score, latestResult.total_ipi) + '%' }"></div>
          </div>
        </div>

        <div class="breakdown-card organizational">
          <div class="breakdown-icon">
            <el-icon :size="20"><OfficeBuilding /></el-icon>
          </div>
          <div class="breakdown-body">
            <span class="breakdown-label">Организационные</span>
            <span class="breakdown-value">{{ latestResult.organizational_score?.toFixed(1) }}</span>
          </div>
          <div class="breakdown-bar">
            <div class="bar-fill" :style="{ width: safePercent(latestResult.organizational_score, latestResult.total_ipi) + '%' }"></div>
          </div>
        </div>

        <div class="breakdown-card technical">
          <div class="breakdown-icon">
            <el-icon :size="20"><Monitor /></el-icon>
          </div>
          <div class="breakdown-body">
            <span class="breakdown-label">Технические</span>
            <span class="breakdown-value">{{ latestResult.technical_score?.toFixed(1) }}</span>
          </div>
          <div class="breakdown-bar">
            <div class="bar-fill" :style="{ width: safePercent(latestResult.technical_score, latestResult.total_ipi) + '%' }"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- IPI breakdown formula -->
    <div v-if="breakdown" class="breakdown-section">
      <div class="breakdown-head">
        <h3 class="section-title" style="margin-bottom: 0">Как считается ваш IPI</h3>
        <div class="breakdown-period">
          <el-select v-model="brYear" size="small" style="width: 100px" @change="fetchBreakdown">
            <el-option v-for="y in availableYears" :key="y" :label="y" :value="y" />
          </el-select>
          <el-select v-model="brQuarter" size="small" style="width: 90px" @change="fetchBreakdown">
            <el-option v-for="q in [1, 2, 3, 4]" :key="q" :label="`Q${q}`" :value="q" />
          </el-select>
        </div>
      </div>
      <IPIBreakdownPanel :breakdown="breakdown" @work-click="goToWork" />
    </div>

    <!-- IPI history chart -->
    <div v-if="historyResults.length > 1" class="chart-section">
      <h3 class="section-title">Динамика IPI</h3>
      <div class="chart-card">
        <svg :viewBox="`0 0 ${chartW} ${chartH}`" class="ipi-chart" preserveAspectRatio="xMidYMid meet">
          <!-- Y-axis grid lines -->
          <g class="grid">
            <line v-for="(gy, i) in gridY" :key="i" :x1="padL" :x2="chartW - padR" :y1="gy.y" :y2="gy.y" />
            <text v-for="(gy, i) in gridY" :key="'t' + i" :x="padL - 8" :y="gy.y + 4" text-anchor="end" class="grid-label">
              {{ gy.label }}
            </text>
          </g>
          <!-- X-axis labels -->
          <g class="x-labels">
            <text
              v-for="(pt, i) in chartPoints"
              :key="'x' + i"
              :x="pt.x"
              :y="chartH - padB + 18"
              text-anchor="middle"
              class="grid-label"
            >
              {{ pt.label }}
            </text>
          </g>
          <!-- Line path -->
          <polyline
            :points="chartPoints.map(p => `${p.x},${p.y}`).join(' ')"
            fill="none"
            stroke="var(--primary)"
            stroke-width="2.5"
            stroke-linejoin="round"
          />
          <!-- Points -->
          <g>
            <circle
              v-for="(pt, i) in chartPoints"
              :key="'pt' + i"
              :cx="pt.x"
              :cy="pt.y"
              r="5"
              fill="var(--primary)"
              stroke="#fff"
              stroke-width="2"
            />
          </g>
        </svg>
      </div>
    </div>

    <!-- History table -->
    <div v-if="historyResults.length" class="table-section">
      <h3 class="section-title">История по кварталам</h3>
      <div class="table-card">
        <el-table :data="historyResults" stripe>
          <el-table-column label="Период" width="160">
            <template #default="{ row }">
              {{ row.year }} Q{{ row.quarter }}
            </template>
          </el-table-column>
          <el-table-column prop="scientific_score" label="Научные" align="center">
            <template #default="{ row }">{{ row.scientific_score?.toFixed(1) }}</template>
          </el-table-column>
          <el-table-column prop="organizational_score" label="Орг." align="center">
            <template #default="{ row }">{{ row.organizational_score?.toFixed(1) }}</template>
          </el-table-column>
          <el-table-column prop="technical_score" label="Тех." align="center">
            <template #default="{ row }">{{ row.technical_score?.toFixed(1) }}</template>
          </el-table-column>
          <el-table-column label="IPI" align="center">
            <template #default="{ row }">
              <strong>{{ row.total_ipi?.toFixed(1) }}</strong>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- Details table — verified works -->
    <div class="table-section">
      <h3 class="section-title">Подтвержденные работы</h3>
      <div class="table-card">
        <el-table :data="verifiedWorks" stripe v-loading="loading">
          <el-table-column prop="title" label="Название" min-width="220" />
          <el-table-column label="Категория" width="160">
            <template #default="{ row }">
              <el-tag effect="light" size="small">{{ getTypeLabel(row._type) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="work_type" label="Тип работы" width="200">
            <template #default="{ row }">
              <span class="key-text">{{ row.work_type || '—' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Баллы" width="100" align="center">
            <template #default="{ row }">
              <span class="points-badge">{{ row.points }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="_date" label="Дата" width="120" />
        </el-table>
      </div>
    </div>

    <!-- Manager section -->
    <div v-if="auth.isManager" class="manager-section">
      <div class="manager-header">
        <h3 class="section-title" style="margin-bottom: 0">KPI отдела</h3>
        <el-button size="small" :loading="recalculating" @click="handleRecalculate">
          <el-icon><Refresh /></el-icon>
          Пересчитать за текущий квартал
        </el-button>
      </div>
      <div class="table-card">
        <el-table :data="allResults" stripe v-loading="loadingAll">
          <el-table-column prop="employee_name" label="Сотрудник" />
          <el-table-column label="IPI" width="160" align="center">
            <template #default="{ row }">
              <div class="emp-ipi">
                <div class="emp-bar">
                  <div class="emp-bar-fill" :style="{ width: Math.min(row.total_ipi, 100) + '%' }"></div>
                </div>
                <span class="emp-value">{{ row.total_ipi?.toFixed(1) }}</span>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/store/auth";
import { Document, OfficeBuilding, Monitor, Refresh, ArrowDown } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { kpiApi, type IPIBreakdown } from "@/api/kpi";
import { worksApi } from "@/api/works";
import type { KPIResult, ScientificWork, OrganizationalWork, TechnicalWork } from "@/types/work";
import IPIBreakdownPanel from "@/components/ui/IPIBreakdownPanel.vue";

const auth = useAuthStore();
const loading = ref(false);
const loadingAll = ref(false);
const recalculating = ref(false);

const circumference = 2 * Math.PI * 52;

const results = ref<KPIResult[]>([]);
const allResults = ref<KPIResult[]>([]);
const scientificWorks = ref<ScientificWork[]>([]);
const orgWorks = ref<OrganizationalWork[]>([]);
const techWorks = ref<TechnicalWork[]>([]);

const myResults = computed(() =>
  results.value.filter((r) => r.employee === auth.employeeId)
);

const latestResult = computed(() => {
  if (!myResults.value.length) return null;
  return myResults.value.reduce((a, b) =>
    (a.year > b.year || (a.year === b.year && a.quarter > b.quarter)) ? a : b
  );
});

const historyResults = computed(() =>
  [...myResults.value].sort((a, b) =>
    a.year !== b.year ? b.year - a.year : b.quarter - a.quarter
  )
);

// Chart layout
const chartW = 720;
const chartH = 240;
const padL = 40;
const padR = 16;
const padT = 16;
const padB = 36;

const chartSeries = computed(() =>
  [...myResults.value].sort((a, b) =>
    a.year !== b.year ? a.year - b.year : a.quarter - b.quarter
  )
);

const chartPoints = computed(() => {
  const s = chartSeries.value;
  if (!s.length) return [];
  const maxY = Math.max(...s.map((r) => r.total_ipi), 1);
  const innerW = chartW - padL - padR;
  const innerH = chartH - padT - padB;
  const step = s.length > 1 ? innerW / (s.length - 1) : 0;
  return s.map((r, i) => ({
    x: padL + step * i,
    y: padT + innerH - (r.total_ipi / maxY) * innerH,
    label: `${r.year} Q${r.quarter}`,
    value: r.total_ipi,
  }));
});

const gridY = computed(() => {
  const s = chartSeries.value;
  if (!s.length) return [];
  const maxY = Math.max(...s.map((r) => r.total_ipi), 1);
  const innerH = chartH - padT - padB;
  const ticks = 4;
  return Array.from({ length: ticks + 1 }, (_, i) => {
    const v = (maxY * (ticks - i)) / ticks;
    return {
      y: padT + (innerH * i) / ticks,
      label: v.toFixed(v >= 10 ? 0 : 1),
    };
  });
});

interface WorkRow {
  id: number
  title: string
  work_type: string
  points: number
  _date: string
  _type: string
}

const verifiedWorks = computed<WorkRow[]>(() => [
  ...scientificWorks.value.filter((w) => w.verified).map((w) => ({
    id: w.id, title: w.title, work_type: w.work_type, points: w.points,
    _date: w.created_at?.slice(0, 10) || '', _type: 'scientific',
  })),
  ...orgWorks.value.filter((w) => w.verified).map((w) => ({
    id: w.id, title: w.title, work_type: w.work_type, points: w.points,
    _date: w.event_date || '', _type: 'organizational',
  })),
  ...techWorks.value.filter((w) => w.verified).map((w) => ({
    id: w.id, title: w.title, work_type: w.work_type, points: w.points,
    _date: w.work_date || '', _type: 'technical',
  })),
]);

const showBreakdownCards = ref(true);

const safePercent = (part: number, total: number) =>
  total > 0 ? Math.min((part / total) * 100, 100) : 0;

const getTypeLabel = (type: string) =>
  ({ scientific: 'Научная', organizational: 'Организационная', technical: 'Техническая' }[type]);

async function fetchAll() {
  loading.value = true;
  try {
    const [r, sw, ow, tw] = await Promise.all([
      kpiApi.getResults(),
      worksApi.getScientificWorks(),
      worksApi.getOrganizationalWorks(),
      worksApi.getTechnicalWorks(),
    ]);
    results.value = r.data;
    scientificWorks.value = sw.data;
    orgWorks.value = ow.data;
    techWorks.value = tw.data;
  } catch (_) {}
  loading.value = false;

  if (auth.isManager) {
    loadingAll.value = true;
    try {
      const { data } = await kpiApi.getResults();
      const latest = new Map<number, KPIResult>();
      for (const r of data) {
        const prev = latest.get(r.employee);
        if (!prev || r.year > prev.year || (r.year === prev.year && r.quarter > prev.quarter)) {
          latest.set(r.employee, r);
        }
      }
      allResults.value = Array.from(latest.values());
    } catch (_) {}
    loadingAll.value = false;
  }
}

const router = useRouter();

function goToWork(w: { id: number; kind: string }) {
  router.push({
    path: '/employee/works',
    query: { work_id: w.id, work_kind: w.kind },
  });
}

// IPI breakdown
const breakdown = ref<IPIBreakdown | null>(null);
const today = new Date();
const brYear = ref(today.getFullYear());
const brQuarter = ref(Math.floor(today.getMonth() / 3) + 1);

const availableYears = computed(() => {
  const cur = today.getFullYear();
  return [cur - 1, cur, cur + 1];
});

async function fetchBreakdown() {
  if (!auth.employeeId) return;
  try {
    const { data } = await kpiApi.getBreakdown({
      employee_id: auth.employeeId,
      year: brYear.value,
      quarter: brQuarter.value,
    });
    breakdown.value = data;
  } catch (_) {}
}

async function handleRecalculate() {
  recalculating.value = true;
  try {
    await kpiApi.recalculateAll();
    ElMessage.success("IPI пересчитан");
    await fetchAll();
  } catch {
    ElMessage.error("Ошибка пересчёта");
  } finally {
    recalculating.value = false;
  }
}

onMounted(() => {
  fetchAll();
  fetchBreakdown();
});
</script>

<style scoped>
.kpi-page {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.page-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.page-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  margin-top: 4px;
}

/* IPI Hero */
.ipi-hero {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: 40px;
  display: flex;
  align-items: center;
  gap: 40px;
}

.ipi-circle {
  position: relative;
  width: 140px;
  height: 140px;
  flex-shrink: 0;
}

.ipi-ring {
  width: 100%;
  height: 100%;
}

.ipi-value-wrap {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.ipi-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -1px;
}

.ipi-info h3 {
  font-size: 22px;
  font-weight: 600;
}

.ipi-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin-top: 4px;
}

/* Breakdown */
.breakdown-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.breakdown-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.breakdown-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.scientific .breakdown-icon { background: var(--primary-light); color: var(--primary); }
.organizational .breakdown-icon { background: var(--success-light); color: var(--success); }
.technical .breakdown-icon { background: var(--warning-light); color: var(--warning); }

.breakdown-body {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.breakdown-label {
  font-size: 14px;
  color: var(--text-secondary);
}

.breakdown-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.breakdown-bar {
  height: 4px;
  background: var(--bg);
  border-radius: 2px;
  overflow: hidden;
}

.scientific .bar-fill { background: var(--primary); }
.organizational .bar-fill { background: var(--success); }
.technical .bar-fill { background: var(--warning); }

.bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.5s ease;
}

/* Breakdown section wrap (collapsible) */
.breakdown-section-wrap {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.breakdown-toggle {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  cursor: pointer;
  user-select: none;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  transition: background var(--transition);
}

.breakdown-toggle:hover { background: var(--bg); }

.breakdown-toggle-label { display: inline-flex; gap: 8px; align-items: center; }

.breakdown-toggle .el-icon {
  transition: transform var(--transition);
}

.breakdown-toggle .rot {
  transform: rotate(180deg);
}

.points-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-soft, #eef2ff);
  color: var(--primary);
  font-weight: 600;
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 12px;
}

.key-text {
  font-size: 12px;
  color: var(--text-muted);
  font-family: monospace;
}

/* Breakdown */
.breakdown-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.breakdown-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.breakdown-period {
  display: flex;
  gap: 8px;
}

/* Chart */
.chart-section {
  display: flex;
  flex-direction: column;
}

.chart-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 24px;
}

.ipi-chart {
  width: 100%;
  height: 280px;
  display: block;
}

.ipi-chart .grid line {
  stroke: var(--border);
  stroke-dasharray: 3 3;
}

.ipi-chart .grid-label {
  font-size: 11px;
  fill: var(--text-muted);
  font-family: inherit;
}

/* Table section */
.section-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
}

.table-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

/* Manager section */
.manager-section {
  border-top: 1px solid var(--border);
  padding-top: 28px;
}

.manager-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.emp-ipi {
  display: flex;
  align-items: center;
  gap: 12px;
}

.emp-bar {
  flex: 1;
  height: 6px;
  background: var(--bg);
  border-radius: 3px;
  overflow: hidden;
}

.emp-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary), var(--accent));
  border-radius: 3px;
}

.emp-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  min-width: 30px;
}
</style>
