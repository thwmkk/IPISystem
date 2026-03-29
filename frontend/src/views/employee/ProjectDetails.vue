<template>
  <div class="project-page">

    <h2>{{ project.name }}</h2>

    <p><b>Руководитель:</b> {{ project.manager }}</p>

    <!-- Участники -->
    <div>
      <h3>Участники</h3>
      <el-tag
        v-for="member in project.members"
        :key="member"
        style="margin-right: 5px"
      >
        {{ member }}
      </el-tag>
    </div>

    <!-- Задачи -->
    <div style="margin-top: 30px">
      <h3>Задачи проекта</h3>

      <div class="tasks">
        <el-card
          v-for="task in project.tasks"
          :key="task.id"
          class="task-card"
        >
          <h4>{{ task.title }}</h4>
          <p>Срок: {{ task.deadline }}</p>
        </el-card>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";

const project = ref({
  name: "ИИ проект",
  manager: "Иванов",
  members: ["Иванов", "Петров"],
  tasks: [
    { id: 1, title: "Модель", deadline: "2026-04-01" },
  ],
});
</script>

<style scoped>
.project-page {
  padding: 20px;
}

.tasks {
  display: flex;
  gap: 10px;
}

.task-card {
  width: 200px;
}
</style>