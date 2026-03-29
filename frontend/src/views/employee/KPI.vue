<template>
  <div class="kpi-page">
    <div class="page-top">
      <div>
        <h2 class="page-title">Мой KPI</h2>
        <p class="page-subtitle">Индивидуальный показатель эффективности</p>
      </div>
    </div>

    <!-- Main IPI card -->
    <div class="ipi-hero">
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
            :stroke-dashoffset="circumference - (circumference * ipi) / 100"
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
          <span class="ipi-value">{{ ipi }}</span>
          <span class="ipi-delta positive">+{{ growth }}</span>
        </div>
      </div>
      <div class="ipi-info">
        <h3>Индекс IPI</h3>
        <p class="ipi-desc">Совокупный показатель за текущий период</p>
      </div>
    </div>

    <!-- Breakdown cards -->
    <div class="breakdown-grid">
      <div class="breakdown-card scientific">
        <div class="breakdown-icon">
          <el-icon :size="20"><Document /></el-icon>
        </div>
        <div class="breakdown-body">
          <span class="breakdown-label">Научные</span>
          <span class="breakdown-value">{{ stats.scientific }}</span>
        </div>
        <div class="breakdown-bar">
          <div class="bar-fill" :style="{ width: (stats.scientific / ipi * 100) + '%' }"></div>
        </div>
      </div>

      <div class="breakdown-card organizational">
        <div class="breakdown-icon">
          <el-icon :size="20"><OfficeBuilding /></el-icon>
        </div>
        <div class="breakdown-body">
          <span class="breakdown-label">Организационные</span>
          <span class="breakdown-value">{{ stats.organizational }}</span>
        </div>
        <div class="breakdown-bar">
          <div class="bar-fill" :style="{ width: (stats.organizational / ipi * 100) + '%' }"></div>
        </div>
      </div>

      <div class="breakdown-card technical">
        <div class="breakdown-icon">
          <el-icon :size="20"><Monitor /></el-icon>
        </div>
        <div class="breakdown-body">
          <span class="breakdown-label">Технические</span>
          <span class="breakdown-value">{{ stats.technical }}</span>
        </div>
        <div class="breakdown-bar">
          <div class="bar-fill" :style="{ width: (stats.technical / ipi * 100) + '%' }"></div>
        </div>
      </div>
    </div>

    <!-- Details table -->
    <div class="table-section">
      <h3 class="section-title">Детализация баллов</h3>
      <div class="table-card">
        <el-table :data="details" stripe>
          <el-table-column prop="title" label="Работа" min-width="200" />
          <el-table-column label="Тип" width="160">
            <template #default="{ row }">
              <el-tag effect="light" size="small">{{ row.type }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="points" label="Баллы" width="100" align="center">
            <template #default="{ row }">
              <span class="points-badge">{{ row.points }}</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- Manager section -->
    <div v-if="isManager" class="manager-section">
      <h3 class="section-title">KPI отдела — {{ departmentIpi }}</h3>
      <div class="table-card">
        <el-table :data="employees" stripe>
          <el-table-column prop="name" label="Сотрудник" />
          <el-table-column label="IPI" width="160" align="center">
            <template #default="{ row }">
              <div class="emp-ipi">
                <div class="emp-bar">
                  <div class="emp-bar-fill" :style="{ width: row.ipi + '%' }"></div>
                </div>
                <span class="emp-value">{{ row.ipi }}</span>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useAuthStore } from "@/store/auth";
import { Document, OfficeBuilding, Monitor } from "@element-plus/icons-vue";

const auth = useAuthStore();
const isManager = computed(() => auth.role === "manager" || auth.role === "admin");

const ipi = ref(87.5);
const growth = ref(5.2);
const circumference = 2 * Math.PI * 52;

const stats = ref({ scientific: 50, organizational: 20, technical: 17.5 });

const details = ref([
  { title: "Статья в Nature", type: "Научная", points: 10 },
  { title: "Доклад на конференции", type: "Научная", points: 5 },
  { title: "Разработка модуля ML", type: "Техническая", points: 8 },
  { title: "Организация семинара", type: "Организационная", points: 3 },
]);

const departmentIpi = ref(72.3);
const employees = ref([
  { name: "Иванов И.И.", ipi: 90 },
  { name: "Петров П.П.", ipi: 70 },
  { name: "Сидоров С.С.", ipi: 65 },
]);
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

.ipi-delta {
  font-size: 13px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 12px;
}

.ipi-delta.positive {
  background: #ecfdf5;
  color: var(--success);
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

.points-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-soft);
  color: var(--primary);
  font-weight: 600;
  font-size: 13px;
  padding: 4px 12px;
  border-radius: 20px;
}

/* Manager section */
.manager-section {
  border-top: 1px solid var(--border);
  padding-top: 28px;
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
