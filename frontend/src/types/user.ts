export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access: string
  refresh: string
  user: UserInfo
}

export interface UserInfo {
  id: number
  email: string
  employee_id: number | null
  full_name: string
  role: string | null
  position: string | null
  department: string | null
}

export type PositionType =
  | 'junior_researcher'
  | 'researcher'
  | 'senior_researcher'
  | 'engineer'
  | 'phd_student'
  | 'head'

export const POSITION_TYPE_LABELS: Record<PositionType, string> = {
  junior_researcher: 'м.н.с.',
  researcher: 'н.с.',
  senior_researcher: 'с.н.с.',
  engineer: 'инженер',
  phd_student: 'аспирант',
  head: 'руководитель отдела',
}

export interface Employee {
  id: number
  full_name: string
  email: string
  position: string
  position_type: PositionType
  phd_year: number | null
  age: number
  experience: number
  academic_degree: string | null
  department: number
  department_name: string
  role: number
  role_name: string
  user: number | null
}

export interface Department {
  id: number
  department_name: string
  department_short_name: string
}

export interface UserRole {
  id: number
  role_name: string
}
