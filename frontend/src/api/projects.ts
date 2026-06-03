import api from './axios'
import type { Project, Task } from '@/types/work'

export const projectsApi = {
  getProjects() {
    return api.get<Project[]>('/projects/')
  },
  getProject(id: number) {
    return api.get<Project>(`/projects/${id}/`)
  },
  createProject(data: Partial<Project>) {
    return api.post<Project>('/projects/', data)
  },
  updateProject(id: number, data: Partial<Project>) {
    return api.patch<Project>(`/projects/${id}/`, data)
  },
  deleteProject(id: number) {
    return api.delete(`/projects/${id}/`)
  },
  addMember(projectId: number, employeeId: number) {
    return api.post(`/projects/${projectId}/add_member/`, { employee_id: employeeId })
  },
  removeMember(projectId: number, employeeId: number) {
    return api.post(`/projects/${projectId}/remove_member/`, { employee_id: employeeId })
  },
  getProjectTasks(projectId: number) {
    return api.get<Task[]>(`/projects/${projectId}/tasks/`)
  },
  completeProject(projectId: number, payload: {
    kpi_group: number
    work_type_key: string
    total_points: number
    distribution: Record<number, number>
  }) {
    return api.post<{ status: string; completed_at: string; works_created: number }>(
      `/projects/${projectId}/complete_project/`,
      payload,
    )
  },
}
