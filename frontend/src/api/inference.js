import request from './index'

/**
 * 提交批量推理/模型对比任务
 * @param {FormData} data 包含文件和所选模型的表单数据
 */
export function batchInference(data) {
  return request.post('/inference/batch', data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

/**
 * 导出模型对比报告
 * @param {Object} data 包含需要导出的任务ID或结果数据
 */
export function exportCompareReport(data) {
  return request.post('/inference/export-compare', data, {
    responseType: 'blob' // 告诉 axios 返回的是二进制文件流，用于下载
  })
}

/**
 * 获取单次推理结果 (备用补充，防止其他页面也会用到)
 * @param {string|number} taskId 任务ID
 */
export function getInferenceResult(taskId) {
  return request.get(`/inference/result/${taskId}`)
}