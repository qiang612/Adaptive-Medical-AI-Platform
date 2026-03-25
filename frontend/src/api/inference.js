// frontend/src/api/inference.js
import request from './index'

/**
 * 提交批量推理/模型对比任务
 * @param {Object} data 包含文件和所选模型的表单数据
 * @returns {Object} { batch_id, tasks: [{task_id, model_id, model_name, status}] }
 */
export function batchInference(data) {
  return request.post('/inference/batch', data)
}

/**
 * 查询批量推理任务状态
 * @param {string} batchId 批次ID
 * @param {string} taskIds 任务ID列表（逗号分隔）
 */
export function getBatchStatus(batchId, taskIds) {
  return request.get(`/inference/batch/${batchId}/status`, {
    params: { task_ids: taskIds }
  })
}

/**
 * 获取批量推理的最终结果
 * @param {string} batchId 批次ID
 * @param {string} taskIds 任务ID列表（逗号分隔）
 */
export function getBatchResults(batchId, taskIds) {
  return request.get(`/inference/batch/${batchId}/results`, {
    params: { task_ids: taskIds }
  })
}

/**
 * 导出模型对比报告
 * @param {Object} data 包含需要导出的任务ID或结果数据
 */
export function exportCompareReport(data) {
  return request.post('/inference/export-compare', data, {
    responseType: 'blob'
  })
}

/**
 * 获取单次推理结果
 * @param {string|number} taskId 任务ID
 */
export function getInferenceResult(taskId) {
  return request.get(`/inference/result/${taskId}`)
}