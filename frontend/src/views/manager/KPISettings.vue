<template>
  <div class="kpi-settings-page">
    <div class="page-top">
      <div>
        <h2 class="page-title">Настройка KPI</h2>
        <p class="page-subtitle">Веса групп Wi по должности · базовые веса показателей W<sub>base</sub></p>
      </div>
      <div class="page-top-actions">
        <el-select
          v-if="auth.isAdmin"
          v-model="departmentFilter"
          placeholder="Выберите подразделение"
          style="width: 280px"
          @change="onDepartmentChange"
        >
          <el-option
            v-for="d in departments"
            :key="d.id"
            :label="d.department_short_name + ' — ' + d.department_name"
            :value="d.id"
          />
        </el-select>
        <el-button type="primary" @click="recalculate" :loading="recalculating">
          Пересчитать IPI для всех
        </el-button>
      </div>
    </div>

    <!-- Formula reminder -->
    <div class="formula-card">
      <span class="formula">IPI = Σ( W<sub>i</sub> × Σ( W<sub>ij</sub> × B<sub>ij</sub> ) )</span>
      <span class="formula-desc">
        W<sub>ij</sub> = W<sub>base</sub> × k<sub>возраст</sub> × k<sub>стаж</sub> × k<sub>аспирант</sub>
        — поправочные коэффициенты считаются автоматически по профилю сотрудника.
      </span>
    </div>

    <el-tabs v-model="activeTab" class="kpi-tabs">
      <!-- Wi per position -->
      <el-tab-pane label="Веса групп (Wi) по должности" name="weights">
        <div class="weights-section">
          <div class="filters-bar">
            <span class="filter-label">Должность:</span>
            <el-select v-model="positionFilter" style="width: 240px" @change="onPositionChange">
              <el-option
                v-for="(label, key) in POSITION_TYPE_LABELS"
                :key="key"
                :label="label"
                :value="key"
              />
            </el-select>
            <template v-if="positionFilter === 'phd_student'">
              <span class="filter-label">Курс аспирантуры:</span>
              <el-select v-model="phdYearFilter" style="width: 140px" @change="loadGroupWeights">
                <el-option :label="'Все курсы'" :value="null as any" />
                <el-option :label="'1 курс'" :value="1" />
                <el-option :label="'2 курс'" :value="2" />
                <el-option :label="'3 курс'" :value="3" />
                <el-option :label="'4 курс'" :value="4" />
              </el-select>
            </template>
          </div>

          <div class="weights-grid" v-loading="loadingWeights">
            <div v-for="g in sortedGroups" :key="g.id" class="weight-card">
              <div class="weight-card-head">
                <div class="weight-dot" :class="groupClass(g.name)"></div>
                <h3 class="weight-name">{{ g.name }}</h3>
              </div>
              <div class="weight-input-row">
                <span class="weight-label">W<sub>i</sub> =</span>
                <el-input-number
                  v-model="weightsByGroup[g.id]"
                  :min="0"
                  :max="2"
                  :step="0.05"
                  :precision="2"
                  size="default"
                  @change="saveWi(g.id)"
                />
                <el-tag
                  v-if="savedFlags[g.id]"
                  size="small"
                  type="success"
                  effect="plain"
                  style="margin-left: 8px"
                >
                  сохранено
                </el-tag>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- Indicators (W_base) -->
      <el-tab-pane label="Показатели (W_base)" name="indicators">
        <div v-loading="loadingGroups" class="groups-list">
          <div v-for="group in sortedGroups" :key="group.id" class="group-card">
            <div class="group-header">
              <div class="group-header-left">
                <div class="group-dot" :class="groupClass(group.name)"></div>
                <h3 class="group-name">{{ group.name }}</h3>
              </div>
            </div>

            <el-table :data="group.indicators" stripe size="small" class="indicators-table">
              <el-table-column prop="name" label="Показатель" min-width="240" />
              <el-table-column prop="work_type_key" label="Ключ" width="220">
                <template #default="{ row }">
                  <span class="key-text">{{ row.work_type_key }}</span>
                </template>
              </el-table-column>
              <el-table-column label="W_base" width="160" align="center">
                <template #default="{ row }">
                  <el-input-number
                    v-model="row.weight"
                    :min="0"
                    :max="20"
                    :step="0.5"
                    :precision="2"
                    size="small"
                    @change="saveIndicatorWeight(row)"
                  />
                </template>
              </el-table-column>
              <el-table-column label="" width="60" align="center">
                <template #default="{ row }">
                  <el-button size="small" circle type="danger" @click="deleteIndicator(group, row)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </template>
              </el-table-column>
            </el-table>

            <div class="add-indicator">
              <el-button size="small" @click="openAddIndicator(group)">
                <el-icon><Plus /></el-icon>
                Добавить показатель
              </el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- Coefficients reference -->
      <el-tab-pane label="Поправочные коэффициенты" name="ref">
        <div class="ref-card">
          <h3 class="section-subtitle">Как считаются k<sub>возраст</sub>, k<sub>стаж</sub>, k<sub>аспирант</sub></h3>
          <p class="ref-desc">
            Эти коэффициенты применяются автоматически и не настраиваются — это часть формулы.
          </p>
          <div class="ref-grid">
            <div class="ref-block">
              <h4>k<sub>возраст</sub></h4>
              <ul>
                <li>≤ 30 лет → <b>×1.2</b></li>
                <li>31–45 лет → <b>×1.0</b></li>
                <li>&gt; 45 лет → <b>×0.9</b></li>
              </ul>
            </div>
            <div class="ref-block">
              <h4>k<sub>стаж</sub></h4>
              <ul>
                <li>≤ 5 лет → <b>×1.2</b></li>
                <li>6–15 лет → <b>×1.0</b></li>
                <li>&gt; 15 лет → <b>×0.9</b></li>
              </ul>
            </div>
            <div class="ref-block">
              <h4>k<sub>аспирант</sub></h4>
              <ul>
                <li>не аспирант → <b>×1.0</b></li>
                <li>1 курс → <b>×1.1</b></li>
                <li>2–3 курс → <b>×1.2</b></li>
                <li>4 курс → <b>×1.3</b></li>
              </ul>
            </div>
          </div>
          <div class="ref-formula">
            W<sub>ij</sub> = W<sub>base</sub> × k<sub>возраст</sub> × k<sub>стаж</sub> × k<sub>аспирант</sub>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- Add indicator dialog -->
    <el-dialog v-model="showAddDialog" title="Добавить показатель" width="450px">
      <el-form :model="newIndicator" label-position="top">
        <el-form-item label="Название показателя">
          <el-input v-model="newIndicator.name" />
        </el-form-item>
        <el-form-item label="Ключ (work_type)">
          <el-input v-model="newIndicator.work_type_key" placeholder="Должен совпадать с типом работы" />
        </el-form-item>
        <el-form-item label="W_base">
          <el-input-number v-model="newIndicator.weight" :min="0" :max="20" :step="0.5" :precision="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">Отмена</el-button>
        <el-button type="primary" @click="addIndicator" :loading="saving">Добавить</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { Delete, Plus } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { kpiApi, type KPIGroupData, type KPIIndicatorData } from "@/api/kpi";
import { POSITION_TYPE_LABELS, type PositionType, type Department } from "@/types/user";
import { useAuthStore } from "@/store/auth";
import api from "@/api/axios";

const auth = useAuthStore();
const activeTab = ref<'weights' | 'indicators' | 'ref'>('weights');

const groups = ref<KPIGroupData[]>([]);
const departments = ref<Department[]>([]);
const departmentFilter = ref<number | null>(null);
const loadingGroups = ref(false);
const loadingWeights = ref(false);
const saving = ref(false);
const recalculating = ref(false);
const showAddDialog = ref(false);
let activeGroupId = 0;
const newIndicator = ref({ name: "", work_type_key: "", weight: 1.0 });

const positionFilter = ref<PositionType>('researcher');
const phdYearFilter = ref<number | null>(null);

// Map: group_id → current Wi for selected (position, phd_year)
const weightsByGroup = ref<Record<number, number>>({});
const savedFlags = ref<Record<number, boolean>>({});

const GROUP_ORDER = ['науч', 'техн', 'организ'];
const sortedGroups = computed(() => {
  const rank = (name: string) => {
    const lower = name.toLowerCase();
    for (let i = 0; i < GROUP_ORDER.length; i++) {
      if (lower.includes(GROUP_ORDER[i])) return i;
    }
    return 99;
  };
  return [...groups.value].sort((a, b) => rank(a.name) - rank(b.name));
});

const groupClass = (name: string) => {
  if (name.toLowerCase().includes('науч')) return 'scientific';
  if (name.toLowerCase().includes('организ')) return 'organizational';
  return 'technical';
};

async function fetchDepartments() {
  if (!auth.isAdmin) return;
  try {
    const { data } = await api.get<Department[]>('/departments/');
    departments.value = data;
    if (!departmentFilter.value && data.length) {
      departmentFilter.value = data[0].id;
    }
  } catch (_) {}
}

async function fetchGroups() {
  loadingGroups.value = true;
  try {
    const params = auth.isAdmin && departmentFilter.value
      ? { department: departmentFilter.value }
      : undefined;
    const { data } = await kpiApi.getGroups(params);
    groups.value = data;
    await loadGroupWeights();
  } catch {
    ElMessage.error('Не удалось загрузить группы');
  } finally {
    loadingGroups.value = false;
  }
}

function onDepartmentChange() {
  fetchGroups();
}

function onPositionChange() {
  if (positionFilter.value !== 'phd_student') phdYearFilter.value = null;
  loadGroupWeights();
}

async function loadGroupWeights() {
  loadingWeights.value = true;
  weightsByGroup.value = {};
  try {
    const params: any = { position_type: positionFilter.value };
    if (positionFilter.value === 'phd_student') {
      params.phd_year = phdYearFilter.value;
    }
    if (auth.isAdmin && departmentFilter.value) {
      params.department = departmentFilter.value;
    }
    const { data } = await kpiApi.getGroupWeights(params);
    const map: Record<number, number> = {};
    for (const w of data) map[w.kpi_group] = w.weight;
    for (const g of groups.value) {
      weightsByGroup.value[g.id] = map[g.id] ?? g.group_weight ?? 1.0;
    }
  } catch (_) {
  } finally {
    loadingWeights.value = false;
  }
}

async function saveWi(groupId: number) {
  try {
    await kpiApi.upsertGroupWeight({
      kpi_group: groupId,
      position_type: positionFilter.value,
      phd_year: positionFilter.value === 'phd_student' ? phdYearFilter.value : null,
      weight: weightsByGroup.value[groupId],
    });
    savedFlags.value[groupId] = true;
    setTimeout(() => { savedFlags.value[groupId] = false; }, 1500);
  } catch {
    ElMessage.error('Не удалось сохранить вес');
  }
}

async function saveIndicatorWeight(indicator: KPIIndicatorData) {
  try {
    await kpiApi.updateIndicator(indicator.id, { weight: indicator.weight });
  } catch {
    ElMessage.error('Ошибка сохранения');
  }
}

function openAddIndicator(group: KPIGroupData) {
  activeGroupId = group.id;
  newIndicator.value = { name: '', work_type_key: '', weight: 1.0 };
  showAddDialog.value = true;
}

async function addIndicator() {
  if (!newIndicator.value.name || !newIndicator.value.work_type_key) {
    ElMessage.warning('Заполните название и ключ');
    return;
  }
  saving.value = true;
  try {
    await kpiApi.createIndicator({
      kpi_group: activeGroupId,
      ...newIndicator.value,
    } as any);
    showAddDialog.value = false;
    ElMessage.success('Показатель добавлен');
    fetchGroups();
  } catch {
    ElMessage.error('Ошибка');
  } finally {
    saving.value = false;
  }
}

async function deleteIndicator(group: KPIGroupData, indicator: KPIIndicatorData) {
  try {
    await ElMessageBox.confirm(`Удалить "${indicator.name}"?`, 'Подтверждение', { type: 'warning' });
  } catch { return; }
  try {
    await kpiApi.deleteIndicator(indicator.id);
    group.indicators = group.indicators.filter(i => i.id !== indicator.id);
    ElMessage.success('Удалено');
  } catch {
    ElMessage.error('Ошибка');
  }
}

async function recalculate() {
  recalculating.value = true;
  try {
    const { data } = await kpiApi.recalculateAll();
    ElMessage.success(`IPI пересчитан для ${data.length} сотрудников`);
  } catch {
    ElMessage.error('Ошибка пересчёта');
  } finally {
    recalculating.value = false;
  }
}

onMounted(async () => {
  await fetchDepartments();
  await fetchGroups();
});
</script>

<style scoped>
.kpi-settings-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.page-top-actions {
  display: flex;
  gap: 12px;
  align-items: center;
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

.formula-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
}

.formula {
  font-size: 17px;
  font-weight: 600;
  color: var(--primary);
}

.formula-desc {
  font-size: 13px;
  color: var(--text-secondary);
}

.kpi-tabs :deep(.el-tabs__header) {
  margin-bottom: 16px;
}

.filters-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.filter-label {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

.weights-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 14px;
}

.weight-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 18px 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.weight-card-head {
  display: flex;
  align-items: center;
  gap: 10px;
}

.weight-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.weight-dot.scientific, .group-dot.scientific { background: var(--primary); }
.weight-dot.organizational, .group-dot.organizational { background: var(--success); }
.weight-dot.technical, .group-dot.technical { background: var(--warning); }

.weight-name {
  font-size: 15px;
  font-weight: 600;
  margin: 0;
}

.weight-input-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.weight-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
}

.weight-hint {
  font-size: 12px;
  color: var(--text-muted);
  margin: 0;
  line-height: 1.5;
}

/* Indicators (W_base) */
.groups-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.group-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.group-header {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
}

.group-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.group-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.group-name {
  font-size: 15px;
  font-weight: 600;
  margin: 0;
}

.indicators-table {
  border: none;
}

.key-text {
  font-size: 12px;
  color: var(--text-muted);
  font-family: monospace;
}

.add-indicator {
  padding: 12px 20px;
  border-top: 1px solid var(--border);
}

/* Reference */
.ref-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 24px;
}

.section-subtitle {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.ref-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0 0 20px 0;
}

.ref-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 14px;
}

.ref-block {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 14px 18px;
}

.ref-block h4 {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 10px 0;
  color: var(--primary);
}

.ref-block ul {
  margin: 0;
  padding-left: 18px;
}

.ref-block li {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.7;
}

.ref-formula {
  margin-top: 24px;
  padding: 16px 20px;
  background: var(--primary-soft, #eef2ff);
  border-radius: var(--radius);
  font-size: 15px;
  font-weight: 600;
  color: var(--primary);
  text-align: center;
}
</style>
