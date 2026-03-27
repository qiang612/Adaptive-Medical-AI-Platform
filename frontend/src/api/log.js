import request from './index'

export function getOperationLogs(params) {
  return request.get('/logs/operation', { params })
}

export function getLoginLogs(params) {
  return request.get('/logs/login', { params })
}

export function getInferenceLogs(params) {
  return request.get('/logs/inference', { params })
}

export function exportLogs(type, params) {
  return request.get(`/logs/${type}/export`, {
    params,
    responseType: 'blob'
  })
}

export function deleteOperationLogs(ids) {
  return request.delete('/logs/operation/batch', { data: { ids } })
}

export function deleteSingleOperationLog(id) {
  return request.delete(`/logs/operation/${id}`)
}

export function deleteLoginLogs(ids) {
  return request.delete('/logs/login/batch', { data: { ids } })
}

export function deleteSingleLoginLog(id) {
  return request.delete(`/logs/login/${id}`)
}

export function getLogStatsOverview() {
  return request.get('/logs/stats/overview')
}

export function getLoginTrend(days = 7) {
  return request.get('/logs/stats/login-trend', { params: { days } })
}

export function getOperationDistribution(days = 7) {
  return request.get('/logs/stats/operation-distribution', { params: { days } })
}

export function getInferenceStatusStats(days = 7) {
  return request.get('/logs/stats/inference-status', { params: { days } })
}
