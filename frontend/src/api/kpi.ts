import api from './axios'
import type { KPIResult } from '@/types/work'
import type { Employee, PositionType } from '@/types/user'

export interface KPIGroupData {
  id: number
  name: string
  group_weight: number
  department: number
  indicators: KPIIndicatorData[]
}

export type EntityKind = 'none' | 'article' | 'monograph' | 'dissertation' | 'software' | 'grant'

export interface KPIIndicatorData {
  id: number
  kpi_group: number
  name: string
  work_type_key: string
  weight: number
  entity_kind: EntityKind
}

export interface KPIGroupWeightData {
  id: number
  kpi_group: number
  group_name: string
  position_type: PositionType
  phd_year: number | null
  weight: number
}

export interface IPIBreakdownWork {
  id: number
  title: string
  points: number
  kind: 'scientific' | 'organizational' | 'technical'
}

export interface IPIBreakdownIndicator {
  name: string
  work_type_key: string
  w_base: number
  k_age: number
  k_exp: number
  k_phd: number
  wij: number
  bij: number
  contribution: number
  works: IPIBreakdownWork[]
}

export interface IPIBreakdownGroup {
  group_id: number
  name: string
  wi: number
  sum_inner: number
  contribution: number
  indicators: IPIBreakdownIndicator[]
}

export interface IPIBreakdown {
  employee_id: number
  employee_name: string
  position_type: PositionType
  phd_year: number | null
  year: number
  quarter: number
  factors: { k_age: number; k_exp: number; k_phd: number; k_total: number }
  groups: IPIBreakdownGroup[]
  scientific_score: number
  organizational_score: number
  technical_score: number
  total_ipi: number
}

export interface DepartmentStatsRow {
  employee_id: number
  full_name: string
  position: string
  position_type: PositionType
  phd_year: number | null
  works_total: number
  works_verified: number
  works_pending: number
  tasks_total: number
  tasks_completed: number
  tasks_overdue: number
  projects_count: number
  total_ipi: number
  activity_score: number
}

export interface DepartmentStats {
  period: 'month' | 'quarter' | 'year'
  year: number
  start_date: string
  end_date: string
  rows: DepartmentStatsRow[]
}

export interface EmployeeDetailWork {
  id: number
  kind: 'scientific' | 'organizational' | 'technical'
  category: string
  title: string
  work_type: string
  points: number
  verified: boolean
  date: string | null
}

export interface EmployeeDetailTask {
  id: number
  title: string
  status: 'assigned' | 'in_progress' | 'completed' | 'overdue'
  priority: 'low' | 'medium' | 'high'
  deadline: string
  project_id: number | null
  project_name: string | null
  points: number
}

export interface EmployeeDetailProject {
  id: number
  name: string
  start_date: string | null
  end_date: string | null
  completed_at: string | null
}

export interface EmployeeDetail {
  employee_id: number
  full_name: string
  works: EmployeeDetailWork[]
  tasks: EmployeeDetailTask[]
  tasks_completed: number
  tasks_overdue: number
  projects: EmployeeDetailProject[]
}

export const kpiApi = {
  getResults() {
    return api.get<KPIResult[]>('/kpi-results/')
  },
  calculateIpi(employeeId: number, year: number, quarter: number) {
    return api.post<KPIResult>('/ipi/calculate/', {
      employee_id: employeeId, year, quarter,
    })
  },
  recalculateAll(year?: number, quarter?: number) {
    return api.post<KPIResult[]>('/ipi/recalculate-all/', { year, quarter })
  },
  getBreakdown(params: { employee_id?: number; year?: number; quarter?: number }) {
    return api.get<IPIBreakdown>('/ipi/breakdown/', { params })
  },

  // Groups
  getGroups(params?: { department?: number }) {
    return api.get<KPIGroupData[]>('/kpi-groups/', { params })
  },
  updateGroup(id: number, data: Partial<KPIGroupData>) {
    return api.patch<KPIGroupData>(`/kpi-groups/${id}/`, data)
  },

  // Indicators
  updateIndicator(id: number, data: Partial<KPIIndicatorData>) {
    return api.patch<KPIIndicatorData>(`/kpi-indicators/${id}/`, data)
  },
  createIndicator(data: Partial<KPIIndicatorData>) {
    return api.post<KPIIndicatorData>('/kpi-indicators/', data)
  },
  deleteIndicator(id: number) {
    return api.delete(`/kpi-indicators/${id}/`)
  },

  // Group weights (Wi per position_type / phd_year)
  getGroupWeights(params: {
    position_type?: PositionType
    phd_year?: number | null
    department?: number
  }) {
    const q: any = {}
    if (params.position_type) q.position_type = params.position_type
    if (params.phd_year !== undefined) {
      q.phd_year = params.phd_year === null ? 'null' : params.phd_year
    }
    if (params.department) q.department = params.department
    return api.get<KPIGroupWeightData[]>('/kpi-group-weights/', { params: q })
  },
  upsertGroupWeight(data: {
    kpi_group: number
    position_type: PositionType
    phd_year: number | null
    weight: number
  }) {
    return api.post<KPIGroupWeightData>('/kpi-group-weights/upsert/', data)
  },
}

export const departmentApi = {
  getStats(params: {
    period: 'month' | 'quarter' | 'year'
    year?: number
    month?: number
    quarter?: number
  }) {
    return api.get<DepartmentStats>('/department/stats/', { params })
  },
  getEmployeeDetail(employeeId: number, params: {
    period: 'month' | 'quarter' | 'year'
    year?: number
    month?: number
    quarter?: number
  }) {
    return api.get<EmployeeDetail>(
      `/department/employee/${employeeId}/details/`,
      { params },
    )
  },
  downloadReport(params: {
    period: 'month' | 'quarter' | 'year'
    year?: number
    month?: number
    quarter?: number
    format: 'excel' | 'word'
  }) {
    return api.get('/department/report/', {
      params,
      responseType: 'blob',
    })
  },
  downloadEmployeeReport(employeeId: number, params: {
    period: 'month' | 'quarter' | 'year'
    year?: number
    month?: number
    quarter?: number
    format: 'excel' | 'word'
  }) {
    return api.get(`/department/employee/${employeeId}/report/`, {
      params,
      responseType: 'blob',
    })
  },
}

export const employeesApi = {
  getAll() {
    return api.get<Employee[]>('/employees/')
  },
  getById(id: number) {
    return api.get<Employee>(`/employees/${id}/`)
  },
  create(data: Partial<Employee>) {
    return api.post('/employees/', data)
  },
  update(id: number, data: Partial<Employee>) {
    return api.patch(`/employees/${id}/`, data)
  },
  delete(id: number) {
    return api.delete(`/employees/${id}/`)
  },
}
