<template>
  <div class="verification-page">
    <div class="page-top">
      <div>
        <h2 class="page-title">Проверка работ</h2>
        <p class="page-subtitle">Верификация и оценка работ сотрудников</p>
      </div>
    </div>

    <!-- Stats row -->
    <div class="verify-stats">
      <div class="vs-card">
        <span class="vs-num pending-num">{{ pendingCount }}</span>
        <span class="vs-label">Ожидают проверки</span>
      </div>
      <div class="vs-card">
        <span class="vs-num approved-num">{{ approvedCount }}</span>
        <span class="vs-label">Подтверждено</span>
      </div>
      <div class="vs-card">
        <span class="vs-num rejected-num">{{ rejectedCount }}</span>
        <span class="vs-label">Отклонено</span>
      </div>
    </div>

    <!-- Table -->
    <div class="table-card">
      <el-table :data="works" stripe>
        <el-table-column prop="title" label="Название" min-width="180">
          <template #default="{ row }">
            <span class="work-title">{{ row.title }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="author" label="Сотрудник" width="160" />

        <el-table-column label="Тип" width="160">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.type)" effect="light" size="small">
              {{ getTypeLabel(row.type) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="category" label="Категория" width="130" />
        <el-table-column prop="date" label="Дата" width="120" />

        <el-table-column prop="points" label="Баллы" width="90" align="center">
          <template #default="{ row }">
            <span class="points-badge">{{ row.points }}</span>
          </template>
        </el-table-column>

        <el-table-column label="Статус" width="140">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" effect="light" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="" width="180" align="right">
          <template #default="{ row }">
            <el-button size="small" circle @click="openModal(row)">
              <el-icon><View /></el-icon>
            </el-button>
            <el-button size="small" circle type="success" @click="approve(row)">
              <el-icon><Check /></el-icon>
            </el-button>
            <el-button size="small" circle type="danger" @click="reject(row)">
              <el-icon><Close /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Modal -->
    <el-dialog v-model="dialogVisible" width="600px" title="Просмотр работы">
      <div v-if="selectedWork" class="modal-body">
        <div class="modal-grid">
          <div class="modal-field">
            <span class="modal-label">Название</span>
            <span class="modal-value">{{ selectedWork.title }}</span>
          </div>
          <div class="modal-field">
            <span class="modal-label">Сотрудник</span>
            <span class="modal-value">{{ selectedWork.author }}</span>
          </div>
          <div class="modal-field">
            <span class="modal-label">Тип</span>
            <span class="modal-value">{{ getTypeLabel(selectedWork.type) }}</span>
          </div>
          <div class="modal-field">
            <span class="modal-label">Категория</span>
            <span class="modal-value">{{ selectedWork.category }}</span>
          </div>
          <div class="modal-field">
            <span class="modal-label">Дата</span>
            <span class="modal-value">{{ selectedWork.date }}</span>
          </div>
          <div class="modal-field">
            <span class="modal-label">Баллы</span>
            <span class="modal-value points-badge">{{ selectedWork.points }}</span>
          </div>
        </div>

        <div class="modal-actions">
          <el-button type="success" @click="approve(selectedWork); dialogVisible = false;">
            <el-icon><Check /></el-icon>
            Подтвердить
          </el-button>
          <el-button type="danger" @click="reject(selectedWork); dialogVisible = false;">
            <el-icon><Close /></el-icon>
            Отклонить
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { View, Check, Close } from "@element-plus/icons-vue";

const dialogVisible = ref(false);
const selectedWork = ref<any>(null);

const works = ref([
  { title: "Статья в Nature", author: "Иванов И.И.", type: "scientific", category: "Статья", date: "2026-03-01", points: 10, status: "pending" },
  { title: "Доклад на ICML", author: "Петров П.П.", type: "scientific", category: "Доклад", date: "2026-02-20", points: 5, status: "pending" },
  { title: "Модуль визуализации", author: "Сидоров С.С.", type: "technical", category: "Код", date: "2026-03-05", points: 8, status: "approved" },
  { title: "Организация хакатона", author: "Козлова А.В.", type: "organizational", category: "Мероприятие", date: "2026-02-28", points: 3, status: "rejected" },
]);

const pendingCount = computed(() => works.value.filter((w) => w.status === "pending").length);
const approvedCount = computed(() => works.value.filter((w) => w.status === "approved").length);
const rejectedCount = computed(() => works.value.filter((w) => w.status === "rejected").length);

const openModal = (row: any) => { selectedWork.value = row; dialogVisible.value = true; };
const approve = (row: any) => { row.status = "approved"; };
const reject = (row: any) => { row.status = "rejected"; };

const getTypeLabel = (type: string) =>
  ({ scientific: "Научная", organizational: "Организационная", technical: "Техническая" })[type];
const getTypeTag = (type: string) =>
  ({ scientific: "primary", organizational: "success", technical: "warning" })[type];
const getStatusLabel = (status: string) =>
  ({ approved: "Подтверждено", pending: "Ожидает", rejected: "Отклонено" })[status];
const getStatusTag = (status: string) =>
  ({ approved: "success", pending: "warning", rejected: "danger" })[status];
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
  grid-template-columns: repeat(3, 1fr);
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

/* Modal */
.modal-body {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.modal-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.modal-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.modal-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.modal-value {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-primary);
}

.modal-actions {
  display: flex;
  gap: 12px;
  padding-top: 8px;
  border-top: 1px solid var(--border);
}
</style>
