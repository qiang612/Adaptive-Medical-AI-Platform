import request from './index'

// 创建诊断任务
export function createTask(formData) {
  return request.post('/tasks/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 获取我的任务列表
export function getMyTasks(params) {
  return request.get('/tasks/', { params })
}

// 获取所有任务列表（管理员）
export function getAllTasks(params) {
  return request.get('/tasks/all', { params })
}

// 获取任务状态
export function getTaskStatus(taskId) {
  return request.get(`/inference/status/${taskId}`)
}

// 获取任务详情
export function getTaskDetail(taskId) {
  return request.get(`/tasks/${taskId}`)
}

// 终止任务
export function terminateTask(taskId) {
  return request.post(`/tasks/${taskId}/terminate`)
}

// 重试失败任务
export function retryTask(taskId) {
  return request.post(`/tasks/${taskId}/retry`)
}

// 下载诊断报告
export function downloadReport(taskId) {
  return request.get(`/tasks/${taskId}/download-report`, {
    responseType: 'blob'
  })
}

// 批量删除任务
export function batchDeleteTasks(ids) {
  return request.delete('/tasks/batch', { data: { ids } })
}

// 获取任务队列统计
export function getTaskQueueStats() {
  return request.get('/tasks/queue-stats')
}

// 获取Worker节点状态
export function getWorkerNodes() {
  return request.get('/tasks/workers')
}