import request from './index'

// 获取患者列表
export function getPatients(params) {
  return request.get('/patients/', { params })
}

// 获取患者详情
export function getPatientDetail(id) {
  return request.get(`/patients/${id}`)
}

// 创建患者档案
export function createPatient(data) {
  return request.post('/patients/', data)
}

// 更新患者档案
export function updatePatient(id, data) {
  return request.put(`/patients/${id}`, data)
}

// 删除患者档案
export function deletePatient(id) {
  return request.delete(`/patients/${id}`)
}

// 获取患者诊断历史
export function getPatientDiagnosisHistory(patientId, params) {
  return request.get(`/patients/${patientId}/diagnosis`, { params })
}

// 导出患者数据
export function exportPatientData(id) {
  return request.get(`/patients/${id}/export`, {
    responseType: 'blob'
  })
}