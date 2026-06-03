import api from './axios'
import type { Task } from '@/types/work'

export const tasksApi = {
  getTasks() {
    return api.get<Task[]>('/tasks/')
  },
  createTask(data: Partial<Task>) {
    return api.post<Task>('/tasks/', data)
  },
  updateTask(id: number, data: Partial<Task>) {
    return api.patch<Task>(`/tasks/${id}/`, data)
  },
  deleteTask(id: number) {
    return api.delete(`/tasks/${id}/`)
  },
  takeTask(id: number) {
    return api.post<Task>(`/tasks/${id}/take/`)
  },
  startTask(id: number) {
    return api.post<Task>(`/tasks/${id}/start/`)
  },
  completeTask(id: number) {
    return api.post<Task>(`/tasks/${id}/complete/`)
  },
}
