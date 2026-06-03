<template>
  <div class="projects-page">
    <div class="page-top">
      <div>
        <h2 class="page-title">Проекты</h2>
        <p class="page-subtitle">Ваши исследовательские проекты</p>
      </div>
      <el-button type="primary" @click="openCreateDialog">
        <el-icon><Plus /></el-icon>
        Создать проект
      </el-button>
    </div>

    <div class="projects-grid" v-loading="loading">
      <div v-if="projects.length === 0 && !loading" class="empty-state">
        <el-icon :size="48" color="var(--text-muted)"><Folder /></el-icon>
        <p>Нет проектов</p>
      </div>

      <div
        v-for="project in projects"
        :key="project.id"
        class="project-card"
        @click="openProject(project.id)"
      >
        <div class="project-header">
          <div class="project-icon">
            <el-icon :size="20"><Folder /></el-icon>
          </div>
          <el-tag size="small" effect="light" :type="getStatusType(project)">
            {{ getStatusLabel(project) }}
          </el-tag>
        </div>

        <h3 class="project-name">{{ project.name }}</h3>

        <div class="project-details">
          <div class="detail-row">
            <el-icon :size="14"><User /></el-icon>
            <span>{{ project.creator_name }}</span>
          </div>
          <div class="detail-row">
            <el-icon :size="14"><UserFilled /></el-icon>
            <span>{{ project.members_count }} участников</span>
          </div>
          <div class="detail-row" v-if="project.budget">
            <el-icon :size="14"><Money /></el-icon>
            <span>{{ formatBudget(project.budget) }}</span>
          </div>
        </div>

        <div class="project-dates">
          <span>{{ project.start_date }}</span>
          <span v-if="project.end_date"> — {{ project.end_date }}</span>
        </div>
      </div>
    </div>

    <!-- Create Dialog -->
    <el-dialog v-model="showFormDialog" title="Создать проект" width="500px" destroy-on-close>
      <el-form :model="form" label-position="top">
        <el-form-item label="Название" required>
          <el-input v-model="form.name" placeholder="Название проекта" />
        </el-form-item>
        <el-form-item label="Описание">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="Бюджет (руб.)">
          <el-input-number v-model="form.budget" :min="0" :step="100000" style="width: 100%" />
        </el-form-item>
        <div class="form-row">
          <el-form-item label="Дата начала" required>
            <el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
          </el-form-item>
          <el-form-item label="Дата окончания">
            <el-date-picker v-model="form.end_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
          </el-form-item>
        </div>
        <el-form-item label="Участники (вы автоматически будете добавлены)">
          <el-select
            v-model="form.member_ids"
            multiple
            filterable
            placeholder="Выберите сотрудников"
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
        <el-button @click="showFormDialog = false">Отмена</el-button>
        <el-button type="primary" @click="submitProject" :loading="saving">Создать</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { Plus, Folder, User, UserFilled, Money } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { projectsApi } from "@/api/projects";
import { employeesApi } from "@/api/kpi";
import { useAuthStore } from "@/store/auth";
import type { Project } from "@/types/work";
import type { Employee } from "@/types/user";

const router = useRouter();
const auth = useAuthStore();
const loading = ref(false);
const saving = ref(false);
const projects = ref<Project[]>([]);

const showFormDialog = ref(false);
const employees = ref<Employee[]>([]);
const form = reactive({
  name: '',
  description: '',
  budget: null as number | null,
  start_date: '',
  end_date: '',
  member_ids: [] as number[],
});

const availableEmployees = computed(() =>
  employees.value.filter(e => e.id !== auth.employeeId)
);

function getStatusType(project: Project) {
  if (project.end_date && new Date(project.end_date) < new Date()) return 'info';
  return 'success';
}

function getStatusLabel(project: Project) {
  if (project.end_date && new Date(project.end_date) < new Date()) return 'Завершён';
  return 'Активный';
}

function formatBudget(budget: number) {
  return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB', maximumFractionDigits: 0 }).format(budget);
}

async function fetchProjects() {
  loading.value = true;
  try {
    const { data } = await projectsApi.getProjects();
    projects.value = data;
  } catch {
    ElMessage.error("Не удалось загрузить проекты");
  } finally {
    loading.value = false;
  }
}

async function fetchEmployees() {
  try {
    const { data } = await employeesApi.getAll();
    employees.value = data;
  } catch (_) {}
}

function openCreateDialog() {
  Object.assign(form, {
    name: '', description: '', budget: null,
    start_date: '', end_date: '', member_ids: [],
  });
  if (!employees.value.length) fetchEmployees();
  showFormDialog.value = true;
}

function openProject(id: number) {
  router.push(`/employee/projects/${id}`);
}

async function submitProject() {
  if (!form.name || !form.start_date) {
    ElMessage.warning("Заполните название и дату начала");
    return;
  }
  saving.value = true;
  try {
    const { data: created } = await projectsApi.createProject({
      name: form.name,
      description: form.description || null,
      budget: form.budget,
      start_date: form.start_date,
      end_date: form.end_date || null,
    } as any);
    for (const empId of form.member_ids) {
      try {
        await projectsApi.addMember(created.id, empId);
      } catch {
        ElMessage.warning(`Не удалось добавить участника #${empId}`);
      }
    }
    ElMessage.success("Проект создан");
    showFormDialog.value = false;
    fetchProjects();
  } catch (e: any) {
    ElMessage.error(e.response?.data ? JSON.stringify(e.response.data) : "Ошибка");
  } finally {
    saving.value = false;
  }
}

// ensure auth has employee id
if (!auth.employeeId) auth.fetchMe?.();

onMounted(() => {
  fetchProjects();
  fetchEmployees();
});
</script>

<style scoped>
.projects-page {
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

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  min-height: 120px;
}

.empty-state {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 60px 0;
  color: var(--text-muted);
}

.project-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  transition: all var(--transition);
  cursor: pointer;
}

.project-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.project-icon {
  width: 40px;
  height: 40px;
  background: var(--primary-soft);
  color: var(--primary);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.project-name {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.project-details {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-secondary);
}

.project-dates {
  font-size: 12px;
  color: var(--text-muted);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
</style>
