import request from './index'

// 获取案例列表
export function getCaseList(params) {
  return request.get('/teaching/cases', { params })
}

// 获取案例详情
export function getCaseDetail(id) {
  return request.get(`/teaching/cases/${id}`)
}

// 创建教学案例
export function createCase(data) {
  return request.post('/teaching/cases', data)
}

// 更新教学案例
export function updateCase(id, data) {
  return request.put(`/teaching/cases/${id}`, data)
}

// 删除教学案例
export function deleteCase(id) {
  return request.delete(`/teaching/cases/${id}`)
}

// 获取模型教程列表
export function getModelTutorials(params) {
  return request.get('/teaching/tutorials', { params })
}