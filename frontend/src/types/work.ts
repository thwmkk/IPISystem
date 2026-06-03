import type { Attachment } from '@/api/attachments'

// Научная работа
export interface ScientificWork {
  id: number
  employee: number
  employee_name: string
  title: string
  work_type: string
  points: number
  verified: boolean
  verification_request: number | null
  created_at: string
  publication?: Publication | null
  dissertation?: Dissertation | null
  project_participation?: ProjectParticipation | null
  software?: Software | null
  attachments?: Attachment[]
}

export interface Publication {
  title: string
  year: number
  pub_type: string
  article?: Article | null
  monograph?: Monograph | null
}

export interface Article {
  journal: string
  doi: string | null
  quartile: number | null
  is_scopus: boolean
}

export interface Monograph {
  publisher: string
  isbn: string | null
  pages_count: number | null
}

export interface Dissertation {
  stage: string
  defense_date: string | null
}

export interface ProjectParticipation {
  role: string
  budget: number | null
  start_date: string
  end_date: string | null
}

export interface Software {
  version: string
  is_commercial: boolean
}

// Организационная работа
export interface OrganizationalWork {
  id: number
  employee: number
  employee_name: string
  title: string
  work_type: string
  event_date: string
  participants_count: number | null
  points: number
  verified: boolean
  verification_request: number | null
  created_at: string
  attachments?: Attachment[]
}

// Техническая работа
export interface TechnicalWork {
  id: number
  employee: number
  employee_name: string
  title: string
  work_type: string
  registration_number: string | null
  work_date: string
  metric: string | null
  base_points: number
  points: number
  verified: boolean
  verification_request: number | null
  created_at: string
  attachments?: Attachment[]
}

// Верификация
export interface VerificationRequest {
  id: number
  work_type: string
  requester: number
  requester_name: string
  evaluator: number | null
  evaluator_name: string | null
  status: 'pending' | 'approved' | 'rejected'
  request_date: string
  comment: string | null
}

// Проекты
export interface ProjectMember {
  id: number
  project: number
  employee: number
  employee_name: string
  joined_at: string
}

export interface Project {
  id: number
  name: string
  description: string | null
  budget: number | null
  start_date: string
  end_date: string | null
  completed_at: string | null
  creator: number
  creator_name: string
  members_count?: number
  members?: ProjectMember[]
  tasks_count?: number
  created_at: string
}

// Задачи
export interface Task {
  id: number
  title: string
  description: string | null
  status: 'assigned' | 'in_progress' | 'completed' | 'overdue'
  priority: 'low' | 'medium' | 'high'
  deadline: string
  assigned_to: number | null
  assigned_to_name: string | null
  created_by: number
  created_by_name: string
  kpi_group: number | null
  work_type_key: string | null
  points: number
  project: number | null
  created_at: string
  attachments?: Attachment[]
}

// KPI
export interface KPIResult {
  id: number
  employee: number
  employee_name: string
  year: number
  quarter: number
  scientific_score: number
  organizational_score: number
  technical_score: number
  total_ipi: number
  created_at: string
}

export interface KPIWeight {
  id: number
  kpi_group: number
  group_name: string
  position: string
  group_weight: number
  weight: number
}
