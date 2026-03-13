// frontend/src/api/inference.js
import request from './index'

/**
 * 提交批量推理/模型对比任务
 * @param {Object} data 包含文件和所选模型的表单数据
 */
export function batchInference(data) {
  // 修复：移除错误的 multipart/form-data 请求头，因为这里传的是纯 JSON 对象
  return request.post('/inference/batch', data)
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
 * 获取单次推理结果
 * @param {string|number} taskId 任务ID
 */
export function getInferenceResult(taskId) {
  return request.get(`/inference/result/${taskId}`)
}