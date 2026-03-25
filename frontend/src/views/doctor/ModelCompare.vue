<template>
  <div class="model-compare-page">
    <PageHeader
      title="多模型对比诊断"
      description="选择多个AI模型对同一病例进行同步诊断，横向对比分析不同模型的诊断结果"
    />

    <el-card class="common-card main-workflow-card">
      <el-steps :active="activeStep" finish-status="success" align-center class="compare-steps">
        <el-step title="输入病例信息" description="填写基本信息与上传资料" />
        <el-step title="选择对比模型" description="勾选需要参与对比的AI模型" />
        <el-step title="查看对比结果" description="多维度横向对比分析" />
      </el-steps>

      <el-divider />

      <div v-show="activeStep === 0" class="step-container">
        <el-form :model="caseForm" label-width="90px" class="centered-form">
          <div class="form-section-title">患者基础信息</div>
          <el-row :gutter="40">
            <el-col :span="12">
              <el-form-item label="选择患者">
                <el-select v-model="caseForm.patient_id" placeholder="从已有患者中选择" clearable filterable style="width: 100%" @change="onPatientSelect">
                  <el-option
                    v-for="patient in patientList"
                    :key="patient.id"
                    :label="`${patient.name} (${patient.gender}, ${patient.age}岁)`"
                    :value="patient.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="患者姓名">
                <el-input v-model="caseForm.patient_name" placeholder="请输入患者姓名" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="性别">
                <el-radio-group v-model="caseForm.gender">
                  <el-radio label="男">男</el-radio>
                  <el-radio label="女">女</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="年龄">
                <el-input-number v-model="caseForm.age" :min="0" :max="150" style="width: 100%" />
              </el-form-item>
            </el-col>
          </el-row>

          <div class="form-section-title" style="margin-top: 20px;">临床与检查资料</div>
          <el-row :gutter="40">
            <el-col :span="24">
              <el-form-item label="主诉">
                <el-input v-model="caseForm.chief_complaint" type="textarea" :rows="2" placeholder="请输入患者主诉" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="现病史">
                <el-input v-model="caseForm.history_of_present_illness" type="textarea" :rows="3" placeholder="请输入现病史" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="既往史">
                <el-input v-model="caseForm.past_history" type="textarea" :rows="3" placeholder="请输入既往史" />
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <el-form-item label="上传影像">
                <FileUpload
                  v-model="caseForm.images"
                  :limit="10"
                  accept="image/*,.dcm"
                  tip="支持上传影像图片或DICOM文件，最多10个"
                />
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <el-form-item label="检验数据">
                <el-input v-model="caseForm.lab_data" type="textarea" :rows="3" placeholder="请输入检验检查数据，支持JSON格式或文本" />
              </el-form-item>
            </el-col>
          </el-row>

          <div class="step-actions">
            <el-button @click="resetForm">清空表单</el-button>
            <el-button type="info" plain @click="loadDemoDataAndJump">快速加载演示数据</el-button>
            <el-button type="primary" @click="nextStep">下一步：选择对比模型</el-button>
          </div>
        </el-form>
      </div>

      <div v-show="activeStep === 1" class="step-container">
        <div class="model-select-wrapper">
          <h3 class="step-title">请选择参与对比的AI模型（至少2个）</h3>
          <el-checkbox-group v-model="selectedModelIds" class="model-checkbox-group">
            <el-row :gutter="20">
              <el-col :span="8" v-for="model in modelList" :key="model.id">
                <div class="model-option-card" :class="{'is-selected': selectedModelIds.includes(model.id), 'is-disabled': !model.is_active}">
                  <el-checkbox :label="model.id" :disabled="!model.is_active" class="model-checkbox">
                    <div class="model-info">
                      <span class="model-name">{{ model.model_name }}</span>
                      <el-tag v-if="model.is_active" type="success" size="small">在线</el-tag>
                      <el-tag v-else type="info" size="small">离线</el-tag>
                    </div>
                  </el-checkbox>
                </div>
              </el-col>
            </el-row>
          </el-checkbox-group>

          <div class="step-actions">
            <el-button @click="activeStep = 0">上一步</el-button>
            <el-button 
              type="primary" 
              size="large"
              :loading="submitting" 
              :disabled="selectedModelIds.length < 2" 
              @click="startCompare"
            >
              <el-icon><DataAnalysis /></el-icon>
              开始对比诊断 (已选 {{ selectedModelIds.length }} 个)
            </el-button>
          </div>
        </div>
      </div>

      <div v-show="submitting && activeStep !== 2" class="step-container loading-container">
        <div class="loading-wrapper">
          <el-icon class="loading-icon" :size="60"><Loading /></el-icon>
          <h3>AI模型正在分析中...</h3>
          <p class="loading-tip">已提交 {{ selectedModelIds.length }} 个模型的推理任务，请稍候</p>
          <el-progress :percentage="pollProgress" :stroke-width="10" :show-text="false" />
          <p class="progress-text">{{ pollProgressText }}</p>
        </div>
      </div>

      <div v-if="activeStep === 2 && !submitting" class="step-container result-container">
        <div class="compare-header-actions">
          <el-button type="primary" plain @click="resetForm">
            <el-icon><RefreshLeft /></el-icon> 开启新一轮对比
          </el-button>
          <el-button type="primary" @click="handleExportCompareReport">
            <el-icon><Download /></el-icon> 导出对比报告
          </el-button>
        </div>

        <div class="compare-result">
          <div class="compare-overview">
            <h4>诊断一致性分析</h4>
            <div class="consensus-chart-wrapper">
              <v-chart :option="consensusOption" style="height: 300px; width: 100%" autoresize />
            </div>
          </div>

          <el-divider />

          <h4 style="margin-bottom: 20px;">各模型诊断结论</h4>
          <el-row :gutter="20" class="model-results-row">
            <el-col
              v-for="(result, index) in compareResults"
              :key="result.model_id"
              :span="24 / compareResults.length"
            >
              <div class="model-result-card" :class="{ highlight: result.risk_level === '高风险' }">
                <div class="model-header">
                  <h5>{{ result.model_name }}</h5>
                  <StatusTag :status="result.status" />
                </div>
                <div class="risk-display">
                  <div class="risk-score" :class="getRiskClass(result.risk_level)">
                    {{ result.risk_score ? (result.risk_score * 100).toFixed(1) + '%' : '-' }}
                  </div>
                  <div class="risk-label">
                    <el-tag :type="result.risk_level === '高风险' ? 'danger' : result.risk_level === '中风险' ? 'warning' : 'success'" size="large" effect="dark">
                      {{ result.risk_level || '待诊断' }}
                    </el-tag>
                  </div>
                </div>
                <div class="result-meta">
                  <div class="meta-item">
                    <span class="meta-label">诊断耗时</span>
                    <span class="meta-value">{{ result.duration ? result.duration + 's' : '-' }}</span>
                  </div>
                  <div class="meta-item">
                    <span class="meta-label">置信度</span>
                    <span class="meta-value">{{ result.confidence ? (result.confidence * 100).toFixed(1) + '%' : '-' }}</span>
                  </div>
                </div>
                <el-divider />
                <div class="diagnosis-content">
                  <h6>诊断摘要</h6>
                  <p>{{ result.diagnosis_summary || '暂无诊断摘要' }}</p>
                </div>
                <div v-if="result.findings && result.findings.length > 0" class="findings-section">
                  <h6>阳性发现</h6>
                  <ul>
                    <li v-for="(finding, i) in result.findings" :key="i">{{ finding }}</li>
                  </ul>
                </div>
                <div class="card-footer">
                  <el-button type="primary" link @click="viewModelDetail(result)">
                    <el-icon><View /></el-icon> 查看完整报告详情
                  </el-button>
                </div>
              </div>
            </el-col>
          </el-row>

          <el-divider />

          <div class="detail-compare-section">
            <h4>多维度详细指标对比</h4>
            <el-table :data="compareMetrics" border class="common-table detail-table">
              <el-table-column prop="metric" label="对比指标" width="180" fixed="left" header-align="center" align="center" />
              <el-table-column
                v-for="result in compareResults"
                :key="result.model_id"
                :label="result.model_name"
                min-width="220"
                align="center"
              >
                <template #default="{ row }">
                  <span v-if="row.key === 'risk_level'">
                    <el-tag :type="result[row.key] === '高风险' ? 'danger' : result[row.key] === '中风险' ? 'warning' : 'success'" size="small">
                      {{ result[row.key] }}
                    </el-tag>
                  </span>
                  <span v-else-if="row.key === 'risk_score' || row.key === 'confidence'">
                    {{ result[row.key] ? (result[row.key] * 100).toFixed(2) + '%' : '-' }}
                  </span>
                  <span v-else>
                    {{ result[row.key] || '-' }}
                  </span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </div>
    </el-card>

    <el-dialog v-model="detailDialogVisible" :title="currentResult?.model_name" width="900px" fullscreen>
      <ResultVisual v-if="currentResult" :result="currentResult" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { RadarChart, PieChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import PageHeader from '@/components/PageHeader.vue'
import FileUpload from '@/components/FileUpload.vue'
import StatusTag from '@/components/StatusTag.vue'
import ResultVisual from '@/components/ResultVisual.vue'
import { getActiveModels } from '@/api/model'
import { getPatients } from '@/api/patient'
import { batchInference, exportCompareReport, getBatchStatus, getBatchResults } from '@/api/inference'

use([
  CanvasRenderer,
  RadarChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

// 步骤控制
const activeStep = ref(0)
const submitting = ref(false)

const modelList = ref([])
const patientList = ref([])
const selectedModelIds = ref([])
const compareResults = ref([])
const detailDialogVisible = ref(false)
const currentResult = ref(null)
const pollProgress = ref(0)
const pollProgressText = ref('正在初始化...')

// 病例表单
const caseForm = reactive({
  patient_name: '',
  gender: '',
  age: null,
  patient_id: '',
  chief_complaint: '',
  history_of_present_illness: '',
  past_history: '',
  images: [],
  lab_data: ''
})

// 对比指标
const compareMetrics = ref([
  { key: 'risk_level', metric: '风险等级' },
  { key: 'risk_score', metric: '风险评分' },
  { key: 'confidence', metric: '置信度' },
  { key: 'duration', metric: '诊断耗时(s)' },
  { key: 'primary_diagnosis', metric: '主要诊断' },
  { key: 'recommendation', metric: '建议' }
])

// 一致性分析图表
const consensusOption = ref({
  tooltip: { trigger: 'item' },
  legend: { orient: 'vertical', left: 'left' },
  series: [
    {
      name: '诊断一致性',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: { show: true, formatter: '{b}\n{d}%' },
      data: []
    }
  ]
})

const getRiskClass = (level) => {
  const map = { '高风险': 'high', '中风险': 'medium', '低风险': 'low' }
  return map[level] || ''
}

const loadModelList = async () => {
  try {
    modelList.value = await getActiveModels()
  } catch (error) {
    console.error('加载模型列表失败', error)
  }
}

const loadPatientList = async () => {
  try {
    const res = await getPatients({ page: 1, page_size: 50 })
    patientList.value = res.items || res || []
  } catch (error) {
    console.error('加载患者列表失败', error)
  }
}

const onPatientSelect = (patientId) => {
  const patient = patientList.value.find(p => p.id === patientId)
  if (patient) {
    caseForm.patient_name = patient.name
    caseForm.gender = patient.gender
    caseForm.age = patient.age
  }
}

// 下一步
const nextStep = () => {
  if (!caseForm.patient_name) {
    ElMessage.warning('请先填写或选择患者信息')
    return
  }
  activeStep.value = 1
}

// 开始对比诊断
const startCompare = async () => {
  if (selectedModelIds.value.length < 2) {
    ElMessage.warning('请至少选择2个模型进行对比')
    return
  }
  submitting.value = true
  
  try {
    const params = {
      model_ids: selectedModelIds.value,
      patient_info: {
        name: caseForm.patient_name,
        gender: caseForm.gender,
        age: caseForm.age,
        patient_id: caseForm.patient_id
      },
      clinical_data: {
        chief_complaint: caseForm.chief_complaint,
        history_of_present_illness: caseForm.history_of_present_illness,
        past_history: caseForm.past_history,
        lab_data: caseForm.lab_data
      },
      files: caseForm.images.map(f => f.id || f.url)
    }

    const res = await batchInference(params)
    
    if (res.tasks && res.tasks.length > 0) {
      const batchId = res.batch_id
      const taskIdList = res.tasks.map(t => t.task_id)
      const taskIdsStr = taskIdList.join(',')
      
      ElMessage.info(`已提交 ${res.total_tasks} 个推理任务，正在处理中...`)
      
      await pollBatchResults(batchId, taskIdsStr, taskIdList)
    } else {
      ElMessage.warning('没有可用的模型进行推理')
      submitting.value = false
    }
  } catch (error) {
    console.error('对比诊断失败', error)
    ElMessage.error(error.response?.data?.detail || '对比诊断失败')
    submitting.value = false
  }
}

const pollBatchResults = async (batchId, taskIdsStr, taskIdList) => {
  const maxAttempts = 60
  const pollInterval = 2000
  let attempts = 0
  
  pollProgress.value = 0
  pollProgressText.value = '正在初始化推理任务...'
  
  const poll = async () => {
    attempts++
    
    try {
      const statusRes = await getBatchStatus(batchId, taskIdsStr)
      
      const completedCount = statusRes.completed_count || 0
      const totalCount = statusRes.total_count || taskIdList.length
      pollProgress.value = Math.min(95, Math.round((completedCount / totalCount) * 100))
      pollProgressText.value = `已完成 ${completedCount}/${totalCount} 个模型推理`
      
      if (statusRes.all_completed || attempts >= maxAttempts) {
        pollProgress.value = 100
        pollProgressText.value = '正在汇总结果...'
        
        const resultsRes = await getBatchResults(batchId, taskIdsStr)
        compareResults.value = resultsRes.results || []
        
        if (compareResults.value.length > 0) {
          updateConsensusChart()
          ElMessage.success('对比诊断完成')
          activeStep.value = 2
        } else {
          ElMessage.warning('推理完成但未获取到有效结果')
        }
        submitting.value = false
      } else {
        setTimeout(poll, pollInterval)
      }
    } catch (error) {
      console.error('轮询状态失败', error)
      if (attempts >= maxAttempts) {
        ElMessage.error('推理超时，请稍后查看任务列表')
        submitting.value = false
      } else {
        pollProgressText.value = `网络异常，正在重试 (${attempts}/${maxAttempts})...`
        setTimeout(poll, pollInterval)
      }
    }
  }
  
  await poll()
}

// 更新饼图逻辑
const updateConsensusChart = () => {
  if (compareResults.value.length === 0) return
  const levels = compareResults.value.map(r => r.risk_level)
  const uniqueLevels = [...new Set(levels)]
  if (uniqueLevels.length === 1) {
    consensusOption.value.series[0].data = [
      { value: 100, name: '完全一致', itemStyle: { color: '#00B42A' } }
    ]
  } else if (uniqueLevels.length === 2) {
    consensusOption.value.series[0].data = [
      { value: 60, name: '部分一致', itemStyle: { color: '#FF7D00' } },
      { value: 40, name: '不一致', itemStyle: { color: '#F53F3F' } }
    ]
  } else {
    consensusOption.value.series[0].data = [
      { value: 30, name: '部分一致', itemStyle: { color: '#FF7D00' } },
      { value: 70, name: '不一致', itemStyle: { color: '#F53F3F' } }
    ]
  }
}

// 重置并返回第一步
const resetForm = () => {
  Object.assign(caseForm, {
    patient_name: '', gender: '', age: null, patient_id: '',
    chief_complaint: '', history_of_present_illness: '', past_history: '',
    images: [], lab_data: ''
  })
  selectedModelIds.value = []
  compareResults.value = []
  activeStep.value = 0
}

// 加载演示数据并直接跳转到结果
const loadDemoDataAndJump = () => {
  compareResults.value = [
    {
      model_id: '1', model_name: '宫颈癌筛查模型 v2.0', status: 'completed',
      risk_level: '高风险', risk_score: 0.85, confidence: 0.92, duration: 12.5,
      diagnosis_summary: '根据细胞学图像分析，发现高度鳞状上皮内病变细胞，建议进一步阴道镜检查及活检。',
      primary_diagnosis: 'HSIL (CIN II-III)', recommendation: '建议阴道镜检查+宫颈活检',
      findings: ['发现ASC-H细胞', 'LSIL细胞', 'HPV16/18阳性可能']
    },
    {
      model_id: '2', model_name: '通用病理视觉大模型', status: 'completed',
      risk_level: '高风险', risk_score: 0.78, confidence: 0.88, duration: 15.2,
      diagnosis_summary: '检测到异常鳞状上皮细胞，高度提示宫颈上皮内瘤变。',
      primary_diagnosis: 'HSIL', recommendation: '阴道镜检查，必要时LEEP术',
      findings: ['异常细胞形态', '核质比增高', '染色质异常']
    },
    {
      model_id: '3', model_name: '妇科肿瘤多模态模型', status: 'completed',
      risk_level: '中风险', risk_score: 0.62, confidence: 0.75, duration: 10.8,
      diagnosis_summary: '发现不典型鳞状细胞，不能排除高度病变，建议结合临床。',
      primary_diagnosis: 'ASC-H', recommendation: 'HPV分型检测，必要时活检',
      findings: ['不典型鳞状细胞', '建议进一步检查']
    }
  ]
  updateConsensusChart()
  ElMessage.success('演示数据已加载')
  activeStep.value = 2
}

const viewModelDetail = (result) => {
  currentResult.value = result
  detailDialogVisible.value = true
}

const handleExportCompareReport = async () => {
  try {
    const res = await exportCompareReport({ results: compareResults.value })
    const blob = new Blob([res], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `多模型对比报告_${new Date().toLocaleDateString()}.pdf`
    a.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

onMounted(() => {
  loadModelList()
  loadPatientList()
})
</script>

<style scoped>
.model-compare-page {
  width: 100%;
}

.main-workflow-card {
  min-height: calc(100vh - 180px);
}

.compare-steps {
  margin: 10px 0 30px;
  padding: 0 40px;
}

.step-container {
  padding: 20px 40px;
  animation: fadeIn 0.4s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 第一步：居中表单 */
.centered-form {
  max-width: 900px;
  margin: 0 auto;
}
.form-section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--el-color-primary);
  margin-bottom: 20px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.step-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px dashed var(--el-border-color-lighter);
}

/* 加载中状态 */
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}
.loading-wrapper {
  text-align: center;
  max-width: 400px;
}
.loading-icon {
  color: var(--el-color-primary);
  animation: spin 1.5s linear infinite;
  margin-bottom: 20px;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
.loading-wrapper h3 {
  color: var(--el-text-color-primary);
  margin-bottom: 12px;
}
.loading-tip {
  color: var(--el-text-color-secondary);
  font-size: 14px;
  margin-bottom: 24px;
}
.progress-text {
  color: var(--el-color-primary);
  font-size: 14px;
  margin-top: 12px;
}

/* 第二步：模型选择卡片 */
.model-select-wrapper {
  max-width: 900px;
  margin: 0 auto;
}
.step-title {
  text-align: center;
  margin-bottom: 30px;
  color: var(--text-primary);
}
.model-option-card {
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  padding: 16px 20px;
  margin-bottom: 20px;
  transition: all 0.3s;
}
.model-option-card:hover:not(.is-disabled) {
  border-color: var(--el-color-primary);
  box-shadow: 0 2px 12px rgba(22, 93, 255, 0.1);
}
.model-option-card.is-selected {
  background-color: var(--el-color-primary-light-9);
  border-color: var(--el-color-primary);
}
.model-option-card.is-disabled {
  background-color: var(--el-fill-color-light);
  opacity: 0.7;
}
.model-checkbox {
  width: 100%;
  height: 100%;
}
.model-info {
  display: flex;
  align-items: center;
  gap: 12px;
}
.model-name {
  font-size: 15px;
  font-weight: 500;
  white-space: normal;
  line-height: 1.4;
}

/* 第三步：对比结果 */
.result-container {
  padding: 0 20px;
}
.compare-header-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-bottom: 20px;
}
.compare-overview h4, .detail-compare-section h4 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px;
}

/* 卡片样式美化 */
.model-results-row {
  display: flex;
  align-items: stretch;
}
.model-result-card {
  height: 100%;
  padding: 24px;
  background: var(--bg-card);
  border: 1px solid var(--el-border-color-light);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
  transition: transform 0.3s ease;
  display: flex;
  flex-direction: column;
}
.model-result-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}
.model-result-card.highlight {
  border: 2px solid var(--el-color-danger-light-3);
  background: linear-gradient(180deg, var(--el-color-danger-light-9) 0%, #ffffff 100%);
}
.model-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.risk-display { text-align: center; margin-bottom: 24px; }
.risk-score { font-size: 48px; font-weight: 700; font-family: 'Arial', sans-serif; line-height: 1; margin-bottom: 12px; }
.risk-score.high { color: var(--danger-color); }
.risk-score.medium { color: var(--warning-color); }
.risk-score.low { color: var(--success-color); }

.result-meta {
  display: flex;
  justify-content: space-around;
  padding: 12px;
  background: var(--el-fill-color-light);
  border-radius: 8px;
}
.meta-item { text-align: center; }
.meta-label { font-size: 12px; color: var(--text-secondary); display: block; margin-bottom: 4px;}
.meta-value { font-size: 14px; font-weight: 600; color: var(--text-primary); }

.diagnosis-content { flex: 1; margin-top: 16px; }
.diagnosis-content h6, .findings-section h6 {
  font-size: 14px; color: var(--text-secondary); margin: 0 0 8px;
}
.diagnosis-content p { font-size: 14px; line-height: 1.6; color: var(--text-primary); }

.findings-section ul { padding-left: 18px; margin: 0; }
.findings-section li { font-size: 13px; color: var(--text-regular); margin-bottom: 6px; line-height: 1.4; }

.card-footer { margin-top: 20px; text-align: center; padding-top: 16px; border-top: 1px dashed var(--el-border-color-lighter); }

.detail-table {
  margin-top: 16px;
  font-size: 14px;
}
</style>