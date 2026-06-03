<template>
  <div class="verification-page">
    <div class="page-top">
      <div>
        <h2 class="page-title">Проверка работ</h2>
        <p class="page-subtitle">Верификация и оценка работ сотрудников</p>
      </div>
    </div>

    <!-- Stats row (clickable as filters) -->
    <div class="verify-stats">
      <div
        class="vs-card"
        :class="{ active: statusFilter === '' }"
        @click="statusFilter = ''"
      >
        <span class="vs-num">{{ requests.length }}</span>
        <span class="vs-label">Все</span>
      </div>
      <div
        class="vs-card"
        :class="{ active: statusFilter === 'pending' }"
        @click="statusFilter = 'pending'"
      >
        <span class="vs-num pending-num">{{ pendingCount }}</span>
        <span class="vs-label">Ожидают проверки</span>
      </div>
      <div
        class="vs-card"
        :class="{ active: statusFilter === 'approved' }"
        @click="statusFilter = 'approved'"
      >
        <span class="vs-num approved-num">{{ approvedCount }}</span>
        <span class="vs-label">Подтверждено</span>
      </div>
      <div
        class="vs-card"
        :class="{ active: statusFilter === 'rejected' }"
        @click="statusFilter = 'rejected'"
      >
        <span class="vs-num rejected-num">{{ rejectedCount }}</span>
        <span class="vs-label">Отклонено</span>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-bar">
      <el-input
        v-model="search"
        placeholder="Поиск по сотруднику или работе"
        clearable
        style="width: 320px"
      />
      <el-select v-model="categoryFilter" placeholder="Категория" clearable style="width: 200px">
        <el-option label="Научная" value="scientific" />
        <el-option label="Техническая" value="technical" />
        <el-option label="Организационная" value="organizational" />
      </el-select>
    </div>

    <!-- Table -->
    <div class="table-card">
      <el-table :data="filteredRequests" stripe v-loading="loading">
        <!-- Expand row for details -->
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="work-details" v-if="row.work_details">
              <h4 class="details-title">Подробности работы</h4>
              <div class="details-grid">
                <div class="detail-item">
                  <span class="detail-label">Название</span>
                  <span class="detail-value">{{ row.work_details.title }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Тип</span>
                  <span class="detail-value">{{ row.work_details.work_type }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">Баллы</span>
                  <span class="detail-value points-val">{{ row.work_details.points }}</span>
                </div>

                <!-- Publication -->
                <template v-if="row.work_details.publication">
                  <div class="detail-item">
                    <span class="detail-label">Публикация</span>
                    <span class="detail-value">{{ row.work_details.publication.title }} ({{ row.work_details.publication.year }})</span>
                  </div>
                  <template v-if="row.work_details.publication.article">
                    <div class="detail-item">
                      <span class="detail-label">Журнал</span>
                      <span class="detail-value">{{ row.work_details.publication.article.journal }}</span>
                    </div>
                    <div class="detail-item" v-if="row.work_details.publication.article.doi">
                      <span class="detail-label">DOI</span>
                      <span class="detail-value">{{ row.work_details.publication.article.doi }}</span>
                    </div>
                    <div class="detail-item" v-if="row.work_details.publication.article.quartile">
                      <span class="detail-label">Квартиль</span>
                      <span class="detail-value">Q{{ row.work_details.publication.article.quartile }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="detail-label">Scopus</span>
                      <span class="detail-value">{{ row.work_details.publication.article.is_scopus ? 'Да' : 'Нет' }}</span>
                    </div>
                  </template>
                  <template v-if="row.work_details.publication.monograph">
                    <div class="detail-item">
                      <span class="detail-label">Издательство</span>
                      <span class="detail-value">{{ row.work_details.publication.monograph.publisher }}</span>
                    </div>
                    <div class="detail-item" v-if="row.work_details.publication.monograph.isbn">
                      <span class="detail-label">ISBN</span>
                      <span class="detail-value">{{ row.work_details.publication.monograph.isbn }}</span>
                    </div>
                    <div class="detail-item" v-if="row.work_details.publication.monograph.pages_count">
                      <span class="detail-label">Страниц</span>
                      <span class="detail-value">{{ row.work_details.publication.monograph.pages_count }}</span>
                    </div>
                  </template>
                </template>

                <!-- Dissertation -->
                <template v-if="row.work_details.dissertation">
                  <div class="detail-item">
                    <span class="detail-label">Этап</span>
                    <span class="detail-value">{{ row.work_details.dissertation.stage }}</span>
                  </div>
                  <div class="detail-item" v-if="row.work_details.dissertation.defense_date">
                    <span class="detail-label">Дата защиты</span>
                    <span class="detail-value">{{ row.work_details.dissertation.defense_date }}</span>
                  </div>
                </template>

                <!-- Project -->
                <template v-if="row.work_details.project">
                  <div class="detail-item">
                    <span class="detail-label">Роль</span>
                    <span class="detail-value">{{ row.work_details.project.role }}</span>
                  </div>
                  <div class="detail-item" v-if="row.work_details.project.budget">
                    <span class="detail-label">Бюджет</span>
                    <span class="detail-value">{{ row.work_details.project.budget.toLocaleString() }} руб.</span>
                  </div>
                  <div class="detail-item" v-if="row.work_details.project.start_date">
                    <span class="detail-label">Период</span>
                    <span class="detail-value">{{ row.work_details.project.start_date }} — {{ row.work_details.project.end_date || '...' }}</span>
                  </div>
                </template>

                <!-- Software -->
                <template v-if="row.work_details.software">
                  <div class="detail-item">
                    <span class="detail-label">Версия</span>
                    <span class="detail-value">{{ row.work_details.software.version }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Коммерческое</span>
                    <span class="detail-value">{{ row.work_details.software.is_commercial ? 'Да' : 'Нет' }}</span>
                  </div>
                </template>

                <!-- Organizational -->
                <div class="detail-item" v-if="row.work_details.event_date">
                  <span class="detail-label">Дата мероприятия</span>
                  <span class="detail-value">{{ row.work_details.event_date }}</span>
                </div>
                <div class="detail-item" v-if="row.work_details.participants_count">
                  <span class="detail-label">Участников</span>
                  <span class="detail-value">{{ row.work_details.participants_count }}</span>
                </div>

                <!-- Technical -->
                <div class="detail-item" v-if="row.work_details.work_date">
                  <span class="detail-label">Дата</span>
                  <span class="detail-value">{{ row.work_details.work_date }}</span>
                </div>
                <div class="detail-item" v-if="row.work_details.registration_number">
                  <span class="detail-label">Рег. номер</span>
                  <span class="detail-value">{{ row.work_details.registration_number }}</span>
                </div>
                <div class="detail-item" v-if="row.work_details.metric">
                  <span class="detail-label">Метрика</span>
                  <span class="detail-value">{{ row.work_details.metric }}</span>
                </div>
              </div>
            </div>
            <div v-else class="work-details">
              <p style="color: var(--text-secondary)">Нет данных о работе</p>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="requester_name" label="Сотрудник" width="160" />

        <el-table-column label="Работа" min-width="180">
          <template #default="{ row }">
            <span class="work-title">{{ row.work_title }}</span>
          </template>
        </el-table-column>

        <el-table-column label="Тип" width="160">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.work_type)" effect="light" size="small">
              {{ getTypeLabel(row.work_type) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="request_date" label="Дата" width="120" />

        <el-table-column label="Статус" width="140">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" effect="light" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="" width="220" align="right">
          <template #default="{ row }">
            <el-button size="small" circle type="primary" @click="openEditDialog(row)">
              <el-icon><Edit /></el-icon>
            </el-button>
            <template v-if="row.status === 'pending'">
              <el-button size="small" circle type="success" @click="handleApprove(row)">
                <el-icon><Check /></el-icon>
              </el-button>
              <el-button size="small" circle type="danger" @click="handleReject(row)">
                <el-icon><Close /></el-icon>
              </el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Edit Work Dialog -->
    <el-dialog v-model="showEditDialog" title="Редактировать работу" width="580px" destroy-on-close>
      <el-form :model="editForm" label-position="top" v-if="editForm">
        <el-form-item label="Название">
          <el-input v-model="editForm.title" />
        </el-form-item>
        <div class="form-row">
          <el-form-item label="Тип работы">
            <el-select v-model="editForm.work_type" style="width: 100%" placeholder="Выберите тип">
              <el-option
                v-for="ind in currentTypeOptions"
                :key="ind.id"
                :label="ind.name"
                :value="ind.work_type_key"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="Баллы">
            <el-input-number v-model="editForm.points" :min="0" :step="0.5" />
          </el-form-item>
        </div>

        <!-- Scientific: Publication / Article -->
        <template v-if="editForm.publication">
          <el-divider content-position="left">Публикация</el-divider>
          <div class="form-row">
            <el-form-item label="Название публикации">
              <el-input v-model="editForm.publication.title" />
            </el-form-item>
            <el-form-item label="Год">
              <el-input-number v-model="editForm.publication.year" :min="2000" :max="2030" />
            </el-form-item>
          </div>
          <template v-if="editForm.publication.article">
            <div class="form-row">
              <el-form-item label="Журнал">
                <el-input v-model="editForm.publication.article.journal" />
              </el-form-item>
              <el-form-item label="DOI">
                <el-input v-model="editForm.publication.article.doi" />
              </el-form-item>
            </div>
            <div class="form-row">
              <el-form-item label="Квартиль">
                <el-select v-model="editForm.publication.article.quartile" clearable>
                  <el-option label="Q1" :value="1" />
                  <el-option label="Q2" :value="2" />
                  <el-option label="Q3" :value="3" />
                  <el-option label="Q4" :value="4" />
                </el-select>
              </el-form-item>
              <el-form-item label="Scopus">
                <el-checkbox v-model="editForm.publication.article.is_scopus">Индексирована в Scopus</el-checkbox>
              </el-form-item>
            </div>
          </template>
          <template v-if="editForm.publication.monograph">
            <div class="form-row">
              <el-form-item label="Издательство">
                <el-input v-model="editForm.publication.monograph.publisher" />
              </el-form-item>
              <el-form-item label="ISBN">
                <el-input v-model="editForm.publication.monograph.isbn" />
              </el-form-item>
            </div>
            <el-form-item label="Кол-во страниц">
              <el-input-number v-model="editForm.publication.monograph.pages_count" :min="0" />
            </el-form-item>
          </template>
        </template>

        <!-- Scientific: Dissertation -->
        <template v-if="editForm.dissertation">
          <el-divider content-position="left">Диссертация</el-divider>
          <div class="form-row">
            <el-form-item label="Этап">
              <el-input v-model="editForm.dissertation.stage" />
            </el-form-item>
            <el-form-item label="Дата защиты">
              <el-date-picker v-model="editForm.dissertation.defense_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </div>
        </template>

        <!-- Scientific: Project -->
        <template v-if="editForm.project">
          <el-divider content-position="left">Участие в проекте</el-divider>
          <div class="form-row">
            <el-form-item label="Роль">
              <el-input v-model="editForm.project.role" />
            </el-form-item>
            <el-form-item label="Бюджет (руб.)">
              <el-input-number v-model="editForm.project.budget" :min="0" :step="100000" style="width: 100%" />
            </el-form-item>
          </div>
          <div class="form-row">
            <el-form-item label="Дата начала">
              <el-date-picker v-model="editForm.project.start_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Дата завершения">
              <el-date-picker v-model="editForm.project.end_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </div>
        </template>

        <!-- Scientific: Software -->
        <template v-if="editForm.software">
          <el-divider content-position="left">Программное обеспечение</el-divider>
          <div class="form-row">
            <el-form-item label="Версия">
              <el-input v-model="editForm.software.version" />
            </el-form-item>
            <el-form-item label="">
              <el-checkbox v-model="editForm.software.is_commercial">Коммерческое ПО</el-checkbox>
            </el-form-item>
          </div>
        </template>

        <!-- Organizational fields -->
        <template v-if="editRow?.work_type === 'organizational'">
          <div class="form-row">
            <el-form-item label="Дата мероприятия">
              <el-date-picker v-model="editForm.event_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Кол-во участников">
              <el-input-number v-model="editForm.participants_count" :min="0" />
            </el-form-item>
          </div>
        </template>

        <!-- Technical fields -->
        <template v-if="editRow?.work_type === 'technical'">
          <div class="form-row">
            <el-form-item label="Дата">
              <el-date-picker v-model="editForm.work_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Номер регистрации">
              <el-input v-model="editForm.registration_number" />
            </el-form-item>
          </div>
          <el-form-item label="Метрика">
            <el-input v-model="editForm.metric" />
          </el-form-item>
        </template>
      </el-form>

      <template #footer>
        <el-button @click="showEditDialog = false">Отмена</el-button>
        <el-button v-if="editRow?.status === 'pending'" type="success" :loading="savingEdit" @click="handleEditAndApprove">
          Сохранить и подтвердить
        </el-button>
        <el-button type="primary" :loading="savingEdit" @click="handleEditSave">Сохранить</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { Check, Close, Edit } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { worksApi } from "@/api/works";
import { kpiApi, type KPIGroupData } from "@/api/kpi";

interface WorkDetails {
  title: string
  work_type: string
  points: number
  created_at?: string | null
  event_date?: string | null
  participants_count?: number | null
  work_date?: string | null
  registration_number?: string | null
  metric?: string | null
  publication?: any
  dissertation?: any
  project?: any
  software?: any
}

interface VR {
  id: number
  work_type: string
  requester: number
  requester_name: string
  evaluator: number | null
  evaluator_name: string | null
  status: string
  request_date: string
  comment: string | null
  work_title: string
  work_details: WorkDetails | null
}

const loading = ref(false);
const requests = ref<VR[]>([]);
const kpiGroups = ref<KPIGroupData[]>([]);

const statusFilter = ref<'' | 'pending' | 'approved' | 'rejected'>('');
const categoryFilter = ref<'' | 'scientific' | 'organizational' | 'technical'>('');
const search = ref('');

const filteredRequests = computed(() => {
  return requests.value.filter(r => {
    if (statusFilter.value && r.status !== statusFilter.value) return false;
    if (categoryFilter.value && r.work_type !== categoryFilter.value) return false;
    if (search.value) {
      const q = search.value.toLowerCase();
      const inEmp = r.requester_name?.toLowerCase().includes(q);
      const inWork = r.work_title?.toLowerCase().includes(q);
      if (!inEmp && !inWork) return false;
    }
    return true;
  });
});

const currentTypeOptions = computed(() => {
  if (!editRow.value) return [];
  const cat = editRow.value.work_type;
  const pattern = cat === 'scientific' ? /науч/
    : cat === 'organizational' ? /организ/
    : /техн/;
  const group = kpiGroups.value.find(g => pattern.test(g.name.toLowerCase()));
  return group?.indicators || [];
});

const pendingCount = computed(() => requests.value.filter((r) => r.status === "pending").length);
const approvedCount = computed(() => requests.value.filter((r) => r.status === "approved").length);
const rejectedCount = computed(() => requests.value.filter((r) => r.status === "rejected").length);

const getTypeLabel = (type: string) =>
  ({ scientific: "Научная", organizational: "Организационная", technical: "Техническая" }[type] || type);
const getTypeTag = (type: string) =>
  ({ scientific: "", organizational: "warning", technical: "info" }[type] as any);
const getStatusLabel = (status: string) =>
  ({ approved: "Подтверждено", pending: "Ожидает", rejected: "Отклонено" }[status]);
const getStatusTag = (status: string) =>
  ({ approved: "success", pending: "warning", rejected: "danger" }[status] as any);

// Edit state
const showEditDialog = ref(false);
const savingEdit = ref(false);
const editRow = ref<VR | null>(null);
const editForm = ref<any>(null);

function openEditDialog(row: VR) {
  editRow.value = row;
  // Deep clone work_details into form
  editForm.value = JSON.parse(JSON.stringify(row.work_details || { title: '', work_type: '', points: 0 }));
  showEditDialog.value = true;
}

async function handleEditSave() {
  if (!editRow.value) return;
  savingEdit.value = true;
  try {
    const { data } = await worksApi.updateVerificationWork(editRow.value.id, editForm.value);
    const idx = requests.value.findIndex((r) => r.id === editRow.value!.id);
    if (idx !== -1) {
      requests.value[idx] = data;
    }
    showEditDialog.value = false;
    ElMessage.success("Работа обновлена");
  } catch {
    ElMessage.error("Ошибка при сохранении");
  } finally {
    savingEdit.value = false;
  }
}

async function handleEditAndApprove() {
  if (!editRow.value) return;
  savingEdit.value = true;
  try {
    await worksApi.updateVerificationWork(editRow.value.id, editForm.value);
    await worksApi.approveVerification(editRow.value.id);
    await fetchRequests();
    showEditDialog.value = false;
    ElMessage.success("Работа обновлена и подтверждена");
  } catch {
    ElMessage.error("Ошибка");
  } finally {
    savingEdit.value = false;
  }
}

async function fetchRequests() {
  loading.value = true;
  try {
    const { data } = await worksApi.getVerificationRequests();
    requests.value = data;
  } catch {
    ElMessage.error("Не удалось загрузить заявки");
  } finally {
    loading.value = false;
  }
}

async function handleApprove(row: VR) {
  try {
    await worksApi.approveVerification(row.id);
    row.status = "approved";
    ElMessage.success("Работа подтверждена");
    await fetchRequests();
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || "Ошибка подтверждения");
  }
}

async function handleReject(row: VR) {
  try {
    await worksApi.rejectVerification(row.id);
    row.status = "rejected";
    ElMessage.success("Работа отклонена");
    await fetchRequests();
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || "Ошибка отклонения");
  }
}

async function fetchKpiGroups() {
  try {
    const { data } = await kpiApi.getGroups();
    kpiGroups.value = data;
  } catch (_) {}
}

onMounted(() => {
  fetchRequests();
  fetchKpiGroups();
});
</script>

<style scoped>
.verification-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
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

/* Verify stats */
.verify-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.vs-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  cursor: pointer;
  transition: all var(--transition);
}

.vs-card:hover {
  border-color: var(--primary);
}

.vs-card.active {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-soft, rgba(99, 102, 241, 0.15));
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
}

.vs-num {
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.pending-num { color: var(--warning); }
.approved-num { color: var(--success); }
.rejected-num { color: var(--danger); }

.vs-label {
  font-size: 13px;
  color: var(--text-secondary);
}

/* Table */
.table-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.work-title {
  font-weight: 500;
  color: var(--text-primary);
}

/* Expand details */
.work-details {
  padding: 16px 24px;
}

.details-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text-primary);
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.detail-label {
  font-size: 12px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-value {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
}

.points-val {
  color: var(--primary);
  font-weight: 600;
}

/* Edit dialog */
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
</style>
