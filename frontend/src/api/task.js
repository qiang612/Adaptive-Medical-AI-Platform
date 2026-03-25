import request from './index'

export function createTask(formData) {
  return request.post('/tasks/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export function getMyTasks(params) {
  return request.get('/tasks/', { params })
}

export function getAllTasks(params) {
  return request.get('/tasks/all', { params })
}

export function getTaskStatus(taskId) {
  return request.get(`/inference/status/${taskId}`)
}

export function getTaskDetail(taskId) {
  return request.get(`/tasks/${taskId}`)
}

export function retryTask(taskId) {
  return request.post(`/tasks/${taskId}/retry`)
}

export function cancelTask(taskId) {
  return request.post(`/tasks/${taskId}/cancel`)
}

export const terminateTask = cancelTask

export function downloadReport(taskId) {
  return request.get(`/tasks/${taskId}/download-report`, {
    responseType: 'blob'
  })
}

export function batchDeleteTasks(ids) {
  return request.delete('/tasks/batch', { data: { ids } })
}

export function getTaskQueueStats() {
  return request.get('/tasks/queue-stats')
}

export function getWorkerNodes() {
  return request.get('/tasks/workers')
}