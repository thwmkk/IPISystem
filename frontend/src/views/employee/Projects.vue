<template>
  <div class="projects-page">
    <div class="page-top">
      <div>
        <h2 class="page-title">Проекты</h2>
        <p class="page-subtitle">Ваши исследовательские проекты</p>
      </div>
      <el-button type="primary" @click="createProject">
        <el-icon><Plus /></el-icon>
        Создать проект
      </el-button>
    </div>

    <div class="projects-grid">
      <div
        v-for="project in projects"
        :key="project.id"
        class="project-card"
      >
        <div class="project-header">
          <div class="project-icon">
            <el-icon :size="20"><Folder /></el-icon>
          </div>
          <el-tag size="small" effect="light" type="success">Активный</el-tag>
        </div>

        <h3 class="project-name">{{ project.name }}</h3>

        <div class="project-details">
          <div class="detail-row">
            <el-icon :size="14"><User /></el-icon>
            <span>{{ project.manager }}</span>
          </div>
          <div class="detail-row">
            <el-icon :size="14"><UserFilled /></el-icon>
            <span>{{ project.members.length }} участников</span>
          </div>
          <div class="detail-row">
            <el-icon :size="14"><Finished /></el-icon>
            <span>{{ project.tasks.length }} задач</span>
          </div>
        </div>

        <!-- Progress -->
        <div class="project-progress">
          <div class="progress-header">
            <span class="progress-label">Прогресс</span>
            <span class="progress-value">{{ project.progress }}%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: project.progress + '%' }"></div>
          </div>
        </div>

        <el-button class="open-btn" @click="openProject(project)">
          Открыть проект
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Plus, Folder, User, UserFilled, Finished } from "@element-plus/icons-vue";

const projects = ref([
  {
    id: 1,
    name: "Исследование ИИ",
    manager: "Иванов И.И.",
    members: ["Иванов", "Петров", "Сидоров"],
    tasks: [1, 2, 3],
    progress: 65,
  },
  {
    id: 2,
    name: "Квантовые вычисления",
    manager: "Петров П.П.",
    members: ["Петров", "Козлов"],
    tasks: [4, 5],
    progress: 30,
  },
]);

const createProject = () => { console.log("create project"); };
const openProject = (project: any) => { console.log("open", project); };
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
}

.project-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  transition: all var(--transition);
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
  background: var(--primary-light);
  color: var(--primary);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.project-name {
  font-size: 18px;
  font-weight: 600;
}

.project-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-secondary);
}

.project-progress {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
}

.progress-label {
  font-size: 12px;
  color: var(--text-muted);
}

.progress-value {
  font-size: 12px;
  font-weight: 600;
  color: var(--primary);
}

.progress-bar {
  height: 6px;
  background: var(--bg);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary), var(--accent));
  border-radius: 3px;
  transition: width 0.5s ease;
}

.open-btn {
  width: 100%;
  margin-top: 4px;
}
</style>
