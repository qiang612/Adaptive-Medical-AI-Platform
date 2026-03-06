import request from './index'

// 获取激活的模型列表
export function getActiveModels() {
  return request.get('/models/active')
}

// 获取模型列表（分页）
export function getModels(params) {
  return request.get('/models/', { params })
}

// 获取模型详情
export function getModelDetail(id) {
  return request.get(`/models/${id}`)
}

// 创建模型
export function createModel(data) {
  return request.post('/models/', data)
}

// 更新模型
export function updateModel(id, data) {
  return request.put(`/models/${id}`, data)
}

// 删除模型
export function deleteModel(id) {
  return request.delete(`/models/${id}`)
}

// 切换模型启用状态
export function toggleModelStatus(id, is_active) {
  return request.patch(`/models/${id}/status`, { is_active })
}

// 获取模型版本列表
export function getModelVersions(modelId) {
  return request.get(`/models/${modelId}/versions`)
}

// 模型版本回滚
export function rollbackModelVersion(modelId, versionId) {
  return request.post(`/models/${modelId}/versions/${versionId}/rollback`)
}