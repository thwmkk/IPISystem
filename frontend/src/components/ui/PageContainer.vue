<template>
  <div class="page-container">
    <div class="page-header" v-if="$slots.header">
      <slot name="header" />
    </div>

    <div class="page-content">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
</style>