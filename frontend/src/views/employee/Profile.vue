<template>
  <div class="profile-page">
    <div class="page-top">
      <div class="page-top-left">
        <el-button
          v-if="route.query.from === 'department'"
          link
          @click="$router.push({ path: '/manager/department', query: { tab: 'compare' } })"
        >
          <el-icon><ArrowLeft /></el-icon>
          Назад в Мой отдел
        </el-button>
        <h2 class="page-title">Профиль</h2>
        <p class="page-subtitle">Информация о сотруднике</p>
      </div>
      <el-button v-if="auth.isManager && employee" type="primary" @click="openEdit">
        <el-icon><Edit /></el-icon>
        Редактировать
      </el-button>
    </div>

    <div class="profile-layout" v-loading="loading">
      <!-- Avatar + name card -->
      <div class="profile-hero">
        <div class="hero-avatar">
          {{ initials }}
        </div>
        <div class="hero-info">
          <h2 class="hero-name">{{ employee?.full_name || '—' }}</h2>
          <p class="hero-position">{{ employee?.position || '—' }}</p>
          <el-tag effect="light" size="small">{{ auth.roleLabel }}</el-tag>
        </div>
      </div>

      <!-- Info cards -->
      <div class="info-grid">
        <div class="info-card">
          <div class="info-icon email-icon">
            <el-icon :size="20"><Message /></el-icon>
          </div>
          <div class="info-body">
            <span class="info-label">Email</span>
            <span class="info-value">{{ employee?.email || '—' }}</span>
          </div>
        </div>

        <div class="info-card">
          <div class="info-icon dept-icon">
            <el-icon :size="20"><OfficeBuilding /></el-icon>
          </div>
          <div class="info-body">
            <span class="info-label">Подразделение</span>
            <span class="info-value">{{ employee?.department_name || '—' }}</span>
          </div>
        </div>

        <div class="info-card">
          <div class="info-icon age-icon">
            <el-icon :size="20"><User /></el-icon>
          </div>
          <div class="info-body">
            <span class="info-label">Возраст</span>
            <span class="info-value">{{ employee?.age ? employee.age + ' лет' : '—' }}</span>
          </div>
        </div>

        <div class="info-card">
          <div class="info-icon exp-icon">
            <el-icon :size="20"><Timer /></el-icon>
          </div>
          <div class="info-body">
            <span class="info-label">Стаж</span>
            <span class="info-value">{{ employee?.experience ? employee.experience + ' лет' : '—' }}</span>
          </div>
        </div>

        <div class="info-card">
          <div class="info-icon degree-icon">
            <el-icon :size="20"><Medal /></el-icon>
          </div>
          <div class="info-body">
            <span class="info-label">Научная степень</span>
            <span class="info-value">{{ employee?.academic_degree || 'Нет' }}</span>
          </div>
        </div>

        <div class="info-card">
          <div class="info-icon phd-icon">
            <el-icon :size="20"><Reading /></el-icon>
          </div>
          <div class="info-body">
            <span class="info-label">Категория</span>
            <span class="info-value">{{ positionTypeDisplay }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit dialog (руководитель / админ) -->
    <el-dialog v-model="showEditDialog" title="Редактировать профиль" width="520px">
      <el-form :model="form" label-position="top">
        <el-form-item label="ФИО" required>
          <el-input v-model="form.full_name" />
        </el-form-item>
        <div class="form-row">
          <el-form-item label="Должность" required>
            <el-input v-model="form.position" />
          </el-form-item>
          <el-form-item label="Возраст" required>
            <el-input-number v-model="form.age" :min="18" :max="99" />
          </el-form-item>
        </div>
        <div class="form-row">
          <el-form-item label="Стаж (лет)" required>
            <el-input-number v-model="form.experience" :min="0" :max="80" />
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
        <el-button @click="showEditDialog = false">Отмена</el-button>
        <el-button type="primary" :loading="saving" @click="submitEdit">Сохранить</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from "vue";
import { useRoute } from "vue-router";
import { useAuthStore } from "@/store/auth";
import { Message, OfficeBuilding, User, Timer, Medal, Reading, Edit, ArrowLeft } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { employeesApi } from "@/api/kpi";
import type { Employee, PositionType } from "@/types/user";
import { POSITION_TYPE_LABELS } from "@/types/user";

const auth = useAuthStore();
const loading = ref(false);
const saving = ref(false);
const employee = ref<Employee | null>(null);
const showEditDialog = ref(false);

const form = reactive({
  full_name: "",
  position: "",
  age: 25,
  experience: 0,
  position_type: 'researcher' as PositionType,
  phd_year: null as number | null,
  academic_degree: null as string | null,
});

const positionTypeDisplay = computed(() => {
  if (!employee.value) return '—';
  const base = POSITION_TYPE_LABELS[employee.value.position_type] || '—';
  if (employee.value.position_type === 'phd_student' && employee.value.phd_year) {
    return `${base} (${employee.value.phd_year} курс)`;
  }
  return base;
});

const initials = computed(() => {
  const parts = (employee.value?.full_name || auth.fullName || 'U').split(' ');
  return parts.map((p) => p[0]).join('').slice(0, 2);
});

const route = useRoute();
const targetEmployeeId = computed(() => {
  const q = route.query.employee_id;
  if (typeof q === 'string' && q) return Number(q);
  if (typeof q === 'number') return q;
  return auth.employeeId;
});

async function fetchProfile() {
  const id = targetEmployeeId.value;
  if (!id) return;
  loading.value = true;
  try {
    const { data } = await employeesApi.getById(id);
    employee.value = data;
  } catch (_) {}
  loading.value = false;
}

watch(targetEmployeeId, () => fetchProfile());

function openEdit() {
  if (!employee.value) return;
  Object.assign(form, {
    full_name: employee.value.full_name,
    position: employee.value.position,
    age: employee.value.age,
    experience: employee.value.experience,
    position_type: employee.value.position_type,
    phd_year: employee.value.phd_year,
    academic_degree: employee.value.academic_degree,
  });
  showEditDialog.value = true;
}

async function submitEdit() {
  if (!employee.value) return;
  if (!form.full_name || !form.position) {
    ElMessage.warning("Заполните ФИО и должность");
    return;
  }
  saving.value = true;
  try {
    await employeesApi.update(employee.value.id, form as any);
    ElMessage.success("Профиль обновлён");
    showEditDialog.value = false;
    await fetchProfile();
    if (employee.value.id === auth.employeeId) {
      await auth.fetchMe();
    }
  } catch (e: any) {
    ElMessage.error(e.response?.data ? JSON.stringify(e.response.data) : "Ошибка");
  } finally {
    saving.value = false;
  }
}

onMounted(fetchProfile);
</script>

<style scoped>
.profile-page {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.page-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.page-top-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
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

.profile-layout {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Hero card */
.profile-hero {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: 40px;
  display: flex;
  align-items: center;
  gap: 32px;
}

.hero-avatar {
  width: 80px;
  height: 80px;
  border-radius: 20px;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  color: #fff;
  font-size: 28px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.hero-name {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.hero-position {
  font-size: 15px;
  color: var(--text-secondary);
  margin-top: 4px;
  margin-bottom: 8px;
}

/* Info grid */
.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.info-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all var(--transition);
}

.info-card:hover {
  box-shadow: var(--shadow-sm);
}

.info-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.email-icon { background: var(--primary-light); color: var(--primary); }
.dept-icon { background: #ecfdf5; color: var(--success); }
.age-icon { background: #f5f3ff; color: var(--accent); }
.exp-icon { background: #fffbeb; color: var(--warning); }
.degree-icon { background: #fef2f2; color: var(--danger); }
.phd-icon { background: #f0f9ff; color: #0ea5e9; }

.info-body {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.info-label {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 500;
}

.info-value {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
</style>
