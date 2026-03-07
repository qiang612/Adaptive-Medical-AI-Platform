import request from './index'

// 获取系统配置
export function getSystemConfig() {
  return request.get('/system/config')
}

// 更新系统配置
export function updateSystemConfig(data) {
  return request.put('/system/config', data)
}

// 获取存储配置
export function getStorageConfig() {
  return request.get('/system/storage-config')
}

// 更新存储配置
export function updateStorageConfig(data) {
  return request.put('/system/storage-config', data)
}

// 获取通知模板
export function getNoticeTemplates() {
  return request.get('/system/notice-templates')
}

// 更新通知模板
export function updateNoticeTemplate(id, data) {
  return request.put(`/system/notice-templates/${id}`, data)
}

// 测试邮件通知
export function testEmailNotice(data) {
  return request.post('/system/test-email', data)
}

// 新增通知模板
export function createNoticeTemplate(data) {
  return request.post('/system/notice-templates', data)
}

// 删除通知模板
export function deleteNoticeTemplate(id) {
  return request.delete(`/system/notice-templates/${id}`)
}