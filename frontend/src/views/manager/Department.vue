<template>
  <div class="department-page">
    <div class="page-top">
      <div>
        <h2 class="page-title">Мой отдел</h2>
        <p class="page-subtitle">Сотрудники, статистика, верификация</p>
      </div>
    </div>

    <el-tabs v-model="activeTab" class="dept-tabs">
      <el-tab-pane label="Сотрудники" name="overview">
        <div class="filters-bar">
          <el-radio-group v-model="period" @change="fetchStats">
            <el-radio-button value="month">Месяц</el-radio-button>
            <el-radio-button value="quarter">Квартал</el-radio-button>
            <el-radio-button value="year">Год</el-radio-button>
          </el-radio-group>

          <el-input-number
            v-model="year"
            :min="2020"
            :max="2100"
            :step="1"
            :precision="0"
            style="width: 120px"
            @change="fetchStats"
          />
          <el-select v-if="period === 'quarter'" v-model="quarter" style="width: 110px" @change="fetchStats">
            <el-option v-for="q in [1, 2, 3, 4]" :key="q" :label="`Q${q}`" :value="q" />
          </el-select>
          <el-select v-if="period === 'month'" v-model="month" style="width: 140px" @change="fetchStats">
            <el-option
              v-for="m in months"
              :key="m.value"
              :label="m.label"
              :value="m.value"
            />
          </el-select>

          <div style="flex: 1"></div>

          <el-button
            type="primary"
            :icon="Document"
            :loading="downloadingExcel"
            @click="downloadReport('excel')"
          >
            Excel
          </el-button>
          <el-button
            type="primary"
            plain
            :icon="Document"
            :loading="downloadingWord"
            @click="downloadReport('word')"
          >
            Word
          </el-button>
        </div>

        <div class="table-card" v-loading="loadingStats">
          <el-table :data="stats?.rows || []" stripe>
            <el-table-column prop="full_name" label="Сотрудник" min-width="180">
              <template #default="{ row }">
                <div class="emp-cell">
                  <div class="emp-avatar">{{ initials(row.full_name) }}</div>
                  <div>
                    <div class="emp-name">{{ row.full_name }}</div>
                    <div class="emp-pos">{{ row.position }} · {{ posLabel(row) }}</div>
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="IPI" width="160" align="center">
              <template #default="{ row }">
                <div class="ipi-cell">
                  <div class="ipi-bar">
                    <div class="ipi-bar-fill" :style="{ width: Math.min(row.total_ipi * 2, 100) + '%' }"></div>
                  </div>
                  <span class="ipi-num">{{ row.total_ipi.toFixed(1) }}</span>
                  <el-button size="small" link @click="openBreakdown(row)">
                    <el-icon><DataLine /></el-icon>
                  </el-button>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="Работы" width="160" align="center">
              <template #default="{ row }">
                <span class="cell-num">{{ row.works_verified }}</span>
                <span class="cell-muted">/ {{ row.works_total }}</span>
                <el-tag v-if="row.works_pending" size="small" type="warning" effect="plain" style="margin-left: 6px">
                  ожидает {{ row.works_pending }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="Задачи" width="170" align="center">
              <template #default="{ row }">
                <span class="cell-num">{{ row.tasks_completed }}</span>
                <span class="cell-muted">/ {{ row.tasks_total }}</span>
                <el-tag v-if="row.tasks_overdue" size="small" type="danger" effect="plain" style="margin-left: 6px">
                  просрочено {{ row.tasks_overdue }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="Проектов" width="100" align="center">
              <template #default="{ row }">
                {{ row.projects_count }}
              </template>
            </el-table-column>
            <el-table-column label="" width="60" align="center">
              <template #default="{ row }">
                <el-button size="small" circle @click="openProfile(row)">
                  <el-icon><User /></el-icon>
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <el-tab-pane label="Сравнение" name="compare">
        <div class="filters-bar">
          <el-radio-group v-model="period" @change="fetchStats">
            <el-radio-button value="month">Месяц</el-radio-button>
            <el-radio-button value="quarter">Квартал</el-radio-button>
            <el-radio-button value="year">Год</el-radio-button>
          </el-radio-group>
          <el-input-number v-model="year" :min="2020" :max="2100" style="width: 120px" @change="fetchStats" />
          <el-select v-if="period === 'quarter'" v-model="quarter" style="width: 110px" @change="fetchStats">
            <el-option v-for="q in [1, 2, 3, 4]" :key="q" :label="`Q${q}`" :value="q" />
          </el-select>
          <el-select v-if="period === 'month'" v-model="month" style="width: 140px" @change="fetchStats">
            <el-option v-for="m in months" :key="m.value" :label="m.label" :value="m.value" />
          </el-select>
        </div>

        <div class="compare-card" v-loading="loadingStats">
          <h3 class="section-subtitle">Активность сотрудников ({{ periodLabel }})</h3>
          <div v-if="!stats?.rows.length" class="empty-state">Данных нет</div>
          <div v-else class="compare-list">
            <div
              v-for="(row, idx) in stats.rows"
              :key="row.employee_id"
              class="compare-card-wrap"
            >
              <div class="compare-row" @click="toggleExpand(row.employee_id)">
                <div class="compare-rank">{{ idx + 1 }}</div>
                <div class="compare-name">
                  <div class="emp-name">{{ row.full_name }}</div>
                  <div class="emp-pos">{{ posLabel(row) }}</div>
                </div>
                <div class="compare-bar-wrap">
                  <div class="compare-bar">
                    <div
                      class="compare-bar-fill"
                      :style="{ width: barWidth(row.activity_score) + '%' }"
                    ></div>
                  </div>
                  <div class="compare-numbers">
                    <span class="num-block" title="Работы (одобрено / всего)">
                      <el-icon :size="13"><Document /></el-icon>
                      {{ row.works_verified }}/{{ row.works_total }}
                    </span>
                    <span class="num-block" title="Задачи (выполнено / всего)">
                      <el-icon :size="13"><Finished /></el-icon>
                      {{ row.tasks_completed }}/{{ row.tasks_total }}
                    </span>
                    <span v-if="row.tasks_overdue" class="num-block num-bad" title="Просрочено">
                      <el-icon :size="13"><Warning /></el-icon>
                      {{ row.tasks_overdue }}
                    </span>
                    <span class="num-block" title="Проектов">
                      <el-icon :size="13"><Folder /></el-icon>
                      {{ row.projects_count }}
                    </span>
                  </div>
                </div>
                <div class="compare-ipi">
                  <span class="ipi-num-big">{{ row.total_ipi.toFixed(1) }}</span>
                  <span class="ipi-label">IPI</span>
                </div>
                <el-icon class="compare-chevron" :class="{ rot: expandedId === row.employee_id }">
                  <ArrowDown />
                </el-icon>
              </div>

              <div v-if="expandedId === row.employee_id" class="compare-detail">
                <div v-if="loadingDetail" class="empty-state">Загрузка...</div>
                <template v-else-if="detail">
                  <!-- Works -->
                  <section class="detail-section">
                    <h4 class="detail-section-title">
                      Работы ({{ detail.works.length }})
                    </h4>
                    <div v-if="detail.works.length === 0" class="empty-row">работ нет</div>
                    <el-table v-else :data="detail.works" stripe size="small">
                      <el-table-column prop="title" label="Название" min-width="200" />
                      <el-table-column label="Категория" width="150">
                        <template #default="{ row: w }">
                          <el-tag size="small" effect="light">{{ w.category }}</el-tag>
                        </template>
                      </el-table-column>
                      <el-table-column prop="work_type" label="Тип" width="180" />
                      <el-table-column label="Баллы" width="80" align="center">
                        <template #default="{ row: w }">
                          <span class="num-points">{{ w.points }}</span>
                        </template>
                      </el-table-column>
                      <el-table-column label="Статус" width="130">
                        <template #default="{ row: w }">
                          <el-tag size="small" :type="w.verified ? 'success' : 'warning'" effect="plain">
                            {{ w.verified ? 'Подтверждено' : 'Ожидает' }}
                          </el-tag>
                        </template>
                      </el-table-column>
                      <el-table-column prop="date" label="Дата" width="110" />
                    </el-table>
                  </section>

                  <!-- Tasks -->
                  <section class="detail-section">
                    <h4 class="detail-section-title">
                      Задачи ({{ detail.tasks.length }})
                      <span class="detail-section-sub">
                        выполнено: <b>{{ detail.tasks_completed }}</b> ·
                        просрочено: <b>{{ detail.tasks_overdue }}</b>
                      </span>
                    </h4>
                    <div v-if="detail.tasks.length === 0" class="empty-row">задач нет</div>
                    <el-table v-else :data="detail.tasks" stripe size="small">
                      <el-table-column prop="title" label="Название" min-width="200" />
                      <el-table-column label="Проект" min-width="160">
                        <template #default="{ row: t }">
                          <span v-if="t.project_name">{{ t.project_name }}</span>
                          <span v-else class="cell-muted">— свободная</span>
                        </template>
                      </el-table-column>
                      <el-table-column label="Статус" width="130">
                        <template #default="{ row: t }">
                          <el-tag size="small" :type="taskStatusType(t.status)" effect="light">
                            {{ taskStatusLabel(t.status) }}
                          </el-tag>
                        </template>
                      </el-table-column>
                      <el-table-column label="Приоритет" width="120">
                        <template #default="{ row: t }">
                          <el-tag size="small" :type="taskPriorityType(t.priority)" effect="plain">
                            {{ taskPriorityLabel(t.priority) }}
                          </el-tag>
                        </template>
                      </el-table-column>
                      <el-table-column prop="deadline" label="Дедлайн" width="110" />
                    </el-table>
                  </section>

                  <!-- Projects -->
                  <section class="detail-section">
                    <h4 class="detail-section-title">
                      Проекты ({{ detail.projects.length }})
                    </h4>
                    <div v-if="detail.projects.length === 0" class="empty-row">проектов нет</div>
                    <ul v-else class="projects-list">
                      <li
                        v-for="p in detail.projects"
                        :key="p.id"
                        class="project-line clickable"
                        @click.stop="goToProject(p.id)"
                      >
                        <el-icon :size="14"><Folder /></el-icon>
                        <span class="project-name">{{ p.name }}</span>
                        <span class="cell-muted">
                          {{ p.start_date }}{{ p.end_date ? ' — ' + p.end_date : '' }}
                        </span>
                        <el-tag
                          v-if="p.completed_at"
                          size="small"
                          type="info"
                          effect="plain"
                        >
                          завершён {{ p.completed_at }}
                        </el-tag>
                        <el-icon class="link-arrow" :size="12"><Right /></el-icon>
                      </li>
                    </ul>
                  </section>
                </template>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="Верификация" name="verification">
        <Verification />
      </el-tab-pane>
    </el-tabs>

    <!-- IPI breakdown dialog -->
    <el-dialog
      v-model="showBreakdownDialog"
      :title="`Разбивка IPI — ${breakdown?.employee_name || ''}`"
      width="780px"
      destroy-on-close
    >
      <IPIBreakdownPanel v-if="breakdown" :breakdown="breakdown" />
      <div v-else style="padding: 24px; text-align: center; color: var(--text-muted)">
        Загрузка...
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  DataLine, Document, Finished, Folder, Warning, User, ArrowDown, Right,
} from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import {
  departmentApi, kpiApi,
  type DepartmentStats, type IPIBreakdown, type DepartmentStatsRow,
  type EmployeeDetail,
} from "@/api/kpi";
import { POSITION_TYPE_LABELS } from "@/types/user";
import Verification from "./Verification.vue";
import IPIBreakdownPanel from "@/components/ui/IPIBreakdownPanel.vue";

const route = useRoute();
const router = useRouter();

const activeTab = ref(typeof route.query.tab === 'string' ? route.query.tab : 'overview');

watch(activeTab, (v) => {
  router.replace({ query: { ...route.query, tab: v } });
});

const period = ref<'month' | 'quarter' | 'year'>('quarter');
const today = new Date();
const year = ref(today.getFullYear());
const month = ref(today.getMonth() + 1);
const quarter = ref(Math.floor(today.getMonth() / 3) + 1);

const months = [
  { value: 1, label: 'Январь' }, { value: 2, label: 'Февраль' }, { value: 3, label: 'Март' },
  { value: 4, label: 'Апрель' }, { value: 5, label: 'Май' }, { value: 6, label: 'Июнь' },
  { value: 7, label: 'Июль' }, { value: 8, label: 'Август' }, { value: 9, label: 'Сентябрь' },
  { value: 10, label: 'Октябрь' }, { value: 11, label: 'Ноябрь' }, { value: 12, label: 'Декабрь' },
];

const stats = ref<DepartmentStats | null>(null);
const loadingStats = ref(false);

const periodLabel = computed(() => {
  if (period.value === 'month') return `${months.find(m => m.value === month.value)?.label} ${year.value}`;
  if (period.value === 'quarter') return `${year.value} Q${quarter.value}`;
  return `${year.value} год`;
});

async function fetchStats() {
  loadingStats.value = true;
  try {
    const params: any = { period: period.value, year: year.value };
    if (period.value === 'month') params.month = month.value;
    if (period.value === 'quarter') params.quarter = quarter.value;
    const { data } = await departmentApi.getStats(params);
    stats.value = data;
  } catch {
    ElMessage.error('Не удалось загрузить статистику');
  } finally {
    loadingStats.value = false;
  }
}

// Выгрузка отчёта
const downloadingExcel = ref(false);
const downloadingWord = ref(false);

async function downloadReport(format: 'excel' | 'word') {
  const flag = format === 'excel' ? downloadingExcel : downloadingWord;
  flag.value = true;
  try {
    const params: any = { period: period.value, year: year.value, format };
    if (period.value === 'month') params.month = month.value;
    if (period.value === 'quarter') params.quarter = quarter.value;
    const resp = await departmentApi.downloadReport(params);
    const blob = resp.data as Blob;
    // имя файла из Content-Disposition
    const cd = resp.headers['content-disposition'] || '';
    let filename = `Отчёт.${format === 'excel' ? 'xlsx' : 'docx'}`;
    const m = cd.match(/filename\*=UTF-8''([^;]+)/);
    if (m) {
      try { filename = decodeURIComponent(m[1]); } catch {}
    }
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    ElMessage.success(`Отчёт ${format === 'excel' ? 'Excel' : 'Word'} скачан`);
  } catch (e: any) {
    ElMessage.error('Не удалось сформировать отчёт');
  } finally {
    flag.value = false;
  }
}

function initials(name: string) {
  if (!name) return '?';
  const parts = name.trim().split(/\s+/);
  return ((parts[0]?.[0] || '') + (parts[1]?.[0] || '')).toUpperCase();
}

function posLabel(row: DepartmentStatsRow) {
  const base = POSITION_TYPE_LABELS[row.position_type] || '—';
  if (row.position_type === 'phd_student' && row.phd_year) {
    return `${base} (${row.phd_year} курс)`;
  }
  return base;
}

const maxActivity = computed(() => {
  const rows = stats.value?.rows || [];
  if (!rows.length) return 1;
  return Math.max(1, ...rows.map(r => Math.max(0, r.activity_score)));
});
function barWidth(score: number) {
  return Math.max(4, (Math.max(0, score) / maxActivity.value) * 100);
}

// Compare expand
const expandedId = ref<number | null>(null);
const detail = ref<EmployeeDetail | null>(null);
const loadingDetail = ref(false);

async function toggleExpand(empId: number) {
  if (expandedId.value === empId) {
    expandedId.value = null;
    return;
  }
  expandedId.value = empId;
  detail.value = null;
  loadingDetail.value = true;
  try {
    const params: any = { period: period.value, year: year.value };
    if (period.value === 'month') params.month = month.value;
    if (period.value === 'quarter') params.quarter = quarter.value;
    const { data } = await departmentApi.getEmployeeDetail(empId, params);
    detail.value = data;
  } catch {
    ElMessage.error('Не удалось загрузить детали сотрудника');
  } finally {
    loadingDetail.value = false;
  }
}

function taskStatusType(s: string) {
  return ({ assigned: 'warning', in_progress: 'primary', completed: 'success', overdue: 'danger' } as any)[s] || 'info';
}
function taskStatusLabel(s: string) {
  return ({ assigned: 'Назначена', in_progress: 'В работе', completed: 'Выполнена', overdue: 'Просрочена' } as any)[s] || s;
}
function taskPriorityType(p: string) {
  return p === 'high' ? 'danger' : p === 'medium' ? 'warning' : 'info';
}
function taskPriorityLabel(p: string) {
  return ({ low: 'Низкий', medium: 'Средний', high: 'Высокий' } as any)[p] || p;
}

// IPI breakdown
const showBreakdownDialog = ref(false);
const breakdown = ref<IPIBreakdown | null>(null);

async function openBreakdown(row: DepartmentStatsRow) {
  showBreakdownDialog.value = true;
  breakdown.value = null;
  try {
    const q = period.value === 'quarter' ? quarter.value : Math.floor((month.value - 1) / 3) + 1;
    const { data } = await kpiApi.getBreakdown({
      employee_id: row.employee_id,
      year: year.value,
      quarter: q,
    });
    breakdown.value = data;
  } catch {
    ElMessage.error('Не удалось загрузить разбивку');
  }
}

function openProfile(row: DepartmentStatsRow) {
  router.push({ path: '/employee/profile', query: { employee_id: row.employee_id, from: 'department' } });
}

function goToProject(projectId: number) {
  router.push({ path: `/employee/projects/${projectId}`, query: { from: 'department' } });
}

onMounted(fetchStats);
</script>

<style scoped>
.department-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
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

.dept-tabs :deep(.el-tabs__header) {
  margin-bottom: 16px;
}

.filters-bar {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
  padding: 14px 16px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  margin-bottom: 16px;
}

.table-card,
.compare-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 16px 20px;
}

.section-subtitle {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 14px;
  color: var(--text-primary);
}

/* Employee cell */
.emp-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.emp-avatar {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: var(--primary-soft, #eef2ff);
  color: var(--primary);
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.emp-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.emp-pos {
  font-size: 11px;
  color: var(--text-muted);
}

.ipi-cell {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.ipi-bar {
  width: 60px;
  height: 6px;
  background: var(--bg);
  border-radius: 3px;
  overflow: hidden;
}

.ipi-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary), var(--accent));
  border-radius: 3px;
}

.ipi-num {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  min-width: 30px;
}

.cell-num {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.cell-muted {
  font-size: 12px;
  color: var(--text-muted);
  margin-left: 4px;
}

/* Compare list */
.compare-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.compare-card-wrap {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
}

.compare-row {
  display: grid;
  grid-template-columns: 36px 200px 1fr 90px 32px;
  gap: 16px;
  align-items: center;
  padding: 12px 14px;
  cursor: pointer;
  transition: background var(--transition);
}

.compare-row:hover { background: var(--bg-card); }

.compare-chevron {
  color: var(--text-muted);
  transition: transform 0.2s;
}

.compare-chevron.rot {
  transform: rotate(180deg);
}

.compare-detail {
  background: var(--bg-card);
  border-top: 1px solid var(--border);
  padding: 16px 18px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.detail-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-section-title {
  font-size: 13px;
  font-weight: 600;
  margin: 0;
  color: var(--text-primary);
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.detail-section-sub {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 400;
}

.empty-row {
  font-size: 12px;
  color: var(--text-muted);
  padding: 4px 0;
}

.num-points {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-soft, #eef2ff);
  color: var(--primary);
  font-weight: 600;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
}

.cell-muted {
  font-size: 12px;
  color: var(--text-muted);
}

.projects-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.project-line {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  font-size: 13px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 6px;
}

.project-name {
  font-weight: 500;
  color: var(--text-primary);
}

.project-line.clickable {
  cursor: pointer;
  transition: all var(--transition);
}

.project-line.clickable:hover {
  border-color: var(--primary);
  background: var(--primary-soft, #eef2ff);
}

.link-arrow {
  margin-left: auto;
  color: var(--text-muted);
}

.compare-rank {
  font-size: 16px;
  font-weight: 700;
  color: var(--primary);
  text-align: center;
}

.compare-name {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.compare-bar-wrap {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
}

.compare-bar {
  height: 8px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 4px;
  overflow: hidden;
}

.compare-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary), var(--accent));
}

.compare-numbers {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.num-block {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-secondary);
}

.num-bad {
  color: var(--danger);
}

.compare-ipi {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.ipi-num-big {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.5px;
}

.ipi-label {
  font-size: 10px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
  color: var(--text-muted);
}
</style>
