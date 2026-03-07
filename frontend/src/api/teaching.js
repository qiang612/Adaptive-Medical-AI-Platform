import request from './index'

// 获取教学案例列表
export function getTeachingCases(params) {
  return request.get('/teaching/cases', { params })
}

// 获取教学案例详情
export function getTeachingCaseDetail(id) {
  return request.get(`/teaching/cases/${id}`)
}

// 创建教学案例
export function createTeachingCase(data) {
  return request.post('/teaching/cases', data)
}

// 更新教学案例
export function updateTeachingCase(id, data) {
  return request.put(`/teaching/cases/${id}`, data)
}

// 删除教学案例
export function deleteTeachingCase(id) {
  return request.delete(`/teaching/cases/${id}`)
}