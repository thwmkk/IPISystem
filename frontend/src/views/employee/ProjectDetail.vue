<template>
  <div class="project-detail" v-loading="loading">
    <!-- Top bar -->
    <div class="topbar">
      <el-button link @click="goBack">
        <el-icon><ArrowLeft /></el-icon>
        {{ route.query.from === 'department' ? 'Назад в Мой отдел' : 'Назад к проектам' }}
      </el-button>
      <div class="topbar-actions" v-if="project && isCreator">
        <el-button
          v-if="!project.completed_at"
          type="success"
          @click="openCompleteDialog"
        >
          <el-icon><CircleCheck /></el-icon>
          Завершить проект
        </el-button>
        <el-button v-if="!project.completed_at" @click="openEditDialog">
          <el-icon><Edit /></el-icon>
          Редактировать
        </el-button>
        <el-button
          v-if="!project.completed_at"
          type="danger"
          plain
          @click="handleDelete"
        >
          <el-icon><Delete /></el-icon>
          Удалить
        </el-button>
      </div>
    </div>

    <div v-if="project" class="content">
      <!-- Header -->
      <div class="project-header-card">
        <div class="project-header-top">
          <div class="project-icon-lg">
            <el-icon :size="28"><Folder /></el-icon>
          </div>
          <div class="project-header-main">
            <div class="project-title-row">
              <h1 class="project-title">{{ project.name }}</h1>
              <el-tag size="small" :type="getStatusType(project)" effect="light">
                {{ getStatusLabel(project) }}
              </el-tag>
            </div>
            <p v-if="project.description" class="project-description">
              {{ project.description }}
            </p>
          </div>
        </div>

        <div class="project-stats">
          <div class="stat">
            <el-icon :size="16"><User /></el-icon>
            <div>
              <div class="stat-label">Создатель</div>
              <div class="stat-value">{{ project.creator_name }}</div>
            </div>
          </div>
          <div class="stat">
            <el-icon :size="16"><Calendar /></el-icon>
            <div>
              <div class="stat-label">Период</div>
              <div class="stat-value">
                {{ project.start_date }}<span v-if="project.end_date"> — {{ project.end_date }}</span>
              </div>
            </div>
          </div>
          <div class="stat" v-if="project.budget">
            <el-icon :size="16"><Money /></el-icon>
            <div>
              <div class="stat-label">Бюджет</div>
              <div class="stat-value">{{ formatBudget(project.budget) }}</div>
            </div>
          </div>
          <div class="stat">
            <el-icon :size="16"><UserFilled /></el-icon>
            <div>
              <div class="stat-label">Участников</div>
              <div class="stat-value">{{ project.members?.length || 0 }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <el-tabs v-model="activeTab" class="project-tabs">
        <el-tab-pane name="info" label="Информация и участники">
          <!-- Members -->
          <div class="panel">
            <div class="panel-header">
              <h2 class="panel-title">Участники ({{ project.members?.length || 0 }})</h2>
              <el-button
                v-if="isCreator && !project.completed_at"
                size="small"
                type="primary"
                @click="openAddMemberDialog"
              >
                <el-icon><Plus /></el-icon>
                Добавить
              </el-button>
            </div>
            <div class="members-grid">
              <div
                v-for="m in project.members || []"
                :key="m.id"
                class="member-card"
              >
                <div class="member-card-head">
                  <div class="member-avatar">{{ getInitials(m.employee_name) }}</div>
                  <div class="member-info">
                    <div class="member-name">{{ m.employee_name }}</div>
                    <div class="member-role" v-if="m.employee === project.creator">
                      Создатель
                    </div>
                  </div>
                  <el-button
                    v-if="isCreator && m.employee !== project.creator && !project.completed_at"
                    size="small"
                    link
                    type="danger"
                    @click="handleRemoveMember(m.employee)"
                  >
                    <el-icon><Close /></el-icon>
                  </el-button>
                </div>
                <div class="member-stats">
                  <div class="stat-pill">
                    <span class="pill-num">{{ memberStats(m.employee).total }}</span>
                    <span class="pill-lbl">всего</span>
                  </div>
                  <div class="stat-pill stat-done">
                    <span class="pill-num">{{ memberStats(m.employee).done }}</span>
                    <span class="pill-lbl">сделано</span>
                  </div>
                  <div class="stat-pill stat-progress">
                    <span class="pill-num">{{ memberStats(m.employee).progress }}</span>
                    <span class="pill-lbl">в работе</span>
                  </div>
                  <div v-if="memberStats(m.employee).overdue" class="stat-pill stat-bad">
                    <span class="pill-num">{{ memberStats(m.employee).overdue }}</span>
                    <span class="pill-lbl">просрочено</span>
                  </div>
                </div>
                <div class="member-bar">
                  <div
                    class="member-bar-fill"
                    :style="{ width: memberStats(m.employee).percent + '%' }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane name="tasks">
          <template #label>
            Задачи <span class="tab-badge">{{ tasks.length }}</span>
          </template>

          <!-- Filters -->
          <div class="filters-bar">
            <el-input
              v-model="taskFilters.search"
              placeholder="Поиск по названию"
              clearable
              style="width: 240px"
            />
            <el-select
              v-model="taskFilters.status"
              placeholder="Статус"
              clearable
              style="width: 160px"
            >
              <el-option label="Назначена" value="assigned" />
              <el-option label="В работе" value="in_progress" />
              <el-option label="Выполнена" value="completed" />
              <el-option label="Просрочена" value="overdue" />
            </el-select>
            <el-select
              v-model="taskFilters.assignee"
              placeholder="Исполнитель"
              clearable
              filterable
              style="width: 200px"
            >
              <el-option :label="'Не назначена'" :value="0" />
              <el-option
                v-for="m in project.members || []"
                :key="m.id"
                :label="m.employee_name"
                :value="m.employee"
              />
            </el-select>
            <el-date-picker
              v-model="taskFilters.dateRange"
              type="daterange"
              range-separator="—"
              start-placeholder="Дедлайн от"
              end-placeholder="до"
              value-format="YYYY-MM-DD"
              style="width: 280px"
            />
            <el-button v-if="hasTaskFilters" size="small" @click="resetTaskFilters">
              Сбросить
            </el-button>
            <div style="flex: 1"></div>
            <el-button
              v-if="isCreator && !project.completed_at"
              type="primary"
              @click="openCreateTaskDialog"
            >
              <el-icon><Plus /></el-icon>
              Новая задача
            </el-button>
          </div>

          <div v-if="filteredTasks.length === 0" class="empty">
            Задач нет
          </div>

          <div v-else class="tasks-list">
            <div
              v-for="task in filteredTasks"
              :key="task.id"
              class="task-card"
              :class="{ expanded: expandedId === task.id, 'is-done': task.status === 'completed' }"
            >
              <div class="task-card-head" @click="toggleExpand(task.id)">
                <div class="task-head-left">
                  <div class="status-dot" :class="task.status"></div>
                  <div class="task-head-main">
                    <div class="task-title-row">
                      <span class="task-title">{{ task.title }}</span>
                      <el-tag size="small" :type="getPriorityType(task.priority)" effect="plain">
                        {{ getPriorityLabel(task.priority) }}
                      </el-tag>
                    </div>
                    <div class="task-meta-row">
                      <span class="task-meta">
                        <el-icon :size="12"><Calendar /></el-icon>
                        {{ task.deadline }}
                      </span>
                      <span class="task-meta" v-if="task.assigned_to_name">
                        <el-icon :size="12"><User /></el-icon>
                        {{ task.assigned_to_name }}
                      </span>
                      <span class="task-meta task-meta-free" v-else>
                        Не назначена
                      </span>
                    </div>
                  </div>
                </div>
                <el-tag size="small" :type="getStatusTagType(task.status)" effect="light">
                  {{ getStatusLabel2(task.status) }}
                </el-tag>
                <el-icon class="expand-chevron" :class="{ rot: expandedId === task.id }">
                  <ArrowDown />
                </el-icon>
              </div>

              <div v-if="expandedId === task.id" class="task-card-body">
                <div v-if="task.description" class="task-description">
                  {{ task.description }}
                </div>
                <div class="task-details-grid">
                  <div class="detail">
                    <div class="detail-label">Создатель</div>
                    <div class="detail-value">{{ task.created_by_name }}</div>
                  </div>
                  <div class="detail">
                    <div class="detail-label">Создана</div>
                    <div class="detail-value">{{ formatDate(task.created_at) }}</div>
                  </div>
                  <div class="detail">
                    <div class="detail-label">Дедлайн</div>
                    <div class="detail-value">{{ formatDate(task.deadline) }}</div>
                  </div>
                </div>

                <div class="task-attachments">
                  <div class="task-attachments-head">
                    <span class="task-attachments-title">
                      <el-icon><Paperclip /></el-icon>
                      Файлы ({{ task.attachments?.length || 0 }})
                    </span>
                    <el-upload
                      :show-file-list="false"
                      :before-upload="(file) => { uploadToTask(task, file); return false }"
                      multiple
                    >
                      <el-button size="small" @click.stop>
                        <el-icon><Paperclip /></el-icon>
                        Прикрепить
                      </el-button>
                    </el-upload>
                  </div>
                  <div v-if="task.attachments?.length" class="attachments-list">
                    <div v-for="att in task.attachments" :key="att.id" class="attachment-item">
                      <el-icon><Document /></el-icon>
                      <a :href="att.url || undefined" target="_blank" class="attachment-name" @click.stop>
                        {{ att.original_name }}
                      </a>
                      <span class="attachment-size">{{ formatSize(att.size) }}</span>
                      <el-button size="small" circle type="danger" @click.stop="removeTaskAttachment(task, att.id)">
                        <el-icon><Delete /></el-icon>
                      </el-button>
                    </div>
                  </div>
                </div>

                <div class="task-actions">
                  <el-button
                    v-if="task.assigned_to === null"
                    size="small"
                    type="primary"
                    @click.stop="handleTakeTask(task)"
                  >
                    Взять задачу
                  </el-button>
                  <el-button
                    v-if="task.status === 'assigned' && task.assigned_to === auth.employeeId"
                    size="small"
                    type="primary"
                    @click.stop="handleStart(task)"
                  >
                    Начать
                  </el-button>
                  <el-button
                    v-if="task.status === 'in_progress' && task.assigned_to === auth.employeeId"
                    size="small"
                    type="success"
                    @click.stop="handleComplete(task)"
                  >
                    Завершить
                  </el-button>
                  <el-button
                    v-if="isCreator"
                    size="small"
                    type="danger"
                    plain
                    @click.stop="handleDeleteTask(task)"
                  >
                    Удалить
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- Edit project dialog -->
    <el-dialog v-model="showEditDialog" title="Редактировать проект" width="500px" destroy-on-close>
      <el-form :model="editForm" label-position="top">
        <el-form-item label="Название" required>
          <el-input v-model="editForm.name" />
        </el-form-item>
        <el-form-item label="Описание">
          <el-input v-model="editForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="Бюджет (руб.)">
          <el-input-number v-model="editForm.budget" :min="0" :step="100000" style="width: 100%" />
        </el-form-item>
        <div class="form-row">
          <el-form-item label="Дата начала" required>
            <el-date-picker v-model="editForm.start_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
          </el-form-item>
          <el-form-item label="Дата окончания">
            <el-date-picker v-model="editForm.end_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
          </el-form-item>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">Отмена</el-button>
        <el-button type="primary" @click="submitEdit" :loading="saving">Сохранить</el-button>
      </template>
    </el-dialog>

    <!-- Add member dialog -->
    <el-dialog v-model="showAddMemberDialog" title="Добавить участника" width="450px" destroy-on-close>
      <el-form label-position="top">
        <el-form-item label="Сотрудник">
          <el-select
            v-model="selectedEmployeeId"
            filterable
            placeholder="Выберите сотрудника"
            style="width: 100%"
          >
            <el-option
              v-for="emp in availableEmployees"
              :key="emp.id"
              :label="emp.full_name"
              :value="emp.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddMemberDialog = false">Отмена</el-button>
        <el-button type="primary" @click="submitAddMember" :loading="saving">Добавить</el-button>
      </template>
    </el-dialog>

    <!-- Create task dialog -->
    <el-dialog v-model="showTaskDialog" title="Новая задача проекта" width="560px" destroy-on-close>
      <el-form :model="taskForm" label-position="top">
        <el-form-item label="Название" required>
          <el-input v-model="taskForm.title" placeholder="Что нужно сделать" />
        </el-form-item>
        <el-form-item label="Описание">
          <el-input v-model="taskForm.description" type="textarea" :rows="3" />
        </el-form-item>

        <div class="form-row">
          <el-form-item label="Приоритет">
            <el-select v-model="taskForm.priority" style="width: 100%">
              <el-option label="Низкий" value="low" />
              <el-option label="Средний" value="medium" />
              <el-option label="Высокий" value="high" />
            </el-select>
          </el-form-item>
          <el-form-item label="Дедлайн" required>
            <el-date-picker
              v-model="taskForm.deadline"
              type="date"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
        </div>

        <el-form-item label="Назначить участнику (необязательно)">
          <el-select v-model="taskForm.assigned_to" clearable style="width: 100%" placeholder="Оставить пустым — задача в пул">
            <el-option
              v-for="m in project?.members || []"
              :key="m.id"
              :label="m.employee_name"
              :value="m.employee"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="Прикрепить файлы (опционально)">
          <el-upload
            :show-file-list="false"
            :before-upload="(file) => { queueTaskFile(file); return false }"
            multiple
          >
            <el-button>
              <el-icon><Paperclip /></el-icon>
              Выбрать файлы
            </el-button>
          </el-upload>
          <div v-if="pendingTaskFiles.length" class="pending-files">
            <div v-for="(f, i) in pendingTaskFiles" :key="i" class="pending-file">
              <el-icon><Document /></el-icon>
              <span>{{ f.name }}</span>
              <span class="attachment-size">{{ formatSize(f.size) }}</span>
              <el-button size="small" circle type="danger" @click="removePendingTask(i)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showTaskDialog = false">Отмена</el-button>
        <el-button type="primary" @click="submitTask" :loading="saving">Создать</el-button>
      </template>
    </el-dialog>

    <!-- Complete project dialog -->
    <el-dialog
      v-model="showCompleteDialog"
      title="Завершение проекта"
      width="640px"
      destroy-on-close
    >
      <el-form :model="completeForm" label-position="top">
        <el-alert
          type="info"
          :closable="false"
          show-icon
          style="margin-bottom: 16px"
        >
          При завершении каждому участнику будет начислена работа с указанными
          баллами (без верификации) и пересчитан IPI.
        </el-alert>

        <el-form-item label="Категория работы" required>
          <el-radio-group v-model="completeForm.kpi_group" @change="onCompleteCategoryChange">
            <el-radio-button
              v-for="g in sortedKpiGroups"
              :key="g.id"
              :label="g.id"
            >
              {{ g.name }}
            </el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="Тип работы" required>
          <el-select
            v-model="completeForm.work_type_key"
            placeholder="Выберите тип"
            style="width: 100%"
            :disabled="!completeForm.kpi_group"
          >
            <el-option
              v-for="ind in completeIndicators"
              :key="ind.id"
              :label="ind.name"
              :value="ind.work_type_key"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="Всего баллов за проект" required>
          <el-input-number
            v-model="completeForm.total_points"
            :min="0"
            :step="0.5"
            style="width: 100%"
            @change="recomputeDistribution"
          />
        </el-form-item>

        <el-form-item label="Распределение по участникам">
          <div class="distribution-hint">
            Автоматически пропорционально выполненным задачам. Значения можно
            изменить вручную.
          </div>
          <el-table :data="distributionRows" size="small" style="width: 100%">
            <el-table-column prop="name" label="Участник" min-width="180" />
            <el-table-column label="Выполнено задач" width="140" align="center">
              <template #default="{ row }">
                {{ row.completed }} / {{ row.total }}
              </template>
            </el-table-column>
            <el-table-column label="Баллы" width="140" align="center">
              <template #default="{ row }">
                <el-input-number
                  v-model="row.points"
                  :min="0"
                  :step="0.5"
                  :controls="false"
                  size="small"
                  style="width: 100%"
                />
              </template>
            </el-table-column>
          </el-table>
          <div class="distribution-sum">
            Сумма: <b>{{ distributionSum.toFixed(2) }}</b>
            <el-button
              size="small"
              link
              type="primary"
              @click="recomputeDistribution"
            >
              Пересчитать пропорционально
            </el-button>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCompleteDialog = false">Отмена</el-button>
        <el-button type="success" :loading="saving" @click="submitComplete">
          Завершить проект
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  ArrowLeft, ArrowDown, Folder, User, UserFilled, Money, Calendar,
  Plus, Edit, Delete, Close, Warning, Paperclip, Document, CircleCheck,
} from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { projectsApi } from "@/api/projects";
import { tasksApi } from "@/api/tasks";
import { kpiApi, employeesApi, type KPIGroupData } from "@/api/kpi";
import { attachmentsApi, type Attachment } from "@/api/attachments";
import { useAuthStore } from "@/store/auth";
import type { Project, Task } from "@/types/work";
import type { Employee } from "@/types/user";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const projectId = computed(() => Number(route.params.id));
const loading = ref(false);
const saving = ref(false);

const project = ref<Project | null>(null);
const tasks = ref<Task[]>([]);
const kpiGroups = ref<KPIGroupData[]>([]);
const allEmployees = ref<Employee[]>([]);

const expandedId = ref<number | null>(null);
const showEditDialog = ref(false);
const showAddMemberDialog = ref(false);
const showTaskDialog = ref(false);

const activeTab = ref<'info' | 'tasks'>('info');

const taskFilters = reactive({
  search: '',
  status: '' as '' | 'assigned' | 'in_progress' | 'completed' | 'overdue',
  assignee: null as number | null,
  dateRange: null as [string, string] | null,
});

const hasTaskFilters = computed(() =>
  !!(taskFilters.search || taskFilters.status || taskFilters.assignee !== null || taskFilters.dateRange)
);

function resetTaskFilters() {
  taskFilters.search = '';
  taskFilters.status = '';
  taskFilters.assignee = null;
  taskFilters.dateRange = null;
}

const PRIORITY_RANK: Record<string, number> = { high: 0, medium: 1, low: 2 };

const filteredTasks = computed(() => {
  let list = tasks.value;
  if (taskFilters.search) {
    const q = taskFilters.search.toLowerCase();
    list = list.filter(t => t.title.toLowerCase().includes(q));
  }
  if (taskFilters.status) list = list.filter(t => t.status === taskFilters.status);
  if (taskFilters.assignee === 0) list = list.filter(t => t.assigned_to === null);
  else if (taskFilters.assignee !== null) list = list.filter(t => t.assigned_to === taskFilters.assignee);
  if (taskFilters.dateRange) {
    const [from, to] = taskFilters.dateRange;
    list = list.filter(t => {
      if (from && t.deadline < from) return false;
      if (to && t.deadline > to) return false;
      return true;
    });
  }
  return [...list].sort((a, b) => {
    const ad = a.status === 'completed' ? 1 : 0;
    const bd = b.status === 'completed' ? 1 : 0;
    if (ad !== bd) return ad - bd;
    const ap = PRIORITY_RANK[a.priority] ?? 3;
    const bp = PRIORITY_RANK[b.priority] ?? 3;
    if (ap !== bp) return ap - bp;
    return (a.deadline || '').localeCompare(b.deadline || '');
  });
});

function memberStats(employeeId: number) {
  const my = tasks.value.filter(t => t.assigned_to === employeeId);
  const total = my.length;
  const done = my.filter(t => t.status === 'completed').length;
  const progress = my.filter(t => t.status === 'in_progress').length;
  const overdue = my.filter(t => t.status === 'overdue').length;
  const percent = total > 0 ? Math.round((done / total) * 100) : 0;
  return { total, done, progress, overdue, percent };
}

const editForm = reactive({
  name: '',
  description: '',
  budget: null as number | null,
  start_date: '',
  end_date: '',
});

const selectedEmployeeId = ref<number | null>(null);

const taskForm = reactive({
  title: '',
  description: '',
  priority: 'medium' as 'low' | 'medium' | 'high',
  deadline: '',
  assigned_to: null as number | null,
});

const showCompleteDialog = ref(false);
const completeForm = reactive({
  kpi_group: null as number | null,
  work_type_key: '',
  total_points: 10,
});
type DistributionRow = {
  employee: number
  name: string
  completed: number
  total: number
  points: number
};
const distributionRows = ref<DistributionRow[]>([]);

const pendingTaskFiles = ref<File[]>([]);

function queueTaskFile(file: File) {
  pendingTaskFiles.value.push(file);
}

function removePendingTask(i: number) {
  pendingTaskFiles.value.splice(i, 1);
}

function formatSize(bytes: number) {
  if (!bytes) return '';
  if (bytes < 1024) return `${bytes} Б`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} КБ`;
  return `${(bytes / 1024 / 1024).toFixed(1)} МБ`;
}

async function uploadToTask(task: Task, file: File) {
  try {
    const { data } = await attachmentsApi.upload(file, { task: task.id });
    if (!(task as any).attachments) (task as any).attachments = [];
    (task as any).attachments.push(data);
    ElMessage.success('Файл загружен');
  } catch {
    ElMessage.error(`Не удалось загрузить ${file.name}`);
  }
}

async function removeTaskAttachment(task: Task, attId: number) {
  try {
    await ElMessageBox.confirm('Удалить файл?', 'Подтверждение', { type: 'warning' });
  } catch { return; }
  try {
    await attachmentsApi.remove(attId);
    (task as any).attachments = (task as any).attachments.filter((a: Attachment) => a.id !== attId);
    ElMessage.success('Файл удалён');
  } catch {
    ElMessage.error('Ошибка при удалении файла');
  }
}

const isCreator = computed(
  () => !!project.value && !!auth.employeeId && project.value.creator === auth.employeeId
);

const availableEmployees = computed(() => {
  const memberIds = new Set((project.value?.members || []).map(m => m.employee));
  return allEmployees.value.filter(e => !memberIds.has(e.id));
});

const completeIndicators = computed(() => {
  if (!completeForm.kpi_group) return [];
  const g = kpiGroups.value.find(g => g.id === completeForm.kpi_group);
  return g?.indicators || [];
});

const GROUP_ORDER = ['науч', 'техн', 'организ'];
const sortedKpiGroups = computed(() => {
  const rank = (name: string) => {
    const lower = name.toLowerCase();
    for (let i = 0; i < GROUP_ORDER.length; i++) {
      if (lower.includes(GROUP_ORDER[i])) return i;
    }
    return 99;
  };
  return [...kpiGroups.value].sort((a, b) => rank(a.name) - rank(b.name));
});

const distributionSum = computed(() =>
  distributionRows.value.reduce((s, r) => s + (Number(r.points) || 0), 0)
);

function goBack() {
  if (route.query.from === 'department') {
    router.push({ path: '/manager/department', query: { tab: 'compare' } });
  } else {
    router.push('/employee/projects');
  }
}

function getInitials(name: string) {
  if (!name) return '?';
  const parts = name.trim().split(/\s+/);
  return (parts[0]?.[0] || '') + (parts[1]?.[0] || '');
}

function formatBudget(budget: number) {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency', currency: 'RUB', maximumFractionDigits: 0,
  }).format(budget);
}

function formatDate(s: string) {
  if (!s) return '';
  return new Date(s).toLocaleDateString('ru-RU');
}

function getStatusType(p: Project) {
  if (p.completed_at) return 'info';
  if (p.end_date && new Date(p.end_date) < new Date()) return 'info';
  return 'success';
}

function getStatusLabel(p: Project) {
  if (p.completed_at) return `Завершён ${formatDate(p.completed_at)}`;
  if (p.end_date && new Date(p.end_date) < new Date()) return 'Завершён по сроку';
  return 'Активный';
}

function getPriorityType(p: string) {
  return p === 'high' ? 'danger' : p === 'medium' ? 'warning' : 'info';
}

function getPriorityLabel(p: string) {
  return { low: 'Низкий', medium: 'Средний', high: 'Высокий' }[p] || p;
}

function getStatusTagType(s: string) {
  return { assigned: 'warning', in_progress: 'primary', completed: 'success', overdue: 'danger' }[s] as any || 'info';
}

function getStatusLabel2(s: string) {
  return { assigned: 'Назначена', in_progress: 'В работе', completed: 'Выполнена', overdue: 'Просрочена' }[s] || s;
}

function toggleExpand(id: number) {
  expandedId.value = expandedId.value === id ? null : id;
}

async function fetchProject() {
  loading.value = true;
  try {
    const { data } = await projectsApi.getProject(projectId.value);
    project.value = data;
  } catch {
    ElMessage.error("Не удалось загрузить проект");
    router.push('/employee/projects');
  } finally {
    loading.value = false;
  }
}

async function fetchTasks() {
  try {
    const { data } = await projectsApi.getProjectTasks(projectId.value);
    tasks.value = data;
  } catch {
    ElMessage.error("Не удалось загрузить задачи");
  }
}

async function fetchKpiGroups() {
  try {
    const { data } = await kpiApi.getGroups();
    kpiGroups.value = data;
  } catch (_) {}
}

async function fetchEmployees() {
  try {
    const { data } = await employeesApi.getAll();
    allEmployees.value = data;
  } catch (_) {}
}

function openEditDialog() {
  if (!project.value) return;
  Object.assign(editForm, {
    name: project.value.name,
    description: project.value.description || '',
    budget: project.value.budget,
    start_date: project.value.start_date,
    end_date: project.value.end_date || '',
  });
  showEditDialog.value = true;
}

async function submitEdit() {
  if (!editForm.name || !editForm.start_date) {
    ElMessage.warning("Заполните название и дату начала");
    return;
  }
  saving.value = true;
  try {
    await projectsApi.updateProject(projectId.value, {
      name: editForm.name,
      description: editForm.description || null,
      budget: editForm.budget,
      start_date: editForm.start_date,
      end_date: editForm.end_date || null,
    } as any);
    ElMessage.success("Проект обновлён");
    showEditDialog.value = false;
    fetchProject();
  } catch (e: any) {
    ElMessage.error(e.response?.data ? JSON.stringify(e.response.data) : "Ошибка");
  } finally {
    saving.value = false;
  }
}

async function handleDelete() {
  try {
    await ElMessageBox.confirm(
      'Удалить проект? Все задачи будут удалены.',
      'Подтверждение',
      { type: 'warning', confirmButtonText: 'Удалить', cancelButtonText: 'Отмена' }
    );
  } catch {
    return;
  }
  try {
    await projectsApi.deleteProject(projectId.value);
    ElMessage.success("Проект удалён");
    router.push('/employee/projects');
  } catch {
    ElMessage.error("Ошибка удаления");
  }
}

function openAddMemberDialog() {
  selectedEmployeeId.value = null;
  showAddMemberDialog.value = true;
}

async function submitAddMember() {
  if (!selectedEmployeeId.value) {
    ElMessage.warning("Выберите сотрудника");
    return;
  }
  saving.value = true;
  try {
    await projectsApi.addMember(projectId.value, selectedEmployeeId.value);
    ElMessage.success("Участник добавлен");
    showAddMemberDialog.value = false;
    fetchProject();
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || "Ошибка");
  } finally {
    saving.value = false;
  }
}

async function handleRemoveMember(employeeId: number) {
  try {
    await ElMessageBox.confirm('Удалить участника из проекта?', 'Подтверждение', {
      type: 'warning', confirmButtonText: 'Удалить', cancelButtonText: 'Отмена',
    });
  } catch { return; }
  try {
    await projectsApi.removeMember(projectId.value, employeeId);
    ElMessage.success("Участник удалён");
    fetchProject();
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || "Ошибка");
  }
}

function openCreateTaskDialog() {
  Object.assign(taskForm, {
    title: '', description: '',
    priority: 'medium', deadline: '',
    assigned_to: null,
  });
  pendingTaskFiles.value = [];
  showTaskDialog.value = true;
}

async function submitTask() {
  if (!taskForm.title || !taskForm.deadline) {
    ElMessage.warning("Заполните название и дедлайн");
    return;
  }
  saving.value = true;
  try {
    const { data: created } = await tasksApi.createTask({
      title: taskForm.title,
      description: taskForm.description || null,
      priority: taskForm.priority,
      deadline: taskForm.deadline,
      project: projectId.value,
      assigned_to: taskForm.assigned_to,
      status: 'assigned',
    } as any);

    if (created?.id && pendingTaskFiles.value.length) {
      for (const f of pendingTaskFiles.value) {
        try {
          await attachmentsApi.upload(f, { task: created.id });
        } catch {
          ElMessage.warning(`Не удалось загрузить ${f.name}`);
        }
      }
    }

    ElMessage.success("Задача создана");
    pendingTaskFiles.value = [];
    showTaskDialog.value = false;
    fetchTasks();
  } catch (e: any) {
    ElMessage.error(e.response?.data ? JSON.stringify(e.response.data) : "Ошибка");
  } finally {
    saving.value = false;
  }
}

function openCompleteDialog() {
  completeForm.kpi_group = kpiGroups.value[0]?.id || null;
  completeForm.work_type_key = '';
  completeForm.total_points = 10;
  distributionRows.value = (project.value?.members || []).map(m => {
    const total = tasks.value.filter(t => t.assigned_to === m.employee).length;
    const completed = tasks.value.filter(
      t => t.assigned_to === m.employee && t.status === 'completed'
    ).length;
    return {
      employee: m.employee,
      name: m.employee_name,
      completed,
      total,
      points: 0,
    };
  });
  recomputeDistribution();
  showCompleteDialog.value = true;
}

function onCompleteCategoryChange() {
  completeForm.work_type_key = '';
}

function recomputeDistribution() {
  const rows = distributionRows.value;
  const totalCompleted = rows.reduce((s, r) => s + r.completed, 0);
  const total = Number(completeForm.total_points) || 0;
  if (totalCompleted > 0) {
    rows.forEach(r => {
      r.points = Math.round((total * r.completed / totalCompleted) * 100) / 100;
    });
  } else {
    // если никто не выполнил ни одной задачи — делим поровну
    const n = rows.length || 1;
    const share = Math.round((total / n) * 100) / 100;
    rows.forEach(r => { r.points = share; });
  }
}

async function submitComplete() {
  if (!completeForm.kpi_group || !completeForm.work_type_key) {
    ElMessage.warning("Укажите категорию и тип работы");
    return;
  }
  const distribution: Record<number, number> = {};
  distributionRows.value.forEach(r => {
    if (r.points > 0) distribution[r.employee] = Number(r.points);
  });
  if (Object.keys(distribution).length === 0) {
    ElMessage.warning("Укажите баллы хотя бы одному участнику");
    return;
  }
  saving.value = true;
  try {
    const { data } = await projectsApi.completeProject(projectId.value, {
      kpi_group: completeForm.kpi_group,
      work_type_key: completeForm.work_type_key,
      total_points: Number(completeForm.total_points),
      distribution,
    });
    ElMessage.success(`Проект завершён — создано работ: ${data.works_created}`);
    showCompleteDialog.value = false;
    fetchProject();
    fetchTasks();
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || "Ошибка завершения");
  } finally {
    saving.value = false;
  }
}

async function handleTakeTask(task: Task) {
  try {
    await tasksApi.takeTask(task.id);
    ElMessage.success("Задача принята");
    fetchTasks();
  } catch {
    ElMessage.error("Ошибка");
  }
}

async function handleStart(task: Task) {
  try {
    await tasksApi.startTask(task.id);
    fetchTasks();
  } catch {
    ElMessage.error("Ошибка");
  }
}

async function handleComplete(task: Task) {
  try {
    const { data } = await tasksApi.completeTask(task.id);
    const created = (data as any)?.created_work;
    if (created?.title) {
      ElMessage.success(`Задача выполнена — создана работа «${created.title}»`);
    } else {
      ElMessage.success("Задача выполнена");
    }
    fetchTasks();
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || "Ошибка");
  }
}

async function handleDeleteTask(task: Task) {
  try {
    await ElMessageBox.confirm('Удалить задачу?', 'Подтверждение', {
      type: 'warning', confirmButtonText: 'Удалить', cancelButtonText: 'Отмена',
    });
  } catch { return; }
  try {
    await tasksApi.deleteTask(task.id);
    ElMessage.success("Удалено");
    fetchTasks();
  } catch {
    ElMessage.error("Ошибка");
  }
}

onMounted(() => {
  if (!auth.employeeId) auth.fetchMe?.();
  fetchProject();
  fetchTasks();
  fetchKpiGroups();
  fetchEmployees();
});
</script>

<style scoped>
.project-detail {
  display: flex;
  flex-direction: column;
  gap: 24px;
  min-height: 400px;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.topbar-actions {
  display: flex;
  gap: 8px;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Header card */
.project-header-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.project-header-top {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.project-icon-lg {
  width: 56px;
  height: 56px;
  background: var(--primary-soft);
  color: var(--primary);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.project-header-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.project-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.project-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0;
  letter-spacing: -0.5px;
}

.project-description {
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
}

.project-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--border);
}

.stat {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  color: var(--text-secondary);
}

.stat-label {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 2px;
}

.stat-value {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

/* Grid layout */
.grid-layout {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 24px;
}

@media (max-width: 900px) {
  .grid-layout {
    grid-template-columns: 1fr;
  }
}

.panel {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.empty {
  color: var(--text-muted);
  font-size: 13px;
  text-align: center;
  padding: 30px 0;
}

/* Members */
.members-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.member-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border-radius: var(--radius);
  transition: background var(--transition);
}

.member-item:hover {
  background: var(--bg);
}

.member-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--primary-soft);
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  text-transform: uppercase;
}

.member-info {
  flex: 1;
  min-width: 0;
}

.member-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.member-role {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
}

/* Tasks */
.tasks-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.task-card {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  transition: all var(--transition);
}

.task-card.expanded {
  border-color: var(--primary);
  box-shadow: var(--shadow-sm);
}

.task-card-head {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  cursor: pointer;
}

.task-card-head:hover {
  background: var(--bg-card);
}

.task-head-left {
  display: flex;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-top: 6px;
  flex-shrink: 0;
}

.status-dot.assigned { background: var(--warning); }
.status-dot.in_progress { background: var(--primary); }
.status-dot.completed { background: var(--success); }
.status-dot.overdue { background: var(--danger); }

.task-head-main {
  flex: 1;
  min-width: 0;
}

.task-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.task-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.task-meta-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.task-meta {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-muted);
}

.expand-chevron {
  color: var(--text-muted);
  transition: transform var(--transition);
}

.expand-chevron.rot {
  transform: rotate(180deg);
}

.task-card-body {
  padding: 16px;
  border-top: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.task-description {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
  white-space: pre-wrap;
}

.task-details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
}

.detail-label {
  font-size: 11px;
  color: var(--text-muted);
  margin-bottom: 2px;
}

.detail-value {
  font-size: 13px;
  color: var(--text-primary);
  font-weight: 500;
}

.task-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

/* Attachments */
.task-attachments {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background: var(--bg-card, #fff);
  border: 1px solid var(--border);
  border-radius: var(--radius);
}

.task-attachments-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-attachments-title {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.attachments-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 6px;
}

.attachment-name {
  flex: 1;
  color: var(--primary);
  text-decoration: none;
  word-break: break-all;
  font-size: 13px;
}

.attachment-name:hover {
  text-decoration: underline;
}

.attachment-size {
  font-size: 12px;
  color: var(--text-muted);
}

.pending-files {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 8px;
  width: 100%;
}

.pending-file {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: var(--bg);
  border: 1px dashed var(--border);
  border-radius: 6px;
  font-size: 13px;
}

.pending-file > span:first-of-type {
  flex: 1;
}

.distribution-hint {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.distribution-sum {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  font-size: 13px;
  color: var(--text-secondary);
}

.project-tabs :deep(.el-tabs__header) {
  margin-bottom: 16px;
}

.tab-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 22px;
  padding: 0 6px;
  height: 18px;
  background: var(--bg);
  color: var(--text-secondary);
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  margin-left: 6px;
}

.filters-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  padding: 12px 14px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  margin-bottom: 14px;
}

.members-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
}

.member-card {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.member-card-head {
  display: flex;
  align-items: center;
  gap: 10px;
}

.member-stats {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.stat-pill {
  display: flex;
  align-items: baseline;
  gap: 4px;
  padding: 3px 9px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  font-size: 11px;
}

.stat-pill .pill-num {
  font-weight: 700;
  color: var(--text-primary);
  font-size: 12px;
}

.stat-pill .pill-lbl {
  color: var(--text-muted);
}

.stat-pill.stat-done {
  border-color: var(--success);
  background: #ecfdf5;
}
.stat-pill.stat-done .pill-num { color: var(--success); }

.stat-pill.stat-progress {
  border-color: var(--primary);
  background: var(--primary-soft, #eef2ff);
}
.stat-pill.stat-progress .pill-num { color: var(--primary); }

.stat-pill.stat-bad {
  border-color: var(--danger);
  background: #fef2f2;
}
.stat-pill.stat-bad .pill-num { color: var(--danger); }

.member-bar {
  height: 4px;
  background: var(--bg-card);
  border-radius: 2px;
  overflow: hidden;
}

.member-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary), var(--success));
  border-radius: 2px;
  transition: width 0.4s ease;
}

.is-done {
  opacity: 0.6;
}

.is-done .task-title {
  text-decoration: line-through;
}

.task-meta-free {
  color: var(--warning) !important;
  font-weight: 500;
}
</style>
