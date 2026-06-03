<template>
  <div class="breakdown-panel">
    <!-- Formula -->
    <div class="formula-card">
      <div class="formula">
        IPI = Σ <i>(W<sub>i</sub></i> × Σ <i>(W<sub>ij</sub></i> × <i>B<sub>ij</sub>))</i>
      </div>
      <div class="formula-desc">
        W<sub>ij</sub> = W<sub>base</sub> × k<sub>возраст</sub> × k<sub>стаж</sub> × k<sub>аспирант</sub>
      </div>
    </div>

    <!-- Employee factors -->
    <div class="factors-row">
      <div class="factor-card">
        <div class="factor-label">Категория</div>
        <div class="factor-value">{{ posLabel }}</div>
      </div>
      <div class="factor-card">
        <div class="factor-label">k<sub>возраст</sub></div>
        <div class="factor-value">×{{ breakdown.factors.k_age }}</div>
      </div>
      <div class="factor-card">
        <div class="factor-label">k<sub>стаж</sub></div>
        <div class="factor-value">×{{ breakdown.factors.k_exp }}</div>
      </div>
      <div class="factor-card">
        <div class="factor-label">k<sub>аспирант</sub></div>
        <div class="factor-value">×{{ breakdown.factors.k_phd }}</div>
      </div>
      <div class="factor-card factor-total">
        <div class="factor-label">Итого множитель</div>
        <div class="factor-value">×{{ breakdown.factors.k_total }}</div>
      </div>
    </div>

    <!-- Groups -->
    <div class="groups">
      <div v-for="g in breakdown.groups" :key="g.group_id" class="group-block">
        <div class="group-head">
          <h3 class="group-name">{{ g.name }}</h3>
          <div class="group-wi">
            W<sub>i</sub> = <b>{{ g.wi }}</b>
          </div>
        </div>

        <table class="indicators-table">
          <thead>
            <tr>
              <th class="th-left">Показатель</th>
              <th>W<sub>base</sub></th>
              <th>×k</th>
              <th>= W<sub>ij</sub></th>
              <th>B<sub>ij</sub></th>
              <th>Вклад</th>
              <th class="th-narrow"></th>
            </tr>
          </thead>
          <tbody>
            <template v-for="ind in g.indicators" :key="ind.work_type_key">
              <tr :class="{ 'has-works': ind.works.length > 0 }">
                <td class="th-left">
                  <div class="ind-name">{{ ind.name }}</div>
                  <div class="ind-key">{{ ind.work_type_key }}</div>
                </td>
                <td>{{ ind.w_base }}</td>
                <td class="cell-muted">×{{ breakdown.factors.k_total }}</td>
                <td><b>{{ ind.wij }}</b></td>
                <td>
                  <span v-if="ind.works.length === 0">{{ ind.bij }}</span>
                  <span v-else class="bij-formula">
                    {{ ind.works.map(w => w.points).join(' + ') }}
                    = <b>{{ ind.bij }}</b>
                  </span>
                </td>
                <td><b class="contribution">{{ ind.contribution }}</b></td>
                <td class="th-narrow">
                  <el-button
                    v-if="ind.works.length"
                    size="small"
                    link
                    @click="toggle(ind.work_type_key)"
                  >
                    <el-icon :class="{ rot: expanded[ind.work_type_key] }">
                      <ArrowDown />
                    </el-icon>
                  </el-button>
                </td>
              </tr>
              <tr v-if="ind.works.length && expanded[ind.work_type_key]" class="works-row">
                <td colspan="7">
                  <div class="works-list">
                    <div
                      v-for="w in ind.works"
                      :key="w.kind + '-' + w.id"
                      class="work-item"
                      :class="{ clickable: clickable }"
                      @click="onWorkClick(w)"
                    >
                      <el-icon :size="13"><Document /></el-icon>
                      <span class="work-title">{{ w.title }}</span>
                      <span class="work-points">{{ w.points }} б.</span>
                      <el-icon v-if="clickable" :size="12" class="work-arrow"><Right /></el-icon>
                    </div>
                  </div>
                </td>
              </tr>
            </template>
            <tr v-if="g.indicators.length === 0">
              <td colspan="7" class="empty-row">показателей нет</td>
            </tr>
          </tbody>
        </table>

        <div class="group-foot">
          <span>Σ внутри группы = <b>{{ g.sum_inner }}</b></span>
          <span class="group-contribution">
            Вклад группы: W<sub>i</sub> × Σ = <b>{{ g.wi }}</b> × <b>{{ g.sum_inner }}</b>
            = <b class="result">{{ g.contribution }}</b>
          </span>
        </div>
      </div>
    </div>

    <!-- Total -->
    <div class="total-card">
      <div class="total-formula">
        IPI = {{ breakdown.groups.map(g => g.contribution).join(' + ') || '0' }}
      </div>
      <div class="total-value">
        = {{ breakdown.total_ipi }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { ArrowDown, Document, Right } from "@element-plus/icons-vue";
import type { IPIBreakdown, IPIBreakdownWork } from "@/api/kpi";
import { POSITION_TYPE_LABELS } from "@/types/user";

const props = withDefaults(defineProps<{
  breakdown: IPIBreakdown
  clickable?: boolean
}>(), { clickable: true });

const emit = defineEmits<{
  (e: 'work-click', work: IPIBreakdownWork): void
}>();

const posLabel = computed(() => {
  const base = POSITION_TYPE_LABELS[props.breakdown.position_type] || '—';
  if (props.breakdown.position_type === 'phd_student' && props.breakdown.phd_year) {
    return `${base} (${props.breakdown.phd_year} курс)`;
  }
  return base;
});

const expanded = ref<Record<string, boolean>>({});
function toggle(key: string) {
  expanded.value[key] = !expanded.value[key];
}

function onWorkClick(work: IPIBreakdownWork) {
  if (props.clickable) emit('work-click', work);
}
</script>

<style scoped>
.breakdown-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.formula-card {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.formula {
  font-size: 16px;
  font-weight: 600;
  color: var(--primary);
}

.formula-desc {
  font-size: 13px;
  color: var(--text-secondary);
}

.factors-row {
  display: grid;
  grid-template-columns: 1.5fr repeat(4, 1fr);
  gap: 8px;
}

.factor-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.factor-total {
  background: var(--primary-soft, #eef2ff);
  border-color: var(--primary);
}

.factor-label {
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.factor-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.groups {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.group-block {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.group-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--bg);
  border-bottom: 1px solid var(--border);
}

.group-name {
  font-size: 14px;
  font-weight: 600;
  margin: 0;
}

.group-wi {
  font-size: 13px;
  color: var(--text-secondary);
}

.indicators-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.indicators-table th {
  text-align: center;
  padding: 8px 10px;
  background: var(--bg);
  font-size: 11px;
  color: var(--text-muted);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  border-bottom: 1px solid var(--border);
}

.indicators-table th.th-left {
  text-align: left;
}

.indicators-table td {
  padding: 10px;
  text-align: center;
  border-bottom: 1px solid var(--border);
}

.indicators-table td.th-left {
  text-align: left;
}

.ind-name {
  color: var(--text-primary);
  font-weight: 500;
}

.ind-key {
  font-size: 11px;
  color: var(--text-muted);
  font-family: monospace;
}

.cell-muted {
  color: var(--text-muted);
  font-size: 12px;
}

.contribution {
  color: var(--primary);
}

.empty-row {
  text-align: center;
  color: var(--text-muted);
  font-size: 12px;
}

.th-narrow {
  width: 32px;
  padding: 0 !important;
}

.bij-formula {
  font-family: monospace;
  font-size: 12px;
  color: var(--text-secondary);
}

.bij-formula b {
  color: var(--text-primary);
}

.indicators-table .rot {
  transform: rotate(180deg);
  transition: transform 0.2s;
}

.works-row td {
  background: var(--bg);
  padding: 8px 12px 12px 12px !important;
}

.works-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.work-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 12px;
  transition: all var(--transition);
}

.work-item.clickable {
  cursor: pointer;
}

.work-item.clickable:hover {
  border-color: var(--primary);
  background: var(--primary-soft, #eef2ff);
}

.work-arrow {
  color: var(--text-muted);
  margin-left: auto;
}

.work-title {
  flex: 1;
  color: var(--text-primary);
}

.work-points {
  color: var(--primary);
  font-weight: 600;
}

.group-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: var(--bg);
  font-size: 13px;
  color: var(--text-secondary);
  border-top: 1px solid var(--border);
}

.group-contribution {
  display: flex;
  gap: 6px;
  align-items: baseline;
}

.result {
  color: var(--primary);
  font-size: 15px;
}

.total-card {
  background: linear-gradient(135deg, var(--primary), var(--accent));
  color: #fff;
  border-radius: var(--radius-lg);
  padding: 20px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.total-formula {
  font-size: 14px;
  opacity: 0.9;
}

.total-value {
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -1px;
}
</style>
