import request from './index'

// 获取操作日志列表
export function getOperationLogs(params) {
  return request.get('/logs/operation', { params })
}

// 获取登录日志列表
export function getLoginLogs(params) {
  return request.get('/logs/login', { params })
}

// 获取推理日志列表
export function getInferenceLogs(params) {
  return request.get('/logs/inference', { params })
}

// 导出日志
export function exportLogs(type, params) {
  return request.get(`/logs/${type}/export`, {
    params,
    responseType: 'blob'
  })
}