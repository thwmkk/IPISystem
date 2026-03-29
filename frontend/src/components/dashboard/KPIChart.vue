<template>
  <el-card>
    <div ref="chartRef" class="chart"></div>
  </el-card>
</template>

<script setup>
import { onMounted, ref } from "vue";

const chartRef = ref(null);

onMounted(() => {
  // Заглушка (позже подключим echarts)
  chartRef.value.innerHTML = "📈 График IPI (подключим ECharts)";
});
</script>

<style scoped>
.chart {
  height: 300px;
}
</style>