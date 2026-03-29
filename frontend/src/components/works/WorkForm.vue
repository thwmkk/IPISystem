<template>
  <el-form :model="form" label-width="120px">

    <el-form-item label="Название">
      <el-input v-model="form.title" />
    </el-form-item>

    <el-form-item label="Тип">
      <el-select v-model="form.type">
        <el-option label="Научная" value="Научная" />
        <el-option label="Техническая" value="Техническая" />
        <el-option label="Организационная" value="Организационная" />
      </el-select>
    </el-form-item>

    <el-form-item label="Категория">
      <el-input v-model="form.category" />
    </el-form-item>

    <el-form-item label="Дата">
      <el-date-picker v-model="form.date" />
    </el-form-item>

    <!-- Динамические поля -->
    <div v-if="form.type === 'Научная'">
      <el-form-item label="Журнал">
        <el-input v-model="form.journal" />
      </el-form-item>
      <el-form-item label="DOI">
        <el-input v-model="form.doi" />
      </el-form-item>
    </div>

    <div v-if="form.type === 'Техническая'">
      <el-form-item label="Версия">
        <el-input v-model="form.version" />
      </el-form-item>
    </div>

    <div v-if="form.type === 'Организационная'">
      <el-form-item label="Описание">
        <el-input v-model="form.description" />
      </el-form-item>
    </div>

    <el-form-item>
      <el-button type="primary" @click="submit">
        Сохранить
      </el-button>
    </el-form-item>

  </el-form>
</template>

<script setup>
import { reactive, watch } from "vue";

const props = defineProps({
  work: Object,
});

const emit = defineEmits(["submit"]);

const form = reactive({
  id: null,
  title: "",
  type: "",
  category: "",
  date: "",
});

watch(
  () => props.work,
  (val) => {
    if (val) Object.assign(form, val);
  },
  { immediate: true }
);

const submit = () => {
  emit("submit", { ...form });
};
</script>