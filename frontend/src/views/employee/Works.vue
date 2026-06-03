<template>
  <div class="works-page">
    <!-- Header -->
    <div class="page-top">
      <div>
        <h2 class="page-title">Мои работы</h2>
        <p class="page-subtitle">Управление научными, организационными и техническими работами</p>
      </div>
      <el-button type="primary" @click="openAddDialog">
        <el-icon><Plus /></el-icon>
        Добавить работу
      </el-button>
    </div>

    <!-- Filters -->
    <div class="filters-card">
      <div class="filters-row">
        <el-input
          v-model="filters.search"
          placeholder="Поиск по названию"
          clearable
          style="width: 240px"
        />
        <el-select v-model="filters.type" placeholder="Категория" clearable style="width: 180px">
          <el-option label="Научная" value="scientific" />
          <el-option label="Техническая" value="technical" />
          <el-option label="Организационная" value="organizational" />
        </el-select>
        <el-select v-model="filters.status" placeholder="Статус" clearable style="width: 160px">
          <el-option label="Подтверждено" value="verified" />
          <el-option label="Ожидает" value="pending" />
        </el-select>
        <el-date-picker
          v-model="filters.dateRange"
          type="daterange"
          range-separator="—"
          start-placeholder="Дата от"
          end-placeholder="до"
          value-format="YYYY-MM-DD"
          style="width: 280px"
        />
        <el-button @click="resetFilters">Сбросить</el-button>
      </div>
    </div>

    <!-- Table -->
    <div class="table-card">
      <el-table
        ref="tableRef"
        :data="filteredWorks"
        stripe
        style="width: 100%"
        v-loading="loading"
        :row-class-name="rowClass"
      >
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="expanded-panel">
              <!-- Details section -->
              <div class="details-section">
                <h4 class="section-subtitle">Информация</h4>
                <div class="details-grid">
                  <div class="detail">
                    <div class="detail-label">Название</div>
                    <div class="detail-value">{{ row.title }}</div>
                  </div>
                  <div class="detail">
                    <div class="detail-label">Категория</div>
                    <div class="detail-value">{{ getCategoryLabel(row._category) }}</div>
                  </div>
                  <div class="detail">
                    <div class="detail-label">Тип работы</div>
                    <div class="detail-value">{{ row.work_type || '—' }}</div>
                  </div>
                  <div v-if="auth.isManager || row.verified" class="detail">
                    <div class="detail-label">Баллы</div>
                    <div class="detail-value">{{ row.points }}</div>
                  </div>
                  <div class="detail">
                    <div class="detail-label">Дата</div>
                    <div class="detail-value">{{ row._date || '—' }}</div>
                  </div>
                  <div class="detail">
                    <div class="detail-label">Статус</div>
                    <el-tag size="small" :type="row.verified ? 'success' : 'warning'" effect="light">
                      {{ row.verified ? 'Подтверждено' : 'Ожидает верификации' }}
                    </el-tag>
                  </div>
                  <!-- Type-specific -->
                  <template v-if="row._category === 'organizational'">
                    <div class="detail" v-if="row.participants_count !== null">
                      <div class="detail-label">Кол-во участников</div>
                      <div class="detail-value">{{ row.participants_count }}</div>
                    </div>
                  </template>
                  <template v-if="row._category === 'technical'">
                    <div class="detail" v-if="row.registration_number">
                      <div class="detail-label">Номер регистрации</div>
                      <div class="detail-value">{{ row.registration_number }}</div>
                    </div>
                    <div class="detail" v-if="row.metric">
                      <div class="detail-label">Метрика</div>
                      <div class="detail-value">{{ row.metric }}</div>
                    </div>
                  </template>
                  <template v-if="row._category === 'scientific' && row.publication">
                    <div class="detail">
                      <div class="detail-label">Публикация</div>
                      <div class="detail-value">
                        {{ row.publication.title }} ({{ row.publication.year }})
                      </div>
                    </div>
                    <div v-if="row.publication.article" class="detail">
                      <div class="detail-label">Журнал</div>
                      <div class="detail-value">
                        {{ row.publication.article.journal }}
                        <span v-if="row.publication.article.quartile">
                          · Q{{ row.publication.article.quartile }}
                        </span>
                        <span v-if="row.publication.article.is_scopus">· Scopus</span>
                      </div>
                    </div>
                    <div v-if="row.publication.monograph" class="detail">
                      <div class="detail-label">Издательство</div>
                      <div class="detail-value">{{ row.publication.monograph.publisher }}</div>
                    </div>
                  </template>
                  <template v-if="row._category === 'scientific' && row.dissertation">
                    <div class="detail">
                      <div class="detail-label">Диссертация</div>
                      <div class="detail-value">
                        {{ row.dissertation.stage }}
                        <span v-if="row.dissertation.defense_date">
                          · {{ row.dissertation.defense_date }}
                        </span>
                      </div>
                    </div>
                  </template>
                  <template v-if="row._category === 'scientific' && row.project_participation">
                    <div class="detail">
                      <div class="detail-label">Участие в проекте</div>
                      <div class="detail-value">{{ row.project_participation.role }}</div>
                    </div>
                  </template>
                  <template v-if="row._category === 'scientific' && row.software">
                    <div class="detail">
                      <div class="detail-label">ПО</div>
                      <div class="detail-value">
                        v{{ row.software.version }}
                        <span v-if="row.software.is_commercial">· Коммерческое</span>
                      </div>
                    </div>
                  </template>
                </div>

                <div v-if="!row.verified" class="edit-actions">
                  <el-button size="small" type="primary" plain @click="openEditWork(row)">
                    <el-icon><Edit /></el-icon>
                    Редактировать
                  </el-button>
                </div>
              </div>

              <!-- Attachments section -->
              <div class="attachments-panel">
                <div class="attachments-header">
                  <span class="attachments-title">
                    <el-icon><Paperclip /></el-icon>
                    Прикреплённые файлы ({{ row.attachments?.length || 0 }})
                  </span>
                  <el-upload
                    :show-file-list="false"
                    :before-upload="(file: File) => { handleRowUpload(row, file); return false }"
                    multiple
                  >
                    <el-button size="small" :disabled="row.verified">
                      <el-icon><Paperclip /></el-icon>
                      Добавить файл
                    </el-button>
                  </el-upload>
                </div>
                <div v-if="!row.attachments?.length" class="attachments-empty">
                  Файлов пока нет
                </div>
                <div v-else class="attachments-list">
                  <div v-for="att in row.attachments" :key="att.id" class="attachment-item">
                    <el-icon><Document /></el-icon>
                    <a :href="att.url || undefined" target="_blank" class="attachment-name">
                      {{ att.original_name }}
                    </a>
                    <span class="attachment-size">{{ formatSize(att.size) }}</span>
                    <el-button
                      size="small"
                      circle
                      type="danger"
                      :disabled="row.verified"
                      @click="removeAttachment(row, att.id)"
                    >
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="title" label="Название" min-width="200">
          <template #default="{ row }">
            <span class="work-title">{{ row.title }}</span>
          </template>
        </el-table-column>

        <el-table-column label="Категория" width="160">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row._category)" effect="light">
              {{ getCategoryLabel(row._category) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="work_type" label="Тип" width="200" />

        <el-table-column label="Дата" width="120">
          <template #default="{ row }">
            {{ row._date }}
          </template>
        </el-table-column>

        <el-table-column prop="points" label="Баллы" width="100" align="center">
          <template #default="{ row }">
            <span v-if="auth.isManager || row.verified" class="points-badge">
              {{ row.points }}
            </span>
            <span v-else class="text-muted">—</span>
          </template>
        </el-table-column>

        <el-table-column label="Статус" width="140">
          <template #default="{ row }">
            <el-tag :type="row.verified ? 'success' : 'warning'" effect="light">
              {{ row.verified ? 'Подтверждено' : 'Ожидает' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="Файлы" width="90" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.attachments?.length" type="info" effect="light">
              <el-icon><Paperclip /></el-icon>
              {{ row.attachments.length }}
            </el-tag>
            <span v-else class="text-muted">—</span>
          </template>
        </el-table-column>

        <el-table-column label="" width="80" align="right">
          <template #default="{ row }">
            <el-button size="small" circle type="danger" @click="deleteWork(row)" :disabled="row.verified">
              <el-icon><Delete /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- ============ Add/Edit Work Dialog (unified) ============ -->
    <el-dialog
      v-model="showWorkDialog"
      :title="isEditing ? 'Редактировать работу' : 'Добавить работу'"
      width="640px"
      destroy-on-close
    >
      <el-form :model="form" label-position="top">

        <!-- Category (только при создании; при редактировании категорию не меняем) -->
        <el-form-item label="Категория работы">
          <el-radio-group v-model="form.category" :disabled="isEditing" @change="onCategoryChange">
            <el-radio-button value="scientific">Научная</el-radio-button>
            <el-radio-button value="technical">Техническая</el-radio-button>
            <el-radio-button value="organizational">Организационная</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <!-- ======== НАУЧНАЯ ======== -->
        <template v-if="form.category === 'scientific'">
          <el-form-item label="Тип работы">
            <el-select
              v-model="form.scientificTypeKey"
              style="width: 100%"
              placeholder="Выберите показатель из настроек KPI"
              :disabled="isEditing"
            >
              <el-option
                v-for="ind in scientificIndicators"
                :key="ind.id"
                :label="ind.name"
                :value="ind.work_type_key"
              />
            </el-select>
            <div v-if="scientificIndicators.length === 0" class="hint-text">
              В группе «Научные» нет показателей. Добавьте их в «Настройка весов».
            </div>
            <div v-if="isEditing" class="hint-text" style="color: var(--text-secondary)">
              Тип работы нельзя изменить при редактировании. Если нужно — удалите работу и создайте заново.
            </div>
            <div v-else-if="selectedSciEntityKind !== 'none' && form.scientificTypeKey" class="hint-text" style="color: var(--text-secondary)">
              Дополнительные поля для типа «{{ entityKindLabel(selectedSciEntityKind) }}» ниже.
            </div>
          </el-form-item>

          <el-form-item label="Название">
            <el-input v-model="form.title" />
          </el-form-item>

          <el-form-item v-if="auth.isManager" label="Баллы">
            <el-input-number v-model="form.points" :min="0" :step="0.5" />
          </el-form-item>

          <!-- Статья -->
          <template v-if="selectedSciEntityKind === 'article'">
            <el-form-item label="Год публикации">
              <el-input-number v-model="form.pubYear" :min="1900" :max="2100" />
            </el-form-item>
            <el-form-item label="Журнал">
              <el-input v-model="form.journal" />
            </el-form-item>
            <div class="form-row">
              <el-form-item label="DOI">
                <el-input v-model="form.doi" />
              </el-form-item>
              <el-form-item label="Квартиль">
                <el-select v-model="form.quartile" clearable style="width: 100%">
                  <el-option label="Q1" :value="1" />
                  <el-option label="Q2" :value="2" />
                  <el-option label="Q3" :value="3" />
                  <el-option label="Q4" :value="4" />
                </el-select>
              </el-form-item>
            </div>
            <el-form-item>
              <el-checkbox v-model="form.isScopus">Индексирована в Scopus/WoS</el-checkbox>
            </el-form-item>
          </template>

          <!-- Монография -->
          <template v-if="selectedSciEntityKind === 'monograph'">
            <el-form-item label="Год публикации">
              <el-input-number v-model="form.pubYear" :min="1900" :max="2100" />
            </el-form-item>
            <el-form-item label="Издательство">
              <el-input v-model="form.publisher" />
            </el-form-item>
            <div class="form-row">
              <el-form-item label="ISBN">
                <el-input v-model="form.isbn" />
              </el-form-item>
              <el-form-item label="Кол-во страниц">
                <el-input-number v-model="form.pagesCount" :min="0" />
              </el-form-item>
            </div>
          </template>

          <!-- Диссертация -->
          <template v-if="selectedSciEntityKind === 'dissertation'">
            <el-form-item label="Этап">
              <el-input v-model="form.stage" placeholder="Защита к.н., Защита д.н., ..." />
            </el-form-item>
            <el-form-item label="Дата защиты">
              <el-date-picker v-model="form.defenseDate" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </template>

          <!-- Участие в проекте/гранте -->
          <template v-if="selectedSciEntityKind === 'grant'">
            <el-form-item label="Роль в проекте">
              <el-input v-model="form.projectRole" placeholder="Руководитель, Участник, ..." />
            </el-form-item>
            <el-form-item label="Бюджет (руб.)">
              <el-input-number v-model="form.budget" :min="0" :step="100000" style="width: 100%" />
            </el-form-item>
            <div class="form-row">
              <el-form-item label="Дата начала">
                <el-date-picker v-model="form.startDate" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
              </el-form-item>
              <el-form-item label="Дата завершения">
                <el-date-picker v-model="form.endDate" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
              </el-form-item>
            </div>
          </template>

          <!-- ПО -->
          <template v-if="selectedSciEntityKind === 'software'">
            <el-form-item label="Версия">
              <el-input v-model="form.version" />
            </el-form-item>
            <el-form-item>
              <el-checkbox v-model="form.isCommercial">Коммерческое ПО</el-checkbox>
            </el-form-item>
          </template>
        </template>

        <!-- ======== ОРГАНИЗАЦИОННАЯ ======== -->
        <template v-if="form.category === 'organizational'">
          <el-form-item label="Тип работы">
            <el-select v-model="form.orgType" style="width: 100%" placeholder="Выберите показатель">
              <el-option
                v-for="ind in orgIndicators"
                :key="ind.id"
                :label="ind.name"
                :value="ind.work_type_key"
              />
            </el-select>
            <div v-if="orgIndicators.length === 0" class="hint-text">
              В группе «Организационные» нет показателей. Добавьте их в «Настройка весов».
            </div>
          </el-form-item>
          <el-form-item label="Название">
            <el-input v-model="form.title" />
          </el-form-item>
          <div class="form-row">
            <el-form-item label="Дата мероприятия">
              <el-date-picker v-model="form.eventDate" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Кол-во участников">
              <el-input-number v-model="form.participantsCount" :min="0" />
            </el-form-item>
          </div>
          <el-form-item v-if="auth.isManager" label="Баллы">
            <el-input-number v-model="form.points" :min="0" :step="0.5" />
          </el-form-item>
        </template>

        <!-- ======== ТЕХНИЧЕСКАЯ ======== -->
        <template v-if="form.category === 'technical'">
          <el-form-item label="Тип работы">
            <el-select v-model="form.techType" style="width: 100%" placeholder="Выберите показатель">
              <el-option
                v-for="ind in techIndicators"
                :key="ind.id"
                :label="ind.name"
                :value="ind.work_type_key"
              />
            </el-select>
            <div v-if="techIndicators.length === 0" class="hint-text">
              В группе «Технические» нет показателей. Добавьте их в «Настройка весов».
            </div>
          </el-form-item>
          <el-form-item label="Название">
            <el-input v-model="form.title" />
          </el-form-item>
          <div class="form-row">
            <el-form-item label="Дата">
              <el-date-picker v-model="form.workDate" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Номер регистрации">
              <el-input v-model="form.registrationNumber" />
            </el-form-item>
          </div>
          <el-form-item label="Метрика">
            <el-input v-model="form.metric" />
          </el-form-item>
          <el-form-item v-if="auth.isManager" label="Баллы">
            <el-input-number v-model="form.points" :min="0" :step="0.5" />
          </el-form-item>
        </template>

        <!-- ======== ПРИЛОЖЕНИЯ (только при создании) ======== -->
        <el-form-item v-if="!isEditing" label="Прикрепить файлы (опционально)">
          <el-upload
            :show-file-list="false"
            :before-upload="(file) => { queueFile(file); return false }"
            multiple
          >
            <el-button>
              <el-icon><Paperclip /></el-icon>
              Выбрать файлы
            </el-button>
          </el-upload>
          <div v-if="pendingFiles.length" class="pending-files">
            <div v-for="(f, i) in pendingFiles" :key="i" class="pending-file">
              <el-icon><Document /></el-icon>
              <span>{{ f.name }}</span>
              <span class="attachment-size">{{ formatSize(f.size) }}</span>
              <el-button size="small" circle type="danger" @click="removePending(i)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </el-form-item>

      </el-form>

      <template #footer>
        <el-button @click="showWorkDialog = false">Отмена</el-button>
        <el-button type="primary" @click="submitWork" :loading="saving">
          {{ isEditing ? 'Сохранить' : 'Добавить' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted, nextTick, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { Plus, Delete, Document, Edit } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { worksApi } from "@/api/works";
import { kpiApi, type KPIGroupData, type KPIIndicatorData, type EntityKind } from "@/api/kpi";
import { attachmentsApi, type Attachment, type AttachmentTarget } from "@/api/attachments";
import { useAuthStore } from "@/store/auth";
import { Paperclip } from "@element-plus/icons-vue";

const route = useRoute();
const router = useRouter();
const tableRef = ref<any>(null);
const highlightedRowKey = ref<string | null>(null);

function rowClass({ row }: { row: any }) {
  return highlightedRowKey.value === `${row._category}-${row.id}` ? 'row-highlight' : '';
}

async function focusWorkFromQuery() {
  const wid = route.query.work_id;
  const wkind = route.query.work_kind;
  if (!wid || !wkind) return;
  const id = Number(wid);
  const target = allWorks.value.find(w => w.id === id && w._category === wkind);
  if (!target) return;
  highlightedRowKey.value = `${target._category}-${target.id}`;
  await nextTick();
  tableRef.value?.toggleRowExpansion?.(target, true);
  setTimeout(() => { highlightedRowKey.value = null; }, 2500);
  router.replace({ query: { ...route.query, work_id: undefined, work_kind: undefined } });
}

watch(() => route.query.work_id, () => { focusWorkFromQuery(); });

const auth = useAuthStore();
const loading = ref(false);
const saving = ref(false);
const showWorkDialog = ref(false);
const isEditing = ref(false);
const editRow = ref<any>(null);

// Dynamic KPI groups/indicators (loaded from "Настройка весов")
const kpiGroups = ref<KPIGroupData[]>([]);

function findGroup(pattern: RegExp): KPIGroupData | undefined {
  return kpiGroups.value.find(g => pattern.test(g.name.toLowerCase()));
}

const scientificIndicators = computed<KPIIndicatorData[]>(
  () => findGroup(/науч/)?.indicators || []
);
const orgIndicators = computed<KPIIndicatorData[]>(
  () => findGroup(/организ/)?.indicators || []
);
const techIndicators = computed<KPIIndicatorData[]>(
  () => findGroup(/техн/)?.indicators || []
);

interface WorkRow {
  id: number
  title: string
  work_type: string
  points: number
  verified: boolean
  _category: string
  _date: string
}

const allWorks = ref<WorkRow[]>([]);
const filters = ref({
  type: "",
  status: "",
  search: "",
  dateRange: null as [string, string] | null,
});

const filteredWorks = computed(() => {
  let list = allWorks.value;
  if (filters.value.type) list = list.filter((w) => w._category === filters.value.type);
  if (filters.value.status === "verified") list = list.filter((w) => w.verified);
  else if (filters.value.status === "pending") list = list.filter((w) => !w.verified);
  if (filters.value.search) {
    const q = filters.value.search.toLowerCase();
    list = list.filter((w) => w.title?.toLowerCase().includes(q));
  }
  if (filters.value.dateRange) {
    const [from, to] = filters.value.dateRange;
    list = list.filter((w) => {
      if (!w._date) return false;
      if (from && w._date < from) return false;
      if (to && w._date > to) return false;
      return true;
    });
  }
  return list;
});

const initialForm = () => ({
  category: "scientific" as string,
  title: "",
  points: 0,
  // Scientific
  scientificTypeKey: "",
  pubYear: new Date().getFullYear(),
  journal: "",
  doi: "",
  quartile: null as number | null,
  isScopus: false,
  publisher: "",
  isbn: "",
  pagesCount: null as number | null,
  stage: "",
  defenseDate: "",
  projectRole: "",
  budget: null as number | null,
  startDate: "",
  endDate: "",
  version: "",
  isCommercial: false,
  // Organizational
  orgType: "",
  eventDate: "",
  participantsCount: null as number | null,
  // Technical
  techType: "",
  workDate: "",
  registrationNumber: "",
  metric: "",
});

const form = reactive(initialForm());
const pendingFiles = ref<File[]>([]);

function onCategoryChange() {
  Object.assign(form, { ...initialForm(), category: form.category });
}

// Lookup: work_type_key -> entity_kind. Reads from all loaded KPI groups.
function entityKindFor(workTypeKey: string): EntityKind {
  if (!workTypeKey) return 'none';
  for (const g of kpiGroups.value) {
    for (const ind of g.indicators) {
      if (ind.work_type_key === workTypeKey) return ind.entity_kind || 'none';
    }
  }
  return 'none';
}

// Принудительный entity_kind для режима редактирования —
// если у работы уже есть подобъект (например, publication.article),
// показываем соответствующие поля даже если справочник KPI ещё не загружен
// или индикатор не найден (для работ, созданных из задачи).
const forcedSciEntityKind = ref<EntityKind | ''>('');

const selectedSciEntityKind = computed<EntityKind>(
  () => forcedSciEntityKind.value || entityKindFor(form.scientificTypeKey)
);

function entityKindLabel(k: EntityKind): string {
  return {
    none: 'без подформы',
    article: 'Статья',
    monograph: 'Монография',
    dissertation: 'Диссертация',
    software: 'ПО',
    grant: 'Участие в проекте',
  }[k] || k;
}

function openAddDialog() {
  Object.assign(form, initialForm());
  pendingFiles.value = [];
  isEditing.value = false;
  editRow.value = null;
  forcedSciEntityKind.value = '';
  showWorkDialog.value = true;
}

function queueFile(file: File) {
  pendingFiles.value.push(file);
}

function removePending(i: number) {
  pendingFiles.value.splice(i, 1);
}

function formatSize(bytes: number) {
  if (!bytes) return '';
  if (bytes < 1024) return `${bytes} Б`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} КБ`;
  return `${(bytes / 1024 / 1024).toFixed(1)} МБ`;
}

function targetFor(category: string, workId: number): AttachmentTarget {
  if (category === 'scientific') return { scientific_work: workId };
  if (category === 'organizational') return { organizational_work: workId };
  return { technical_work: workId };
}

async function uploadPendingFiles(category: string, workId: number) {
  for (const f of pendingFiles.value) {
    try {
      await attachmentsApi.upload(f, targetFor(category, workId));
    } catch {
      ElMessage.warning(`Не удалось загрузить ${f.name}`);
    }
  }
}

async function handleRowUpload(row: any, file: File) {
  try {
    const { data } = await attachmentsApi.upload(file, targetFor(row._category, row.id));
    if (!row.attachments) row.attachments = [];
    row.attachments.push(data);
    ElMessage.success('Файл загружен');
  } catch {
    ElMessage.error(`Не удалось загрузить ${file.name}`);
  }
}

async function removeAttachment(row: any, attId: number) {
  try {
    await ElMessageBox.confirm('Удалить файл?', 'Подтверждение', { type: 'warning' });
  } catch { return; }
  try {
    await attachmentsApi.remove(attId);
    row.attachments = row.attachments.filter((a: Attachment) => a.id !== attId);
    ElMessage.success('Файл удалён');
  } catch {
    ElMessage.error('Ошибка при удалении файла');
  }
}

async function fetchWorks() {
  loading.value = true;
  try {
    const [sw, ow, tw] = await Promise.all([
      worksApi.getScientificWorks(),
      worksApi.getOrganizationalWorks(),
      worksApi.getTechnicalWorks(),
    ]);
    allWorks.value = [
      ...sw.data.map((w: any) => ({ ...w, _category: "scientific", _date: w.created_at?.slice(0, 10) || '' })),
      ...ow.data.map((w: any) => ({ ...w, _category: "organizational", _date: w.event_date || '' })),
      ...tw.data.map((w: any) => ({ ...w, _category: "technical", _date: w.work_date || '' })),
    ];
    await focusWorkFromQuery();
  } catch {
    ElMessage.error("Не удалось загрузить работы");
  } finally {
    loading.value = false;
  }
}

// Build the scientific work payload from current form state.
// Includes the relevant nested subtype block based on selected indicator's entity_kind.
function buildScientificPayload(): any {
  const payload: any = {
    title: form.title,
    work_type: form.scientificTypeKey,
    points: form.points,
    employee: auth.employeeId,
  };
  const kind = selectedSciEntityKind.value;
  if (kind === 'article') {
    payload.publication = {
      title: form.title,
      year: form.pubYear,
      pub_type: 'article',
      article: {
        journal: form.journal,
        doi: form.doi || null,
        quartile: form.quartile,
        is_scopus: form.isScopus,
      },
    };
  } else if (kind === 'monograph') {
    payload.publication = {
      title: form.title,
      year: form.pubYear,
      pub_type: 'monograph',
      monograph: {
        publisher: form.publisher,
        isbn: form.isbn || null,
        pages_count: form.pagesCount,
      },
    };
  } else if (kind === 'dissertation') {
    payload.dissertation = {
      stage: form.stage,
      defense_date: form.defenseDate || null,
    };
  } else if (kind === 'grant') {
    payload.project_participation = {
      role: form.projectRole,
      budget: form.budget,
      start_date: form.startDate,
      end_date: form.endDate || null,
    };
  } else if (kind === 'software') {
    payload.software = {
      version: form.version,
      is_commercial: form.isCommercial,
    };
  }
  return payload;
}

async function submitWork() {
  if (!form.title) { ElMessage.warning("Введите название"); return; }

  if (form.category === 'scientific' && !form.scientificTypeKey) {
    ElMessage.warning("Выберите тип работы из настроек KPI");
    return;
  }
  if (form.category === 'organizational' && !form.orgType) {
    ElMessage.warning("Выберите тип работы");
    return;
  }
  if (form.category === 'technical' && !form.techType) {
    ElMessage.warning("Выберите тип работы");
    return;
  }

  saving.value = true;
  try {
    let savedId: number | null = null;

    if (form.category === "scientific") {
      const payload = buildScientificPayload();
      if (isEditing.value && editRow.value) {
        const { data } = await worksApi.updateScientificWork(editRow.value.id, payload);
        savedId = data.id;
      } else {
        const { data } = await worksApi.createScientificWork(payload);
        savedId = data.id;
      }
    } else if (form.category === "organizational") {
      const payload: any = {
        title: form.title,
        work_type: form.orgType,
        event_date: form.eventDate,
        participants_count: form.participantsCount,
        points: form.points,
        employee: auth.employeeId,
      };
      if (isEditing.value && editRow.value) {
        const { data } = await worksApi.updateOrganizationalWork(editRow.value.id, payload);
        savedId = data.id;
      } else {
        const { data } = await worksApi.createOrganizationalWork(payload);
        savedId = data.id;
      }
    } else {
      const payload: any = {
        title: form.title,
        work_type: form.techType,
        work_date: form.workDate,
        registration_number: form.registrationNumber || null,
        metric: form.metric || null,
        base_points: form.points,
        points: form.points,
        employee: auth.employeeId,
      };
      if (isEditing.value && editRow.value) {
        const { data } = await worksApi.updateTechnicalWork(editRow.value.id, payload);
        savedId = data.id;
      } else {
        const { data } = await worksApi.createTechnicalWork(payload);
        savedId = data.id;
      }
    }

    if (!isEditing.value && savedId && pendingFiles.value.length) {
      await uploadPendingFiles(form.category, savedId);
    }
    showWorkDialog.value = false;
    ElMessage.success(isEditing.value ? "Работа обновлена" : "Работа добавлена");
    pendingFiles.value = [];
    fetchWorks();
  } catch (e: any) {
    ElMessage.error(e.response?.data ? JSON.stringify(e.response.data) : "Ошибка при сохранении");
  } finally {
    saving.value = false;
  }
}

// Open dialog in edit mode — prefill all subtype-specific fields from the row.
function openEditWork(row: any) {
  Object.assign(form, initialForm());
  form.category = row._category;
  form.title = row.title || '';
  form.points = row.points ?? 0;
  forcedSciEntityKind.value = '';

  if (row._category === 'scientific') {
    form.scientificTypeKey = row.work_type || '';
    if (row.publication) {
      form.pubYear = row.publication.year || new Date().getFullYear();
      if (row.publication.article) {
        const a = row.publication.article;
        form.journal = a.journal || '';
        form.doi = a.doi || '';
        form.quartile = a.quartile ?? null;
        form.isScopus = !!a.is_scopus;
        forcedSciEntityKind.value = 'article';
      } else if (row.publication.monograph) {
        const m = row.publication.monograph;
        form.publisher = m.publisher || '';
        form.isbn = m.isbn || '';
        form.pagesCount = m.pages_count ?? null;
        forcedSciEntityKind.value = 'monograph';
      }
    }
    if (row.dissertation) {
      form.stage = row.dissertation.stage || '';
      form.defenseDate = row.dissertation.defense_date || '';
      forcedSciEntityKind.value = 'dissertation';
    }
    if (row.project_participation) {
      form.projectRole = row.project_participation.role || '';
      form.budget = row.project_participation.budget ?? null;
      form.startDate = row.project_participation.start_date || '';
      form.endDate = row.project_participation.end_date || '';
      forcedSciEntityKind.value = 'grant';
    }
    if (row.software) {
      form.version = row.software.version || '';
      form.isCommercial = !!row.software.is_commercial;
      forcedSciEntityKind.value = 'software';
    }
  } else if (row._category === 'organizational') {
    form.orgType = row.work_type || '';
    form.eventDate = row.event_date || '';
    form.participantsCount = row.participants_count ?? null;
  } else if (row._category === 'technical') {
    form.techType = row.work_type || '';
    form.workDate = row.work_date || '';
    form.registrationNumber = row.registration_number || '';
    form.metric = row.metric || '';
  }

  isEditing.value = true;
  editRow.value = row;
  pendingFiles.value = [];
  showWorkDialog.value = true;
}

async function deleteWork(row: WorkRow) {
  try {
    await ElMessageBox.confirm("Удалить эту работу?", "Подтверждение", { type: "warning" });
  } catch { return; }

  try {
    if (row._category === "scientific") await worksApi.deleteScientificWork(row.id);
    else if (row._category === "organizational") await worksApi.deleteOrganizationalWork(row.id);
    else await worksApi.deleteTechnicalWork(row.id);
    ElMessage.success("Работа удалена");
    fetchWorks();
  } catch {
    ElMessage.error("Ошибка при удалении");
  }
}

const resetFilters = () => {
  filters.value = { type: "", status: "", search: "", dateRange: null };
};

const getCategoryLabel = (c: string) =>
  ({ scientific: "Научная", organizational: "Организационная", technical: "Техническая" }[c]);
const getTypeTag = (c: string) =>
  ({ scientific: "primary", organizational: "success", technical: "warning" }[c] as any);

async function fetchKpiGroups() {
  try {
    const { data } = await kpiApi.getGroups();
    kpiGroups.value = data;
  } catch (_) {}
}

onMounted(() => {
  fetchWorks();
  fetchKpiGroups();
});
</script>

<style scoped>
.works-page {
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

.filters-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 16px 20px;
}

.filters-row {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.table-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.work-title {
  font-weight: 500;
  color: var(--text-primary);
}

.points-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-soft);
  color: var(--primary);
  font-weight: 600;
  font-size: 13px;
  padding: 4px 12px;
  border-radius: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.hint-text {
  font-size: 12px;
  color: var(--warning);
  margin-top: 4px;
}

.text-muted {
  color: var(--text-secondary);
}

.expanded-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px 20px;
}

.details-section {
  background: var(--bg, #f8fafc);
  border-radius: var(--radius-md, 8px);
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.section-subtitle {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 10px 16px;
}

.detail {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.detail-label {
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.detail-value {
  font-size: 13px;
  color: var(--text-primary);
  font-weight: 500;
}

.edit-actions {
  display: flex;
  justify-content: flex-end;
}

.attachments-panel {
  padding: 12px 16px;
  background: var(--bg, #fafafa);
  border-radius: var(--radius-md, 8px);
}

.attachments-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.attachments-title {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  color: var(--text-primary);
}

.attachments-empty {
  font-size: 13px;
  color: var(--text-secondary);
  padding: 8px 0;
}

.attachments-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: var(--bg-card, #fff);
  border: 1px solid var(--border);
  border-radius: 6px;
}

.attachment-name {
  flex: 1;
  color: var(--primary);
  text-decoration: none;
  word-break: break-all;
}

.attachment-name:hover {
  text-decoration: underline;
}

.attachment-size {
  font-size: 12px;
  color: var(--text-secondary);
}

.pending-files {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 8px;
  width: 100%;
}

.pending-file {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: var(--bg-soft, #fafafa);
  border: 1px dashed var(--border);
  border-radius: 6px;
  font-size: 13px;
}

.pending-file > span:first-of-type {
  flex: 1;
}

:deep(.row-highlight) {
  background-color: var(--primary-soft, #eef2ff) !important;
  animation: pulse 1.2s ease-in-out infinite alternate;
}

@keyframes pulse {
  from { background-color: var(--primary-soft, #eef2ff) !important; }
  to { background-color: transparent !important; }
}
</style>
