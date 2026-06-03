<template>
  <div class="tasks-page">
    <div class="page-top">
      <div>
        <h2 class="page-title">Задачи</h2>
        <p class="page-subtitle">Отслеживание и управление задачами</p>
      </div>
      <el-button v-if="auth.isManager" type="primary" @click="openCreateDialog">
        <el-icon><Plus /></el-icon>
        Создать задачу
      </el-button>
    </div>

    <!-- Filters bar -->
    <div class="filters-bar">
      <el-input
        v-model="filter.search"
        placeholder="Поиск по названию"
        clearable
        style="width: 260px"
        :prefix-icon="Search"
      />
      <el-select v-model="filter.status" placeholder="Статус" clearable style="width: 150px">
        <el-option label="Назначена" value="assigned" />
        <el-option label="В работе" value="in_progress" />
        <el-option label="Выполнена" value="completed" />
        <el-option label="Просрочена" value="overdue" />
      </el-select>
      <el-date-picker
        v-model="filter.deadline"
        type="daterange"
        range-separator="—"
        start-placeholder="Дедлайн от"
        end-placeholder="до"
        value-format="YYYY-MM-DD"
        style="width: 280px"
      />
      <el-select
        v-if="activeTab === 'project'"
        v-model="filter.projectId"
        placeholder="Проект"
        clearable
        filterable
        style="width: 200px"
      >
        <el-option
          v-for="p in projectsList"
          :key="p.id"
          :label="p.name"
          :value="p.id"
        />
      </el-select>
      <el-button v-if="hasActiveFilters" size="small" @click="resetFilters">Сбросить</el-button>
    </div>

    <!-- Tabs -->
    <el-tabs v-model="activeTab" class="task-tabs">
      <!-- MINE -->
      <el-tab-pane name="mine">
        <template #label>
          <span class="tab-label">
            Мои задачи
            <span class="tab-badge">{{ mineTasks.length }}</span>
          </span>
        </template>

        <div class="list-wrap" v-loading="loading">
          <div v-if="mineTasks.length === 0" class="empty-state">
            Свободных задач, назначенных на вас, нет
          </div>
          <div
            v-for="task in mineTasks"
            :key="task.id"
            class="list-card"
            :class="{ 'is-done': task.status === 'completed' }"
            @click="openDetail(task)"
          >
            <div class="list-card-left">
              <div class="status-dot" :class="task.status"></div>
              <div>
                <div class="list-card-title">{{ task.title }}</div>
                <div class="list-card-meta">
                  <span class="task-meta">
                    <el-icon :size="12"><Calendar /></el-icon>
                    {{ task.deadline }}
                  </span>
                  <span class="task-meta">
                    <el-icon :size="12"><Medal /></el-icon>
                    {{ task.points }} б.
                  </span>
                  <span v-if="task.kpi_group" class="task-meta">
                    <el-icon :size="12"><DataLine /></el-icon>
                    {{ getCategoryName(task.kpi_group) }}
                  </span>
                </div>
              </div>
            </div>
            <div class="list-card-right">
              <el-tag size="small" :type="getStatusType(task.status)" effect="light">
                {{ getStatusLabel(task.status) }}
              </el-tag>
              <el-tag size="small" :type="getPriorityType(task.priority)" effect="plain">
                {{ getPriorityLabel(task.priority) }}
              </el-tag>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- PROJECT TASKS -->
      <el-tab-pane name="project">
        <template #label>
          <span class="tab-label">
            Проектные
            <span class="tab-badge">{{ projectTasks.length }}</span>
          </span>
        </template>

        <div class="list-wrap" v-loading="loading">
          <div v-if="projectTasks.length === 0" class="empty-state">Задач нет</div>
          <div
            v-for="task in projectTasks"
            :key="task.id"
            class="list-card"
            :class="{ 'is-done': task.status === 'completed' }"
            @click="openDetail(task)"
          >
            <div class="list-card-left">
              <div class="status-dot" :class="task.status"></div>
              <div>
                <div class="list-card-title">{{ task.title }}</div>
                <div class="list-card-meta">
                  <span class="task-meta">
                    <el-icon :size="12"><Folder /></el-icon>
                    {{ getProjectName(task.project) }}
                  </span>
                  <span class="task-meta">
                    <el-icon :size="12"><Calendar /></el-icon>
                    {{ task.deadline }}
                  </span>
                  <span v-if="task.assigned_to_name" class="task-meta">
                    <el-icon :size="12"><User /></el-icon>
                    {{ task.assigned_to_name }}
                  </span>
                  <span v-else class="task-meta task-free">
                    Свободна
                  </span>
                </div>
              </div>
            </div>
            <div class="list-card-right" @click.stop>
              <el-button
                v-if="task.assigned_to === null && canTakeProjectTask(task)"
                size="small"
                type="primary"
                @click="handleTake(task)"
              >
                Взять
              </el-button>
              <el-button
                v-if="task.status === 'assigned' && task.assigned_to === auth.employeeId"
                size="small"
                type="primary"
                @click="handleStart(task)"
              >
                Начать
              </el-button>
              <el-tag size="small" :type="getStatusType(task.status)" effect="light">
                {{ getStatusLabel(task.status) }}
              </el-tag>
              <el-tag size="small" :type="getPriorityType(task.priority)" effect="plain">
                {{ getPriorityLabel(task.priority) }}
              </el-tag>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- POOL (free tasks) -->
      <el-tab-pane name="pool">
        <template #label>
          <span class="tab-label">
            Свободные
            <span class="tab-badge">{{ poolTasks.length }}</span>
          </span>
        </template>

        <div class="pool-grid" v-loading="loading">
          <div v-if="poolTasks.length === 0" class="empty-state">Свободных задач нет</div>
          <div
            v-for="task in poolTasks"
            :key="task.id"
            class="pool-card"
            @click="openDetail(task)"
          >
            <div class="pool-card-top">
              <h4 class="task-title">{{ task.title }}</h4>
              <el-tag size="small" :type="getPriorityType(task.priority)" effect="plain">
                {{ getPriorityLabel(task.priority) }}
              </el-tag>
            </div>
            <div class="task-meta-row">
              <span class="task-meta">
                <el-icon :size="12"><Calendar /></el-icon>
                {{ task.deadline }}
              </span>
              <span class="task-meta">
                <el-icon :size="12"><Medal /></el-icon>
                {{ task.points }} б.
              </span>
            </div>
            <el-button type="primary" size="small" @click.stop="handleTake(task)">
              Взять задачу
            </el-button>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- Create free task dialog -->
    <el-dialog v-model="showCreateDialog" title="Создать задачу" width="560px" destroy-on-close>
      <el-form :model="form" label-position="top">
        <el-form-item label="Название" required>
          <el-input v-model="form.title" placeholder="Что нужно сделать" />
        </el-form-item>
        <el-form-item label="Описание">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>

        <el-form-item label="Категория" required>
          <el-radio-group v-model="form.category" @change="form.work_type_key = ''">
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
            v-model="form.work_type_key"
            style="width: 100%"
            placeholder="Выберите тип"
            :disabled="!form.category"
          >
            <el-option
              v-for="ind in currentIndicators"
              :key="ind.id"
              :label="ind.name"
              :value="ind.work_type_key"
            />
          </el-select>
        </el-form-item>

        <div class="form-row">
          <el-form-item label="Баллы" required>
            <el-input-number v-model="form.points" :min="0.5" :step="0.5" style="width: 100%" />
          </el-form-item>
          <el-form-item label="Приоритет">
            <el-select v-model="form.priority" style="width: 100%">
              <el-option label="Низкий" value="low" />
              <el-option label="Средний" value="medium" />
              <el-option label="Высокий" value="high" />
            </el-select>
          </el-form-item>
        </div>

        <el-form-item label="Дедлайн" required>
          <el-date-picker
            v-model="form.deadline"
            type="date"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="Назначить (пусто — в общий пул)">
          <el-select
            v-model="form.assigned_to"
            clearable
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="e in availableEmployees"
              :key="e.id"
              :label="e.full_name"
              :value="e.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">Отмена</el-button>
        <el-button type="primary" @click="submitCreate" :loading="saving">Создать</el-button>
      </template>
    </el-dialog>

    <!-- Task detail dialog -->
    <el-dialog
      v-model="showDetailDialog"
      :title="detailTask?.title || 'Задача'"
      width="640px"
      class="task-detail-dialog"
      append-to-body
    >
      <div v-if="detailTask" class="detail-container">
        <div v-if="!editing">
          <div v-if="detailTask.description" class="detail-description">
            {{ detailTask.description }}
          </div>

          <div class="detail-grid">
            <div class="detail-item">
              <div class="detail-label">Статус</div>
              <el-tag size="small" :type="getStatusType(detailTask.status)" effect="light">
                {{ getStatusLabel(detailTask.status) }}
              </el-tag>
            </div>
            <div class="detail-item">
              <div class="detail-label">Приоритет</div>
              <el-tag size="small" :type="getPriorityType(detailTask.priority)" effect="plain">
                {{ getPriorityLabel(detailTask.priority) }}
              </el-tag>
            </div>
            <div class="detail-item">
              <div class="detail-label">Дедлайн</div>
              <div class="detail-value">{{ detailTask.deadline }}</div>
            </div>
            <div class="detail-item">
              <div class="detail-label">Создатель</div>
              <div class="detail-value">{{ detailTask.created_by_name }}</div>
            </div>
            <div class="detail-item">
              <div class="detail-label">Исполнитель</div>
              <div class="detail-value">{{ detailTask.assigned_to_name || 'Не назначен' }}</div>
            </div>
            <div v-if="!detailTask.project" class="detail-item">
              <div class="detail-label">Баллы</div>
              <div class="detail-value">{{ detailTask.points }}</div>
            </div>
            <div v-if="!detailTask.project && detailTask.kpi_group" class="detail-item">
              <div class="detail-label">Категория</div>
              <div class="detail-value">{{ getCategoryName(detailTask.kpi_group) }}</div>
            </div>
            <div v-if="!detailTask.project && detailTask.work_type_key" class="detail-item">
              <div class="detail-label">Тип работы</div>
              <div class="detail-value">
                {{ getIndicatorName(detailTask.kpi_group, detailTask.work_type_key) }}
              </div>
            </div>
            <div v-if="detailTask.project" class="detail-item">
              <div class="detail-label">Проект</div>
              <div class="detail-value">{{ getProjectName(detailTask.project) }}</div>
            </div>
          </div>

          <div class="detail-section">
            <div class="detail-section-head">
              <span class="detail-section-title">
                <el-icon><Paperclip /></el-icon>
                Файлы ({{ detailTask.attachments?.length || 0 }})
              </span>
              <el-upload
                v-if="canManageFiles"
                :show-file-list="false"
                :before-upload="(file: File) => { uploadFile(file); return false }"
                multiple
              >
                <el-button size="small">
                  <el-icon><Paperclip /></el-icon>
                  Прикрепить
                </el-button>
              </el-upload>
            </div>
            <div v-if="detailTask.attachments?.length" class="attachments-list">
              <div
                v-for="att in detailTask.attachments"
                :key="att.id"
                class="attachment-item"
              >
                <el-icon><Document /></el-icon>
                <a :href="att.url || undefined" target="_blank" class="attachment-name">
                  {{ att.original_name }}
                </a>
                <span class="attachment-size">{{ formatSize(att.size) }}</span>
                <el-button
                  v-if="canManageFiles"
                  size="small"
                  circle
                  type="danger"
                  @click="removeAttachment(att.id)"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
            <div v-else class="no-attachments">Файлов нет</div>
          </div>
        </div>

        <el-form v-else :model="editForm" label-position="top">
          <el-form-item label="Название" required>
            <el-input v-model="editForm.title" />
          </el-form-item>
          <el-form-item label="Описание">
            <el-input v-model="editForm.description" type="textarea" :rows="3" />
          </el-form-item>
          <div class="form-row">
            <el-form-item label="Приоритет">
              <el-select v-model="editForm.priority" style="width: 100%">
                <el-option label="Низкий" value="low" />
                <el-option label="Средний" value="medium" />
                <el-option label="Высокий" value="high" />
              </el-select>
            </el-form-item>
            <el-form-item label="Дедлайн" required>
              <el-date-picker
                v-model="editForm.deadline"
                type="date"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </div>
          <el-form-item v-if="detailTask && !detailTask.project" label="Баллы">
            <el-input-number
              v-model="editForm.points"
              :min="0"
              :step="0.5"
              style="width: 100%"
            />
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <div v-if="!editing" class="detail-footer">
          <el-button @click="showDetailDialog = false">Закрыть</el-button>
          <el-button
            v-if="detailTask && detailTask.status === 'assigned' && detailTask.assigned_to === auth.employeeId"
            type="primary"
            @click="handleStartFromDetail"
          >
            Начать
          </el-button>
          <el-button
            v-if="detailTask && detailTask.status === 'in_progress' && detailTask.assigned_to === auth.employeeId"
            type="success"
            @click="openCompletionFlow"
          >
            Завершить
          </el-button>
          <el-button
            v-if="detailTask && detailTask.assigned_to === null && canTakeAny(detailTask)"
            type="primary"
            @click="handleTakeFromDetail"
          >
            Взять задачу
          </el-button>
          <el-button v-if="canEditTask" @click="startEdit">
            <el-icon><Edit /></el-icon>
            Редактировать
          </el-button>
          <el-button v-if="canDeleteTask" type="danger" plain @click="handleDelete">
            <el-icon><Delete /></el-icon>
            Удалить
          </el-button>
        </div>
        <div v-else>
          <el-button @click="editing = false">Отмена</el-button>
          <el-button type="primary" :loading="saving" @click="submitEdit">
            Сохранить
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- Completion dialog (Add Work) -->
    <el-dialog
      v-model="showCompletionDialog"
      title="Завершение задачи → Добавление работы"
      width="620px"
      destroy-on-close
    >
      <el-alert
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 16px"
      >
        Задача будет завершена и по её данным создана работа на верификацию.
        Баллы проставит руководитель.
      </el-alert>

      <el-form :model="compForm" label-position="top" v-if="detailTask">
        <el-form-item label="Категория" required>
          <el-radio-group v-model="compForm.category" disabled>
            <el-radio-button value="scientific">Научная</el-radio-button>
            <el-radio-button value="technical">Техническая</el-radio-button>
            <el-radio-button value="organizational">Организационная</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Название" required>
          <el-input v-model="compForm.title" />
        </el-form-item>
        <el-form-item label="Тип работы" required>
          <el-input v-model="compForm.work_type" disabled />
        </el-form-item>

        <!-- Scientific -->
        <template v-if="compForm.category === 'scientific'">
          <el-form-item label="Форма работы">
            <el-select v-model="compForm.sci_form" style="width: 100%">
              <el-option label="Публикация" value="publication" />
              <el-option label="Диссертация" value="dissertation" />
              <el-option label="Участие в проекте" value="project" />
              <el-option label="ПО" value="software" />
            </el-select>
          </el-form-item>

          <template v-if="compForm.sci_form === 'publication'">
            <el-form-item label="Тип публикации">
              <el-radio-group v-model="compForm.pub_type">
                <el-radio value="article">Статья</el-radio>
                <el-radio value="monograph">Монография</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="Год">
              <el-input-number v-model="compForm.pub_year" :min="2000" :max="2030" />
            </el-form-item>
            <template v-if="compForm.pub_type === 'article'">
              <el-form-item label="Журнал">
                <el-input v-model="compForm.journal" />
              </el-form-item>
              <div class="form-row">
                <el-form-item label="DOI">
                  <el-input v-model="compForm.doi" />
                </el-form-item>
                <el-form-item label="Квартиль">
                  <el-select v-model="compForm.quartile" clearable>
                    <el-option label="Q1" :value="1" />
                    <el-option label="Q2" :value="2" />
                    <el-option label="Q3" :value="3" />
                    <el-option label="Q4" :value="4" />
                  </el-select>
                </el-form-item>
              </div>
              <el-form-item>
                <el-checkbox v-model="compForm.is_scopus">Индексирована в Scopus</el-checkbox>
              </el-form-item>
            </template>
            <template v-if="compForm.pub_type === 'monograph'">
              <el-form-item label="Издательство">
                <el-input v-model="compForm.publisher" />
              </el-form-item>
              <el-form-item label="ISBN">
                <el-input v-model="compForm.isbn" />
              </el-form-item>
            </template>
          </template>

          <template v-if="compForm.sci_form === 'dissertation'">
            <el-form-item label="Этап">
              <el-input v-model="compForm.stage" />
            </el-form-item>
            <el-form-item label="Дата защиты">
              <el-date-picker v-model="compForm.defense_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </template>

          <template v-if="compForm.sci_form === 'project'">
            <el-form-item label="Роль">
              <el-input v-model="compForm.project_role" />
            </el-form-item>
            <div class="form-row">
              <el-form-item label="Дата начала">
                <el-date-picker v-model="compForm.start_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
              </el-form-item>
              <el-form-item label="Дата окончания">
                <el-date-picker v-model="compForm.end_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
              </el-form-item>
            </div>
          </template>

          <template v-if="compForm.sci_form === 'software'">
            <el-form-item label="Версия">
              <el-input v-model="compForm.version" />
            </el-form-item>
            <el-form-item>
              <el-checkbox v-model="compForm.is_commercial">Коммерческое</el-checkbox>
            </el-form-item>
          </template>
        </template>

        <!-- Organizational -->
        <template v-if="compForm.category === 'organizational'">
          <div class="form-row">
            <el-form-item label="Дата мероприятия" required>
              <el-date-picker v-model="compForm.event_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Кол-во участников">
              <el-input-number v-model="compForm.participants_count" :min="0" />
            </el-form-item>
          </div>
        </template>

        <!-- Technical -->
        <template v-if="compForm.category === 'technical'">
          <div class="form-row">
            <el-form-item label="Дата" required>
              <el-date-picker v-model="compForm.work_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Номер регистрации">
              <el-input v-model="compForm.registration_number" />
            </el-form-item>
          </div>
          <el-form-item label="Метрика">
            <el-input v-model="compForm.metric" />
          </el-form-item>
        </template>

        <el-form-item label="Дополнительные файлы">
          <el-upload
            :show-file-list="false"
            :before-upload="(file: File) => { compPendingFiles.push(file); return false }"
            multiple
          >
            <el-button>
              <el-icon><Paperclip /></el-icon>
              Добавить файлы
            </el-button>
          </el-upload>
          <div v-if="taskAttachmentsCount" class="hint-text" style="margin-top: 8px">
            К задаче уже прикреплено {{ taskAttachmentsCount }} файлов — они перенесутся автоматически.
          </div>
          <div v-if="compPendingFiles.length" class="pending-files">
            <div v-for="(f, i) in compPendingFiles" :key="i" class="pending-file">
              <el-icon><Document /></el-icon>
              <span>{{ f.name }}</span>
              <el-button size="small" circle type="danger" @click="compPendingFiles.splice(i, 1)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCompletionDialog = false">Отмена</el-button>
        <el-button type="success" :loading="saving" @click="submitCompletion">
          Завершить и отправить на верификацию
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from "vue";
import {
  Calendar, Plus, Paperclip, Document, Delete, Edit, Medal,
  Search, Folder, User, DataLine,
} from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { tasksApi } from "@/api/tasks";
import { kpiApi, employeesApi, type KPIGroupData } from "@/api/kpi";
import { projectsApi } from "@/api/projects";
import { worksApi } from "@/api/works";
import { attachmentsApi, type Attachment } from "@/api/attachments";
import { useAuthStore } from "@/store/auth";
import type { Task, Project } from "@/types/work";
import type { Employee } from "@/types/user";

const auth = useAuthStore();
const loading = ref(false);
const saving = ref(false);
const tasks = ref<Task[]>([]);
const kpiGroups = ref<KPIGroupData[]>([]);
const employees = ref<Employee[]>([]);
const projectsList = ref<Project[]>([]);
const showCreateDialog = ref(false);
const activeTab = ref<'mine' | 'project' | 'pool'>('mine');

const filter = reactive({
  search: '',
  status: '' as '' | 'assigned' | 'in_progress' | 'completed' | 'overdue',
  deadline: null as [string, string] | null,
  projectId: null as number | null,
});

const hasActiveFilters = computed(() =>
  !!(filter.search || filter.status || filter.deadline || filter.projectId)
);

function resetFilters() {
  filter.search = '';
  filter.status = '';
  filter.deadline = null;
  filter.projectId = null;
}

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

function getProjectName(id: number | null) {
  if (!id) return '—';
  return projectsList.value.find(p => p.id === id)?.name || `Проект #${id}`;
}

function canTakeProjectTask(task: Task): boolean {
  if (!task.project || !auth.employeeId) return false;
  // Я участник проекта → могу взять (создатель тоже участник, его добавили автоматически)
  return true;  // дополнительная проверка делается на бэке
}

function canTakeAny(task: Task): boolean {
  if (task.assigned_to !== null) return false;
  if (task.project) return canTakeProjectTask(task);
  return true; // свободные задачи в пуле — всегда (бэк проверит департамент)
}
function getCategoryName(groupId: number | null) {
  if (!groupId) return '—';
  return kpiGroups.value.find(g => g.id === groupId)?.name || '—';
}
function getIndicatorName(groupId: number | null, key: string | null) {
  if (!groupId || !key) return '—';
  return kpiGroups.value.find(g => g.id === groupId)?.indicators
    .find(i => i.work_type_key === key)?.name || key;
}

function applyFilters(list: Task[]): Task[] {
  return list.filter(t => {
    if (filter.search && !t.title.toLowerCase().includes(filter.search.toLowerCase())) return false;
    if (filter.status && t.status !== filter.status) return false;
    if (filter.deadline) {
      const [from, to] = filter.deadline;
      if (from && t.deadline < from) return false;
      if (to && t.deadline > to) return false;
    }
    if (filter.projectId && t.project !== filter.projectId) return false;
    return true;
  });
}

// Сортировка: выполненные вниз, выше — высокий приоритет, дальше — по дедлайну
const PRIORITY_RANK: Record<string, number> = { high: 0, medium: 1, low: 2 };
function sortTasks(list: Task[]): Task[] {
  return [...list].sort((a, b) => {
    const ad = a.status === 'completed' ? 1 : 0;
    const bd = b.status === 'completed' ? 1 : 0;
    if (ad !== bd) return ad - bd;
    const ap = PRIORITY_RANK[a.priority] ?? 3;
    const bp = PRIORITY_RANK[b.priority] ?? 3;
    if (ap !== bp) return ap - bp;
    return (a.deadline || '').localeCompare(b.deadline || '');
  });
}

const mineTasks = computed(() =>
  // Только свободные задачи, назначенные на меня (проектные — в отдельной вкладке)
  sortTasks(applyFilters(
    tasks.value.filter(t => t.assigned_to === auth.employeeId && t.project === null)
  ))
);
const projectTasks = computed(() =>
  sortTasks(applyFilters(tasks.value.filter(t => t.project !== null)))
);
const poolTasks = computed(() =>
  sortTasks(applyFilters(tasks.value.filter(t => t.project === null && t.assigned_to === null)))
);

// --- Create free task form ---
const form = reactive({
  title: '',
  description: '',
  category: null as number | null,
  work_type_key: '',
  points: 5,
  priority: 'medium' as 'low' | 'medium' | 'high',
  deadline: '',
  assigned_to: null as number | null,
});

const currentIndicators = computed(() => {
  if (!form.category) return [];
  return kpiGroups.value.find(g => g.id === form.category)?.indicators || [];
});
const availableEmployees = computed(() =>
  employees.value.filter(e => e.id !== auth.employeeId)
);

function openCreateDialog() {
  Object.assign(form, {
    title: '', description: '', category: null, work_type_key: '',
    points: 5, priority: 'medium', deadline: '', assigned_to: null,
  });
  showCreateDialog.value = true;
}

async function submitCreate() {
  if (!form.title || !form.deadline || !form.category || !form.work_type_key || !form.points) {
    ElMessage.warning("Заполните название, категорию, тип, баллы и дедлайн");
    return;
  }
  saving.value = true;
  try {
    await tasksApi.createTask({
      title: form.title,
      description: form.description || null,
      priority: form.priority,
      deadline: form.deadline,
      kpi_group: form.category,
      work_type_key: form.work_type_key,
      points: form.points,
      project: null,
      assigned_to: form.assigned_to,
      status: 'assigned',
    } as any);
    ElMessage.success(form.assigned_to ? "Задача назначена" : "Задача размещена в пуле");
    showCreateDialog.value = false;
    fetchTasks();
  } catch (e: any) {
    ElMessage.error(e.response?.data ? JSON.stringify(e.response.data) : "Ошибка");
  } finally {
    saving.value = false;
  }
}

// --- Detail dialog ---
const showDetailDialog = ref(false);
const detailTask = ref<Task | null>(null);
const editing = ref(false);
const editForm = reactive({
  title: '', description: '',
  priority: 'medium' as 'low' | 'medium' | 'high',
  deadline: '', points: 0,
});

const canEditTask = computed(
  () => !!detailTask.value && detailTask.value.created_by === auth.employeeId
    && detailTask.value.status !== 'completed'
);
const canDeleteTask = computed(
  () => !!detailTask.value && detailTask.value.created_by === auth.employeeId
);
const canManageFiles = computed(
  () => !!detailTask.value
    && (detailTask.value.created_by === auth.employeeId
        || detailTask.value.assigned_to === auth.employeeId)
    && detailTask.value.status !== 'completed'
);

function openDetail(task: Task) {
  detailTask.value = task;
  editing.value = false;
  showDetailDialog.value = true;
}

function startEdit() {
  if (!detailTask.value) return;
  Object.assign(editForm, {
    title: detailTask.value.title,
    description: detailTask.value.description || '',
    priority: detailTask.value.priority,
    deadline: detailTask.value.deadline,
    points: detailTask.value.points,
  });
  editing.value = true;
}

async function submitEdit() {
  if (!detailTask.value) return;
  if (!editForm.title || !editForm.deadline) {
    ElMessage.warning("Заполните название и дедлайн");
    return;
  }
  saving.value = true;
  try {
    const payload: any = {
      title: editForm.title,
      description: editForm.description || null,
      priority: editForm.priority,
      deadline: editForm.deadline,
    };
    if (!detailTask.value.project) payload.points = editForm.points;
    const { data } = await tasksApi.updateTask(detailTask.value.id, payload);
    const idx = tasks.value.findIndex(t => t.id === data.id);
    if (idx !== -1) tasks.value[idx] = data;
    detailTask.value = data;
    editing.value = false;
    ElMessage.success("Сохранено");
  } catch (e: any) {
    ElMessage.error(e.response?.data ? JSON.stringify(e.response.data) : "Ошибка");
  } finally {
    saving.value = false;
  }
}

async function uploadFile(file: File) {
  if (!detailTask.value) return;
  try {
    const { data } = await attachmentsApi.upload(file, { task: detailTask.value.id });
    if (!detailTask.value.attachments) detailTask.value.attachments = [];
    detailTask.value.attachments.push(data as Attachment);
    ElMessage.success('Файл загружен');
  } catch {
    ElMessage.error(`Не удалось загрузить ${file.name}`);
  }
}

async function removeAttachment(attId: number) {
  if (!detailTask.value) return;
  try {
    await ElMessageBox.confirm('Удалить файл?', 'Подтверждение', { type: 'warning' });
  } catch { return; }
  try {
    await attachmentsApi.remove(attId);
    detailTask.value.attachments = (detailTask.value.attachments || []).filter(a => a.id !== attId);
    ElMessage.success('Файл удалён');
  } catch {
    ElMessage.error('Ошибка удаления');
  }
}

async function handleDelete() {
  if (!detailTask.value) return;
  try {
    await ElMessageBox.confirm('Удалить задачу?', 'Подтверждение', {
      type: 'warning', confirmButtonText: 'Удалить', cancelButtonText: 'Отмена',
    });
  } catch { return; }
  try {
    await tasksApi.deleteTask(detailTask.value.id);
    tasks.value = tasks.value.filter(t => t.id !== detailTask.value!.id);
    ElMessage.success('Удалено');
    showDetailDialog.value = false;
  } catch {
    ElMessage.error('Ошибка');
  }
}

async function handleStartFromDetail() {
  if (!detailTask.value) return;
  try {
    const { data } = await tasksApi.startTask(detailTask.value.id);
    const idx = tasks.value.findIndex(t => t.id === data.id);
    if (idx !== -1) tasks.value[idx] = data;
    detailTask.value = data;
  } catch {
    ElMessage.error('Ошибка');
  }
}

async function handleTakeFromDetail() {
  if (!detailTask.value) return;
  await handleTake(detailTask.value);
  const updated = tasks.value.find(t => t.id === detailTask.value!.id);
  if (updated) detailTask.value = updated;
}

async function handleTake(task: Task) {
  try {
    const { data } = await tasksApi.takeTask(task.id);
    const idx = tasks.value.findIndex(t => t.id === task.id);
    if (idx !== -1) tasks.value[idx] = data;
    ElMessage.success('Задача принята');
  } catch {
    ElMessage.error('Ошибка');
  }
}

// --- Completion flow ---
const showCompletionDialog = ref(false);
const compPendingFiles = ref<File[]>([]);

const compForm = reactive({
  category: 'scientific' as 'scientific' | 'organizational' | 'technical',
  title: '',
  work_type: '',
  // scientific
  sci_form: 'publication' as string,
  pub_type: 'article' as string,
  pub_year: new Date().getFullYear(),
  journal: '',
  doi: '',
  quartile: null as number | null,
  is_scopus: false,
  publisher: '',
  isbn: '',
  stage: '',
  defense_date: '',
  project_role: '',
  start_date: '',
  end_date: '',
  version: '',
  is_commercial: false,
  // organizational
  event_date: '' as string,
  participants_count: null as number | null,
  // technical
  work_date: '' as string,
  registration_number: '',
  metric: '',
});

const taskAttachmentsCount = computed(() => detailTask.value?.attachments?.length || 0);

function categoryFromGroup(groupId: number | null): 'scientific' | 'organizational' | 'technical' {
  const g = kpiGroups.value.find(g => g.id === groupId);
  if (!g) return 'scientific';
  const name = g.name.toLowerCase();
  if (name.includes('науч')) return 'scientific';
  if (name.includes('организ')) return 'organizational';
  return 'technical';
}

async function completeProjectTaskDirectly() {
  if (!detailTask.value) return;
  const task = detailTask.value;
  try {
    await tasksApi.completeTask(task.id);
    ElMessage.success('Задача проекта завершена');
    showDetailDialog.value = false;
    fetchTasks();
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || 'Ошибка');
  }
}

function openCompletionFlow() {
  if (!detailTask.value) return;
  const task = detailTask.value;
  // Проектная задача — просто меняем статус, без диалога создания работы
  if (task.project !== null) {
    completeProjectTaskDirectly();
    return;
  }
  const today = new Date().toISOString().slice(0, 10);
  Object.assign(compForm, {
    category: categoryFromGroup(task.kpi_group),
    title: task.title,
    work_type: task.work_type_key || '',
    sci_form: 'publication',
    pub_type: 'article',
    pub_year: new Date().getFullYear(),
    journal: '', doi: '', quartile: null, is_scopus: false,
    publisher: '', isbn: '',
    stage: '', defense_date: '',
    project_role: '', start_date: '', end_date: '',
    version: '', is_commercial: false,
    event_date: today, participants_count: null,
    work_date: today, registration_number: '', metric: '',
  });
  compPendingFiles.value = [];
  showCompletionDialog.value = true;
}

async function submitCompletion() {
  if (!detailTask.value) return;
  const task = detailTask.value;
  if (!compForm.title) {
    ElMessage.warning('Заполните название');
    return;
  }
  saving.value = true;
  try {
    let createdWorkId: number | null = null;
    let createdKind: 'scientific_work' | 'organizational_work' | 'technical_work' = 'scientific_work';

    if (compForm.category === 'scientific') {
      const payload: any = {
        title: compForm.title,
        work_type: compForm.work_type,
        points: 0,
        employee: auth.employeeId,
        source_task: task.id,
      };
      if (compForm.sci_form === 'publication' && compForm.pub_type) {
        payload.publication = { title: compForm.title, year: compForm.pub_year, pub_type: compForm.pub_type };
        if (compForm.pub_type === 'article') {
          payload.publication.article = {
            journal: compForm.journal, doi: compForm.doi || null,
            quartile: compForm.quartile, is_scopus: compForm.is_scopus,
          };
        } else {
          payload.publication.monograph = {
            publisher: compForm.publisher, isbn: compForm.isbn || null, pages_count: null,
          };
        }
      }
      if (compForm.sci_form === 'dissertation') {
        payload.dissertation = { stage: compForm.stage, defense_date: compForm.defense_date || null };
      }
      if (compForm.sci_form === 'project') {
        payload.project_participation = {
          role: compForm.project_role, budget: null,
          start_date: compForm.start_date, end_date: compForm.end_date || null,
        };
      }
      if (compForm.sci_form === 'software') {
        payload.software = { version: compForm.version, is_commercial: compForm.is_commercial };
      }
      const { data } = await worksApi.createScientificWork(payload);
      createdWorkId = data.id;
      createdKind = 'scientific_work';
    } else if (compForm.category === 'organizational') {
      const { data } = await worksApi.createOrganizationalWork({
        title: compForm.title,
        work_type: compForm.work_type,
        event_date: compForm.event_date,
        participants_count: compForm.participants_count,
        points: 0,
        employee: auth.employeeId,
        source_task: task.id,
      } as any);
      createdWorkId = data.id;
      createdKind = 'organizational_work';
    } else {
      const { data } = await worksApi.createTechnicalWork({
        title: compForm.title,
        work_type: compForm.work_type,
        work_date: compForm.work_date,
        registration_number: compForm.registration_number || null,
        metric: compForm.metric || null,
        base_points: 0,
        points: 0,
        employee: auth.employeeId,
        source_task: task.id,
      } as any);
      createdWorkId = data.id;
      createdKind = 'technical_work';
    }

    if (createdWorkId && compPendingFiles.value.length) {
      for (const f of compPendingFiles.value) {
        try {
          await attachmentsApi.upload(f, { [createdKind]: createdWorkId } as any);
        } catch {
          ElMessage.warning(`Не удалось загрузить ${f.name}`);
        }
      }
    }

    await tasksApi.completeTask(task.id);
    ElMessage.success('Задача завершена, работа отправлена на верификацию');
    showCompletionDialog.value = false;
    showDetailDialog.value = false;
    fetchTasks();
  } catch (e: any) {
    ElMessage.error(e.response?.data ? JSON.stringify(e.response.data) : 'Ошибка');
  } finally {
    saving.value = false;
  }
}

// --- fetch ---
async function fetchTasks() {
  loading.value = true;
  try {
    const { data } = await tasksApi.getTasks();
    tasks.value = data;
  } catch {
    ElMessage.error('Не удалось загрузить задачи');
  } finally {
    loading.value = false;
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
    employees.value = data;
  } catch (_) {}
}
async function fetchProjectsList() {
  try {
    const { data } = await projectsApi.getProjects();
    projectsList.value = data;
  } catch (_) {}
}

// --- utils ---
function formatSize(bytes: number) {
  if (!bytes) return '';
  if (bytes < 1024) return `${bytes} Б`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} КБ`;
  return `${(bytes / 1024 / 1024).toFixed(1)} МБ`;
}
function getPriorityType(p: string) {
  return p === 'high' ? 'danger' : p === 'medium' ? 'warning' : 'info';
}
function getPriorityLabel(p: string) {
  return { low: 'Низкий', medium: 'Средний', high: 'Высокий' }[p] || p;
}
function getStatusType(s: string) {
  return { assigned: 'warning', in_progress: 'primary', completed: 'success', overdue: 'danger' }[s] as any || 'info';
}
function getStatusLabel(s: string) {
  return { assigned: 'Назначена', in_progress: 'В работе', completed: 'Выполнена', overdue: 'Просрочена' }[s] || s;
}

onMounted(() => {
  fetchTasks();
  fetchKpiGroups();
  fetchProjectsList();
  if (auth.isManager) fetchEmployees();
});
</script>

<style scoped>
.tasks-page {
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

.task-tabs :deep(.el-tabs__header) {
  margin-bottom: 16px;
}

.tab-label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.tab-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 22px;
  padding: 0 6px;
  height: 20px;
  background: var(--bg);
  color: var(--text-secondary);
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
}

/* Kanban */
.kanban {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
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
  padding: 14px 16px;
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

.col-dot.assigned, .status-dot.assigned { background: var(--warning); }
.col-dot.in_progress, .status-dot.in_progress { background: var(--primary); }
.col-dot.completed, .status-dot.completed { background: var(--success); }
.col-dot.overdue, .status-dot.overdue { background: var(--danger); }

.col-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.col-count {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  background: var(--bg);
  padding: 2px 8px;
  border-radius: 10px;
}

.col-body {
  padding: 10px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.col-empty, .empty-state {
  color: var(--text-muted);
  font-size: 13px;
  text-align: center;
  padding: 40px 0;
}

.task-card {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  cursor: pointer;
  transition: all var(--transition);
}

.task-card:hover {
  box-shadow: var(--shadow-sm);
  border-color: var(--primary);
}

.task-card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}

.task-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.4;
}

.task-meta-row {
  display: flex;
  align-items: center;
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

/* Project list */
.list-wrap {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.list-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 14px 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all var(--transition);
}

.list-card:hover {
  box-shadow: var(--shadow-sm);
  border-color: var(--primary);
}

.list-card-left {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  min-width: 0;
  flex: 1;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-top: 5px;
  flex-shrink: 0;
}

.list-card-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.list-card-meta {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
}

.list-card-right {
  display: flex;
  gap: 8px;
  align-items: center;
}

/* Pool */
.pool-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 14px;
}

.pool-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  cursor: pointer;
  transition: all var(--transition);
}

.pool-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.pool-card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.hint-text {
  font-size: 12px;
  color: var(--text-muted);
}

/* Detail dialog */
.detail-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-description {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
  white-space: pre-wrap;
  padding: 12px;
  background: var(--bg);
  border-radius: var(--radius);
  border: 1px solid var(--border);
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-label {
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.detail-value {
  font-size: 13px;
  color: var(--text-primary);
  font-weight: 500;
}

.detail-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
  border-top: 1px solid var(--border);
  padding-top: 14px;
}

.detail-section-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-section-title {
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

.attachment-name:hover { text-decoration: underline; }

.attachment-size {
  font-size: 12px;
  color: var(--text-muted);
}

.no-attachments {
  font-size: 12px;
  color: var(--text-muted);
  padding: 8px 0;
}

.detail-footer {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  flex-wrap: wrap;
}

.pending-files {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 8px;
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

.pending-file > span:first-of-type { flex: 1; }

.is-done {
  opacity: 0.55;
}

.is-done .list-card-title {
  text-decoration: line-through;
}

.task-free {
  color: var(--success) !important;
  font-weight: 500;
}
</style>

<style>
/* Стабилизируем ширину диалога деталей задачи — иначе он прыгает */
.task-detail-dialog {
  width: 640px !important;
  max-width: 95vw !important;
}

.task-detail-dialog .el-dialog__body {
  min-height: 200px;
  padding: 16px 20px 8px;
}

.task-detail-dialog .detail-container {
  width: 100%;
}
</style>
