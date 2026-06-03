import api from './axios'
import type { ScientificWork, OrganizationalWork, TechnicalWork, VerificationRequest } from '@/types/work'

export const worksApi = {
  // Scientific
  getScientificWorks() {
    return api.get<ScientificWork[]>('/scientific-works/')
  },
  createScientificWork(data: Partial<ScientificWork>) {
    return api.post<ScientificWork>('/scientific-works/', data)
  },
  updateScientificWork(id: number, data: Partial<ScientificWork>) {
    return api.patch<ScientificWork>(`/scientific-works/${id}/`, data)
  },
  deleteScientificWork(id: number) {
    return api.delete(`/scientific-works/${id}/`)
  },

  // Organizational
  getOrganizationalWorks() {
    return api.get<OrganizationalWork[]>('/organizational-works/')
  },
  createOrganizationalWork(data: Partial<OrganizationalWork>) {
    return api.post<OrganizationalWork>('/organizational-works/', data)
  },
  updateOrganizationalWork(id: number, data: Partial<OrganizationalWork>) {
    return api.patch<OrganizationalWork>(`/organizational-works/${id}/`, data)
  },
  deleteOrganizationalWork(id: number) {
    return api.delete(`/organizational-works/${id}/`)
  },

  // Technical
  getTechnicalWorks() {
    return api.get<TechnicalWork[]>('/technical-works/')
  },
  createTechnicalWork(data: Partial<TechnicalWork>) {
    return api.post<TechnicalWork>('/technical-works/', data)
  },
  updateTechnicalWork(id: number, data: Partial<TechnicalWork>) {
    return api.patch<TechnicalWork>(`/technical-works/${id}/`, data)
  },
  deleteTechnicalWork(id: number) {
    return api.delete(`/technical-works/${id}/`)
  },

  // Verification
  getVerificationRequests() {
    return api.get<VerificationRequest[]>('/verification-requests/')
  },
  createVerificationRequest(data: Partial<VerificationRequest>) {
    return api.post<VerificationRequest>('/verification-requests/', data)
  },
  approveVerification(id: number) {
    return api.post(`/verification-requests/${id}/approve/`)
  },
  rejectVerification(id: number, comment?: string) {
    return api.post(`/verification-requests/${id}/reject/`, { comment })
  },
  updateVerificationWork(id: number, data: any) {
    return api.post(`/verification-requests/${id}/update_work/`, data)
  },
}
