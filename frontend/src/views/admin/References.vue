<template>
  <div class="refs-page">
    <div class="page-top">
      <div>
        <h2 class="page-title">Справочники</h2>
        <p class="page-subtitle">Подразделения и роли пользователей</p>
      </div>
    </div>

    <el-tabs v-model="tab" class="refs-tabs">
      <!-- ====== Подразделения ====== -->
      <el-tab-pane label="Подразделения" name="departments">
        <div class="tab-top">
          <el-button type="primary" @click="openDeptAdd">
            <el-icon><Plus /></el-icon>
            Добавить подразделение
          </el-button>
        </div>
        <div class="table-card">
          <el-table :data="departments" stripe v-loading="loadingDept">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="department_name" label="Название" min-width="260" />
            <el-table-column prop="department_short_name" label="Сокр." width="140" />
            <el-table-column label="" width="110" align="right">
              <template #default="{ row }">
                <el-button size="small" circle type="primary" @click="openDeptEdit(row)">
                  <el-icon><Edit /></el-icon>
                </el-button>
                <el-button size="small" circle type="danger" @click="handleDeptDelete(row)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <!-- ====== Роли ====== -->
      <el-tab-pane label="Роли" name="roles">
        <div class="tab-top">
          <el-button type="primary" @click="openRoleAdd">
            <el-icon><Plus /></el-icon>
            Добавить роль
          </el-button>
        </div>
        <div class="table-card">
          <el-table :data="roles" stripe v-loading="loadingRole">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="role_name" label="Название" min-width="260" />
            <el-table-column label="" width="110" align="right">
              <template #default="{ row }">
                <el-button size="small" circle type="primary" @click="openRoleEdit(row)">
                  <el-icon><Edit /></el-icon>
                </el-button>
                <el-button size="small" circle type="danger" @click="handleRoleDelete(row)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- Dialog: Department -->
    <el-dialog
      v-model="showDeptDialog"
      :title="deptEditingId ? 'Редактировать подразделение' : 'Новое подразделение'"
      width="480px"
    >
      <el-form :model="deptForm" label-position="top">
        <el-form-item label="Название" required>
          <el-input v-model="deptForm.department_name" placeholder="Отдел..." />
        </el-form-item>
        <el-form-item label="Сокращённое название" required>
          <el-input v-model="deptForm.department_short_name" placeholder="ОТ-1" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDeptDialog = false">Отмена</el-button>
        <el-button type="primary" :loading="saving" @click="submitDept">Сохранить</el-button>
      </template>
    </el-dialog>

    <!-- Dialog: Role -->
    <el-dialog
      v-model="showRoleDialog"
      :title="roleEditingId ? 'Редактировать роль' : 'Новая роль'"
      width="440px"
    >
      <el-form :model="roleForm" label-position="top">
        <el-form-item label="Название" required>
          <el-input v-model="roleForm.role_name" placeholder="сотрудник / руководитель / администратор" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRoleDialog = false">Отмена</el-button>
        <el-button type="primary" :loading="saving" @click="submitRole">Сохранить</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { Plus, Edit, Delete } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import api from "@/api/axios";
import type { Department, UserRole } from "@/types/user";

const tab = ref<"departments" | "roles">("departments");

const departments = ref<Department[]>([]);
const roles = ref<UserRole[]>([]);
const loadingDept = ref(false);
const loadingRole = ref(false);
const saving = ref(false);

const showDeptDialog = ref(false);
const deptEditingId = ref<number | null>(null);
const deptForm = reactive({ department_name: "", department_short_name: "" });

const showRoleDialog = ref(false);
const roleEditingId = ref<number | null>(null);
const roleForm = reactive({ role_name: "" });

async function fetchDepartments() {
  loadingDept.value = true;
  try {
    const { data } = await api.get<Department[]>("/departments/");
    departments.value = data;
  } catch {
    ElMessage.error("Не удалось загрузить подразделения");
  } finally {
    loadingDept.value = false;
  }
}

async function fetchRoles() {
  loadingRole.value = true;
  try {
    const { data } = await api.get<UserRole[]>("/roles/");
    roles.value = data;
  } catch {
    ElMessage.error("Не удалось загрузить роли");
  } finally {
    loadingRole.value = false;
  }
}

function openDeptAdd() {
  deptEditingId.value = null;
  Object.assign(deptForm, { department_name: "", department_short_name: "" });
  showDeptDialog.value = true;
}

function openDeptEdit(row: Department) {
  deptEditingId.value = row.id;
  Object.assign(deptForm, {
    department_name: row.department_name,
    department_short_name: row.department_short_name,
  });
  showDeptDialog.value = true;
}

async function submitDept() {
  if (!deptForm.department_name || !deptForm.department_short_name) {
    ElMessage.warning("Заполните оба поля");
    return;
  }
  saving.value = true;
  try {
    if (deptEditingId.value) {
      await api.patch(`/departments/${deptEditingId.value}/`, deptForm);
    } else {
      await api.post("/departments/", deptForm);
    }
    ElMessage.success("Сохранено");
    showDeptDialog.value = false;
    fetchDepartments();
  } catch (e: any) {
    ElMessage.error(e.response?.data ? JSON.stringify(e.response.data) : "Ошибка");
  } finally {
    saving.value = false;
  }
}

async function handleDeptDelete(row: Department) {
  try {
    await ElMessageBox.confirm(`Удалить «${row.department_short_name}»?`, "Подтверждение", {
      type: "warning",
    });
  } catch {
    return;
  }
  try {
    await api.delete(`/departments/${row.id}/`);
    ElMessage.success("Удалено");
    fetchDepartments();
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || "Нельзя удалить — подразделение используется");
  }
}

function openRoleAdd() {
  roleEditingId.value = null;
  roleForm.role_name = "";
  showRoleDialog.value = true;
}

function openRoleEdit(row: UserRole) {
  roleEditingId.value = row.id;
  roleForm.role_name = row.role_name;
  showRoleDialog.value = true;
}

async function submitRole() {
  if (!roleForm.role_name) {
    ElMessage.warning("Укажите название");
    return;
  }
  saving.value = true;
  try {
    if (roleEditingId.value) {
      await api.patch(`/roles/${roleEditingId.value}/`, roleForm);
    } else {
      await api.post("/roles/", roleForm);
    }
    ElMessage.success("Сохранено");
    showRoleDialog.value = false;
    fetchRoles();
  } catch (e: any) {
    ElMessage.error(e.response?.data ? JSON.stringify(e.response.data) : "Ошибка");
  } finally {
    saving.value = false;
  }
}

async function handleRoleDelete(row: UserRole) {
  try {
    await ElMessageBox.confirm(`Удалить роль «${row.role_name}»?`, "Подтверждение", {
      type: "warning",
    });
  } catch {
    return;
  }
  try {
    await api.delete(`/roles/${row.id}/`);
    ElMessage.success("Удалено");
    fetchRoles();
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || "Нельзя удалить — роль используется");
  }
}

onMounted(() => {
  fetchDepartments();
  fetchRoles();
});
</script>

<style scoped>
.refs-page {
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

.refs-tabs :deep(.el-tabs__header) {
  margin-bottom: 20px;
}

.tab-top {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 16px;
}

.table-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}
</style>
