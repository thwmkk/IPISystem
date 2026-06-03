<template>
  <div class="employees-page">
    <div class="page-top">
      <div>
        <h2 class="page-title">Сотрудники</h2>
        <p class="page-subtitle">Управление сотрудниками подразделения</p>
      </div>
      <el-button type="primary" @click="openAdd">
        <el-icon><Plus /></el-icon>
        Добавить сотрудника
      </el-button>
    </div>

    <!-- Table -->
    <div class="table-card">
      <el-table :data="employees" stripe v-loading="loading">
        <el-table-column prop="full_name" label="ФИО" min-width="180" />
        <el-table-column prop="email" label="Email" width="200" />
        <el-table-column prop="position" label="Должность" width="160" />
        <el-table-column prop="department_name" label="Подразделение" width="140" />
        <el-table-column prop="role_name" label="Роль" width="130">
          <template #default="{ row }">
            <el-tag :type="getRoleTag(row.role_name)" effect="light" size="small">
              {{ row.role_name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Категория" width="140">
          <template #default="{ row }">
            {{ positionTypeDisplay(row) }}
          </template>
        </el-table-column>
        <el-table-column prop="experience" label="Стаж" width="80" />
        <el-table-column prop="academic_degree" label="Степень" width="120" />
        <el-table-column label="" width="110" align="right">
          <template #default="{ row }">
            <el-button size="small" circle type="primary" @click="openEdit(row)">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button v-if="row.id !== auth.employeeId" size="small" circle type="danger" @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Add / Edit Dialog -->
    <el-dialog v-model="showDialog" :title="isEditing ? 'Редактировать сотрудника' : 'Новый сотрудник'" width="520px" @close="resetForm">
      <el-form :model="form" label-position="top">
        <el-form-item label="ФИО" required>
          <el-input v-model="form.full_name" placeholder="Иванов Иван Иванович" />
        </el-form-item>
        <el-form-item label="Email" required>
          <el-input v-model="form.email" placeholder="ivanov@isem.irk.ru" :disabled="isEditing" />
        </el-form-item>
        <div class="form-row">
          <el-form-item label="Должность" required>
            <el-input v-model="form.position" placeholder="н.с." />
          </el-form-item>
          <el-form-item label="Возраст" required>
            <el-input-number v-model="form.age" :min="18" :max="99" />
          </el-form-item>
        </div>
        <div class="form-row">
          <el-form-item label="Стаж (лет)" required>
            <el-input-number v-model="form.experience" :min="0" :max="60" />
          </el-form-item>
          <el-form-item label="Научная степень">
            <el-select v-model="form.academic_degree" clearable placeholder="Нет">
              <el-option label="к.т.н." value="к.т.н." />
              <el-option label="д.т.н." value="д.т.н." />
              <el-option label="к.ф.-м.н." value="к.ф.-м.н." />
              <el-option label="д.ф.-м.н." value="д.ф.-м.н." />
            </el-select>
          </el-form-item>
        </div>
        <div class="form-row">
          <el-form-item label="Подразделение" required>
            <el-select v-model="form.department" placeholder="Выберите">
              <el-option
                v-for="d in departments"
                :key="d.id"
                :label="d.department_short_name"
                :value="d.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="Роль" required>
            <el-select v-model="form.role" placeholder="Выберите">
              <el-option
                v-for="r in roles"
                :key="r.id"
                :label="r.role_name"
                :value="r.id"
              />
            </el-select>
          </el-form-item>
        </div>
        <div class="form-row">
          <el-form-item label="Категория" required>
            <el-select v-model="form.position_type" style="width: 100%">
              <el-option
                v-for="(label, key) in POSITION_TYPE_LABELS"
                :key="key"
                :label="label"
                :value="key"
              />
            </el-select>
          </el-form-item>
          <el-form-item
            v-if="form.position_type === 'phd_student'"
            label="Курс аспирантуры"
          >
            <el-select v-model="form.phd_year" style="width: 100%">
              <el-option :label="'1 курс'" :value="1" />
              <el-option :label="'2 курс'" :value="2" />
              <el-option :label="'3 курс'" :value="3" />
              <el-option :label="'4 курс'" :value="4" />
            </el-select>
          </el-form-item>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">Отмена</el-button>
        <el-button type="primary" :loading="saving" @click="isEditing ? handleUpdate() : handleCreate()">
          {{ isEditing ? 'Сохранить' : 'Создать' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- Password Dialog -->
    <el-dialog v-model="showPasswordDialog" title="Сотрудник создан" width="420px">
      <p style="margin-bottom: 12px">Учётные данные для входа:</p>
      <div class="credentials">
        <div><strong>Email:</strong> {{ createdEmail }}</div>
        <div><strong>Пароль:</strong> <code>{{ createdPassword }}</code></div>
      </div>
      <p class="credentials-hint">Сохраните пароль — он показывается только один раз.</p>
      <template #footer>
        <el-button type="primary" @click="showPasswordDialog = false">Понятно</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { Plus, Edit, Delete } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { employeesApi } from "@/api/kpi";
import { useAuthStore } from "@/store/auth";
import api from "@/api/axios";
import type { Employee, Department, UserRole, PositionType } from "@/types/user";
import { POSITION_TYPE_LABELS } from "@/types/user";

const auth = useAuthStore();

const loading = ref(false);
const saving = ref(false);
const employees = ref<Employee[]>([]);
const departments = ref<Department[]>([]);
const roles = ref<UserRole[]>([]);

const showDialog = ref(false);
const isEditing = ref(false);
const editingId = ref<number | null>(null);

const showPasswordDialog = ref(false);
const createdEmail = ref("");
const createdPassword = ref("");

const defaultForm = () => ({
  full_name: "",
  email: "",
  position: "",
  age: 25,
  experience: 0,
  position_type: 'researcher' as PositionType,
  phd_year: null as number | null,
  academic_degree: null as string | null,
  department: null as number | null,
  role: null as number | null,
});

function positionTypeDisplay(emp: Employee) {
  const label = POSITION_TYPE_LABELS[emp.position_type] || '—';
  if (emp.position_type === 'phd_student' && emp.phd_year) {
    return `${label} (${emp.phd_year} курс)`;
  }
  return label;
}

const form = ref(defaultForm());

const resetForm = () => {
  form.value = defaultForm();
  isEditing.value = false;
  editingId.value = null;
};

function openAdd() {
  resetForm();
  showDialog.value = true;
}

function openEdit(row: Employee) {
  isEditing.value = true;
  editingId.value = row.id;
  form.value = {
    full_name: row.full_name,
    email: row.email,
    position: row.position,
    age: row.age,
    experience: row.experience,
    position_type: row.position_type,
    phd_year: row.phd_year,
    academic_degree: row.academic_degree,
    department: row.department,
    role: row.role,
  };
  showDialog.value = true;
}

const getRoleTag = (role: string) =>
  ({ сотрудник: "", руководитель: "warning", администратор: "danger" }[role] as any);

async function fetchData() {
  loading.value = true;
  try {
    const [empRes, depRes, roleRes] = await Promise.all([
      employeesApi.getAll(),
      api.get<Department[]>("/departments/"),
      api.get<UserRole[]>("/roles/"),
    ]);
    employees.value = empRes.data;
    departments.value = depRes.data;
    roles.value = roleRes.data;
  } catch {
    ElMessage.error("Не удалось загрузить данные");
  } finally {
    loading.value = false;
  }
}

async function handleCreate() {
  if (!form.value.full_name || !form.value.email || !form.value.department || !form.value.role) {
    ElMessage.warning("Заполните обязательные поля");
    return;
  }
  saving.value = true;
  try {
    const { data } = await employeesApi.create(form.value as any);
    createdEmail.value = form.value.email;
    createdPassword.value = data.generated_password;
    showDialog.value = false;
    showPasswordDialog.value = true;
    resetForm();
    await fetchData();
    ElMessage.success("Сотрудник создан");
  } catch {
    ElMessage.error("Не удалось создать сотрудника");
  } finally {
    saving.value = false;
  }
}

async function handleUpdate() {
  if (!form.value.full_name || !form.value.department || !form.value.role) {
    ElMessage.warning("Заполните обязательные поля");
    return;
  }
  saving.value = true;
  try {
    const { email: _, ...updateData } = form.value;
    await employeesApi.update(editingId.value!, updateData as any);
    showDialog.value = false;
    // If editing self, refresh auth store so header/sidebar update
    if (editingId.value === auth.employeeId) {
      await auth.fetchMe();
    }
    resetForm();
    await fetchData();
    ElMessage.success("Сотрудник обновлён");
  } catch {
    ElMessage.error("Не удалось обновить сотрудника");
  } finally {
    saving.value = false;
  }
}

async function handleDelete(row: Employee) {
  try {
    await ElMessageBox.confirm(
      `Удалить сотрудника ${row.full_name}?`,
      "Подтверждение",
      { type: "warning" }
    );
    await employeesApi.delete(row.id);
    employees.value = employees.value.filter((e) => e.id !== row.id);
    ElMessage.success("Сотрудник удалён");
  } catch {
    // cancelled
  }
}

onMounted(fetchData);
</script>

<style scoped>
.employees-page {
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

.table-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.credentials {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 14px;
}

.credentials code {
  background: var(--primary-light);
  padding: 2px 8px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 14px;
  user-select: all;
}

.credentials-hint {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 12px;
}
</style>
