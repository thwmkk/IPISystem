<template>
  <!-- Login page — no sidebar/header -->
  <router-view v-if="isAuthPage" />

  <!-- Main layout -->
  <div v-else class="app-layout">
    <aside class="sidebar">
      <AppSidebar />
    </aside>

    <div class="main-area">
      <header class="header">
        <AppHeader />
      </header>

      <main class="content">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import AppSidebar from "@/components/ui/AppSidebar.vue";
import AppHeader from "@/components/ui/AppHeader.vue";

const route = useRoute();
const authPages = ["/login"];
const isAuthPage = computed(() => authPages.includes(route.path));
</script>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  width: 260px;
  flex-shrink: 0;
  background: var(--bg-sidebar);
  overflow-y: auto;
}

.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  height: 64px;
  flex-shrink: 0;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  padding: 0 32px;
  box-shadow: var(--shadow-xs);
}

.content {
  flex: 1;
  overflow-y: auto;
  padding: 32px;
  background: var(--bg);
}
</style>
