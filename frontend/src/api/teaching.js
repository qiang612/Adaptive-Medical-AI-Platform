import request from './index'

export function getTeachingCases(params) {
  return request.get('/teaching/cases', { params })
}

export function getTeachingCaseDetail(id) {
  return request.get(`/teaching/cases/${id}`)
}

export function createTeachingCase(data) {
  return request.post('/teaching/cases', data)
}

export function updateTeachingCase(id, data) {
  return request.put(`/teaching/cases/${id}`, data)
}

export function deleteTeachingCase(id) {
  return request.delete(`/teaching/cases/${id}`)
}

export function starTeachingCase(id) {
  return request.post(`/teaching/cases/${id}/star`)
}

export function getTeachingStats() {
  return request.get('/teaching/stats')
}