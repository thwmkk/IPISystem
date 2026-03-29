<template>
  <div class="works-page">
    <!-- Header -->
    <div class="page-top">
      <div>
        <h2 class="page-title">Мои работы</h2>
        <p class="page-subtitle">Управление научными и техническими работами</p>
      </div>
      <el-button type="primary" @click="goToAdd">
        <el-icon><Plus /></el-icon>
        Добавить работу
      </el-button>
    </div>

    <!-- Filters -->
    <div class="filters-card">
      <div class="filters-row">
        <el-select v-model="filters.type" placeholder="Тип работы" clearable style="width: 180px">
          <el-option label="Научная" value="scientific" />
          <el-option label="Организационная" value="organizational" />
          <el-option label="Техническая" value="technical" />
        </el-select>

        <el-select v-model="filters.status" placeholder="Статус" clearable style="width: 160px">
          <el-option label="Подтверждено" value="approved" />
          <el-option label="Ожидает" value="pending" />
          <el-option label="Отклонено" value="rejected" />
        </el-select>

        <el-date-picker
          v-model="filters.date"
          type="daterange"
          range-separator="—"
          start-placeholder="От"
          end-placeholder="До"
          style="width: 260px"
        />

        <el-button @click="resetFilters">Сбросить</el-button>
      </div>
    </div>

    <!-- Table -->
    <div class="table-card">
      <el-table :data="works" stripe style="width: 100%">
        <el-table-column prop="title" label="Название" min-width="200">
          <template #default="{ row }">
            <span class="work-title">{{ row.title }}</span>
          </template>
        </el-table-column>

        <el-table-column label="Тип" width="160">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.type)" effect="light">
              {{ getTypeLabel(row.type) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="category" label="Категория" width="140" />
        <el-table-column prop="date" label="Дата" width="120" />

        <el-table-column prop="points" label="Баллы" width="100" align="center">
          <template #default="{ row }">
            <span class="points-badge">{{ row.points }}</span>
          </template>
        </el-table-column>

        <el-table-column label="Статус" width="140">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" effect="light">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="" width="100" align="right">
          <template #default="{ row }">
            <el-button size="small" circle @click="editWork(row)">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button size="small" circle type="danger" @click="deleteWork(row)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Plus, Edit, Delete } from "@element-plus/icons-vue";

const works = ref([
  { title: "Статья в журнале Nature", type: "scientific", category: "Статья", date: "2026-03-01", points: 10, status: "approved" },
  { title: "Доклад на конференции", type: "scientific", category: "Доклад", date: "2026-02-15", points: 5, status: "pending" },
  { title: "Разработка модуля ML", type: "technical", category: "Код", date: "2026-02-20", points: 8, status: "approved" },
  { title: "Организация семинара", type: "organizational", category: "Мероприятие", date: "2026-01-10", points: 3, status: "rejected" },
]);

const filters = ref({ type: "", status: "", date: [] });

const getTypeLabel = (type: string) =>
  ({ scientific: "Научная", organizational: "Организационная", technical: "Техническая" })[type];

const getTypeTag = (type: string) =>
  ({ scientific: "primary", organizational: "success", technical: "warning" })[type];

const getStatusLabel = (status: string) =>
  ({ approved: "Подтверждено", pending: "Ожидает", rejected: "Отклонено" })[status];

const getStatusTag = (status: string) =>
  ({ approved: "success", pending: "warning", rejected: "danger" })[status];

const resetFilters = () => { filters.value = { type: "", status: "", date: [] }; };
const goToAdd = () => { console.log("go to add page"); };
const editWork = (row: any) => { console.log("edit", row); };
const deleteWork = (row: any) => { console.log("delete", row); };
</script>

<style scoped>
.works-page {
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

.filters-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 16px 20px;
}

.filters-row {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

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
</style>
