import api from './axios'

export interface Attachment {
  id: number
  file: string
  url: string | null
  original_name: string
  size: number
  uploaded_at: string
  uploaded_by: number | null
  uploaded_by_name: string | null
  scientific_work: number | null
  organizational_work: number | null
  technical_work: number | null
  task: number | null
}

export type AttachmentTarget =
  | { scientific_work: number }
  | { organizational_work: number }
  | { technical_work: number }
  | { task: number }

export const attachmentsApi = {
  list(params: Partial<Record<'scientific_work' | 'organizational_work' | 'technical_work' | 'task', number>>) {
    return api.get<Attachment[]>('/attachments/', { params })
  },
  upload(file: File, target: AttachmentTarget) {
    const form = new FormData()
    form.append('file', file)
    for (const [k, v] of Object.entries(target)) {
      form.append(k, String(v))
    }
    return api.post<Attachment>('/attachments/', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  remove(id: number) {
    return api.delete(`/attachments/${id}/`)
  },
}
