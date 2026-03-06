import request from './index'

// 获取个人诊断统计（医生）
export function getPersonalStats(params) {
  return request.get('/statistics/personal', { params })
}

// 获取病种分布统计
export function getDiseaseStats(params) {
  return request.get('/statistics/disease', { params })
}

// 获取模型调用统计
export function getModelCallStats(params) {
  return request.get('/statistics/model-call', { params })
}

// 获取平台全局统计（管理员）
export function getPlatformStats() {
  return request.get('/statistics/platform')
}

// 获取平台趋势统计
export function getTrendStats(params) {
  return request.get('/statistics/trend', { params })
}