<template>
  <div class="tasks-page">
    <div class="page-top">
      <div>
        <h2 class="page-title">Задачи</h2>
        <p class="page-subtitle">Отслеживание и управление задачами</p>
      </div>
    </div>

    <!-- Kanban -->
    <div class="kanban">
      <div v-for="col in columns" :key="col.status" class="kanban-col">
        <div class="col-header">
          <div class="col-header-left">
            <div class="col-dot" :class="col.status"></div>
            <span class="col-title">{{ col.label }}</span>
          </div>
          <span class="col-count">{{ getTasks(col.status).length }}</span>
        </div>

        <div class="col-body">
          <div
            v-for="task in getTasks(col.status)"
            :key="task.id"
            class="task-card"
          >
            <h4 class="task-title">{{ task.title }}</h4>
            <div class="task-meta">
              <el-icon :size="14"><Calendar /></el-icon>
              <span>{{ task.deadline }}</span>
            </div>
            <div class="task-actions">
              <el-button
                v-if="task.status === 'assigned'"
                size="small"
                type="primary"
                @click="startTask(task)"
              >
                Начать
              </el-button>
              <el-button
                v-if="task.status === 'in_progress'"
                size="small"
                type="success"
                @click="completeTask(task)"
              >
                Завершить
              </el-button>
            </div>
          </div>

          <div v-if="getTasks(col.status).length === 0" class="col-empty">
            Нет задач
          </div>
        </div>
      </div>
    </div>

    <!-- Task pool -->
    <div class="pool-section">
      <h3 class="section-title">Доступные задачи</h3>
      <div class="pool-grid">
        <div v-for="task in poolTasks" :key="task.id" class="pool-card">
          <div class="pool-card-top">
            <h4 class="task-title">{{ task.title }}</h4>
            <div class="task-meta">
              <el-icon :size="14"><Calendar /></el-icon>
              <span>{{ task.deadline }}</span>
            </div>
          </div>
          <el-button type="primary" size="small" @click="takeTask(task)">
            Взять задачу
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Calendar } from "@element-plus/icons-vue";

const columns = [
  { status: "assigned", label: "Назначена" },
  { status: "in_progress", label: "В работе" },
  { status: "completed", label: "Выполнена" },
  { status: "overdue", label: "Просрочена" },
];

const tasks = ref([
  { id: 1, title: "Написать статью", deadline: "2026-03-30", status: "assigned" },
  { id: 2, title: "Сделать отчет", deadline: "2026-03-20", status: "in_progress" },
  { id: 4, title: "Ревью диссертации", deadline: "2026-03-15", status: "completed" },
]);

const poolTasks = ref([
  { id: 3, title: "Подготовить доклад", deadline: "2026-04-01" },
  { id: 5, title: "Анализ данных эксперимента", deadline: "2026-04-05" },
]);

const getTasks = (status: string) => tasks.value.filter((t) => t.status === status);

const startTask = (task: any) => { task.status = "in_progress"; };
const completeTask = (task: any) => { task.status = "completed"; };
const takeTask = (task: any) => {
  tasks.value.push({ ...task, status: "assigned" });
  poolTasks.value = poolTasks.value.filter((t) => t.id !== task.id);
};
</script>

<style scoped>
.tasks-page {
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

/* Kanban */
.kanban {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.kanban-col {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  min-height: 300px;
}

.col-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 16px 12px;
  border-bottom: 1px solid var(--border);
}

.col-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.col-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.col-dot.assigned { background: var(--warning); }
.col-dot.in_progress { background: var(--primary); }
.col-dot.completed { background: var(--success); }
.col-dot.overdue { background: var(--danger); }

.col-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.col-count {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  background: var(--bg);
  padding: 2px 8px;
  border-radius: 10px;
}

.col-body {
  padding: 12px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.col-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  font-size: 13px;
}

.task-card {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  transition: all var(--transition);
}

.task-card:hover {
  box-shadow: var(--shadow-sm);
  border-color: var(--text-muted);
}

.task-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin: 0;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-muted);
}

.task-actions {
  display: flex;
  gap: 8px;
}

/* Pool */
.section-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
}

.pool-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.pool-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  transition: all var(--transition);
}

.pool-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.pool-card-top {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
</style>
