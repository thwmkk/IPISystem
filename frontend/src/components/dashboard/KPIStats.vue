<template>
  <el-card>
    <div class="kpi">
      <div class="value">IPI: 87.5</div>
      <div class="delta">+5.2 ↑</div>
      <div class="period">Период: март</div>
    </div>
  </el-card>
</template>

<script setup>
</script>

<style scoped>
.kpi {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.value {
  font-size: 28px;
  font-weight: bold;
}

.delta {
  color: green;
}

.period {
  color: #888;
}
</style>