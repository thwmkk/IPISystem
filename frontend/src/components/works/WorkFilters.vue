<template>
  <el-card>
    <div class="filters">

      <el-select v-model="type" placeholder="Тип">
        <el-option label="Научная" value="Научная" />
        <el-option label="Техническая" value="Техническая" />
        <el-option label="Организационная" value="Организационная" />
      </el-select>

      <el-select v-model="status" placeholder="Статус">
        <el-option label="Подтверждено" value="Подтверждено" />
        <el-option label="Ожидает" value="Ожидает" />
        <el-option label="Отклонено" value="Отклонено" />
      </el-select>

      <el-date-picker
        v-model="dateRange"
        type="daterange"
        start-placeholder="От"
        end-placeholder="До"
      />

      <el-button @click="reset">Сбросить</el-button>

    </div>
  </el-card>
</template>

<script setup>
import { ref, watch } from "vue";

const emit = defineEmits(["filter"]);

const type = ref("");
const status = ref("");
const dateRange = ref([]);

watch([type, status, dateRange], () => {
  emit("filter", {
    type: type.value,
    status: status.value,
    dateRange: dateRange.value,
  });
});

const reset = () => {
  type.value = "";
  status.value = "";
  dateRange.value = [];
};
</script>

<style scoped>
.filters {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}
</style>