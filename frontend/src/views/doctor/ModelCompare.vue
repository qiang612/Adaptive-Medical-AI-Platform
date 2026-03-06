<template>
  <div class="model-compare-page">
    <PageHeader
      title="多模型对比诊断"
      description="选择多个AI模型对同一病例进行同步诊断，对比分析不同模型的诊断结果"
    />

    <el-row :gutter="20">
      <!-- 左侧：病例输入区 -->
      <el-col :span="8">
        <el-card class="common-card">
          <template #header>
            <span class="card-title">病例信息</span>
          </template>

          <el-form :model="caseForm" label-width="100px" class="case-form">
            <el-form-item label="患者姓名">
              <el-input v-model="caseForm.patient_name" placeholder="请输入患者姓名" />
            </el-form-item>
            <el-form-item label="性别">
              <el-radio-group v-model="caseForm.gender">
                <el-radio label="男">男</el-radio>
                <el-radio label="女">女</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="年龄">
              <el-input-number v-model="caseForm.age" :min="0" :max="150" style="width: 100%" />
            </el-form-item>
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
            <el-divider content-position="left">临床资料</el-divider>
            <el-form-item label="主诉">
              <el-input v-model="caseForm.chief_complaint" type="textarea" :rows="2" placeholder="请输入患者主诉" />
            </el-form-item>
            <el-form-item label="现病史">
              <el-input v-model="caseForm.history_of_present_illness" type="textarea" :rows="3" placeholder="请输入现病史" />
            </el-form-item>
            <el-form-item label="既往史">
              <el-input v-model="caseForm.past_history" type="textarea" :rows="2" placeholder="请输入既往史" />
            </el-form-item>
            <el-divider content-position="left">检查资料</el-divider>
            <el-form-item label="上传影像">
              <FileUpload
                v-model="caseForm.images"
                :limit="10"
                accept="image/*,.dcm"
                tip="支持上传影像图片或DICOM文件，最多10个"
              />
            </el-form-item>
            <el-form-item label="检验数据">
              <el-input v-model="caseForm.lab_data" type="textarea" :rows="3" placeholder="请输入检验检查数据，支持JSON格式或文本" />
            </el-form-item>
            <el-divider content-position="left">选择对比模型</el-divider>
            <el-form-item label="对比模型" required>
              <el-checkbox-group v-model="selectedModelIds">
                <el-checkbox
                  v-for="model in modelList"
                  :key="model.id"
                  :label="model.id"
                  :disabled="!model.is_active"
                >
                  {{ model.model_name }}
                  <el-tag v-if="model.is_active" type="success" size="small" style="margin-left: 8px">在线</el-tag>
                  <el-tag v-else type="info" size="small" style="margin-left: 8px">离线</el-tag>
                </el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                style="width: 100%"
                :loading="submitting"
                :disabled="selectedModelIds.length < 2"
                @click="startCompare"
              >
                <el-icon><DataAnalysis /></el-icon>
                开始对比诊断 (已选 {{ selectedModelIds.length }} 个模型)
              </el-button>
              <el-button style="width: 100%" @click="resetForm">
                <el-icon><RefreshLeft /></el-icon>
                重置
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 右侧：对比结果区 -->
      <el-col :span="16">
        <el-card class="common-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">诊断对比结果</span>
              <template v-if="compareResults.length > 0">
                <el-button type="primary" size="small" @click="exportCompareReport">
                  <el-icon><Download /></el-icon>
                  导出对比报告
                </el-button>
              </template>
            </div>
          </template>

          <div v-if="compareResults.length === 0" class="empty-result">
            <el-empty description="请在左侧输入病例信息并选择至少2个模型开始对比诊断">
              <el-button type="primary" @click="loadDemoData">加载演示数据</el-button>
            </el-empty>
          </div>

          <div v-else class="compare-result">
            <!-- 对比概览 -->
            <div class="compare-overview">
              <h4>诊断一致性分析</h4>
              <div class="consensus-chart">
                <v-chart :option="consensusOption" style="height: 280px" autoresize />
              </div>
            </div>

            <el-divider />

            <!-- 各模型结果对比 -->
            <el-row :gutter="20">
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
                      <el-tag :type="result.risk_level === '高风险' ? 'danger' : result.risk_level === '中风险' ? 'warning' : 'success'" size="large">
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
                    <el-button type="primary" link size="small" @click="viewModelDetail(result)">
                      查看完整报告
                    </el-button>
                  </div>
                </div>
              </el-col>
            </el-row>

            <el-divider />

            <!-- 详细对比表格 -->
            <div class="detail-compare-section">
              <h4>详细指标对比</h4>
              <el-table :data="compareMetrics" border class="common-table">
                <el-table-column prop="metric" label="对比指标" width="180" fixed="left" />
                <el-table-column
                  v-for="result in compareResults"
                  :key="result.model_id"
                  :label="result.model_name"
                  min-width="180"
                >
                  <template #default="{ row }">
                    <span v-if="row.key === 'risk_level'">
                      <el-tag :type="result[row.key] === '高风险' ? 'danger' : result[row.key] === '中风险' ? 'warning' : 'success'" size="small">
                        {{ result[row.key] }}
                      </el-tag>
                    </span>
                    <span v-else-if="row.key === 'risk_score'">
                      {{ result[row.key] ? (result[row.key] * 100).toFixed(2) + '%' : '-' }}
                    </span>
                    <span v-else-if="row.key === 'confidence'">
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
        </el-card>
      </el-col>
    </el-row>

    <!-- 模型详情对话框 -->
    <el-dialog v-model="detailDialogVisible" :title="currentResult?.model_name" width="800px" fullscreen>
      <ResultVisual v-if="currentResult" :result="currentResult" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
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
import { batchInference, exportCompareReport } from '@/api/inference'

use([
  CanvasRenderer,
  RadarChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const submitting = ref(false)
const modelList = ref([])
const patientList = ref([])
const selectedModelIds = ref([])
const compareResults = ref([])
const detailDialogVisible = ref(false)
const currentResult = ref(null)

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
  tooltip: {
    trigger: 'item'
  },
  legend: {
    orient: 'vertical',
    left: 'left'
  },
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
      label: {
        show: true,
        formatter: '{b}\n{d}%'
      },
      data: [
        { value: 70, name: '完全一致', itemStyle: { color: '#00B42A' } },
        { value: 20, name: '部分一致', itemStyle: { color: '#FF7D00' } },
        { value: 10, name: '不一致', itemStyle: { color: '#F53F3F' } }
      ]
    }
  ]
})

// 获取风险等级样式类
const getRiskClass = (level) => {
  const map = {
    '高风险': 'high',
    '中风险': 'medium',
    '低风险': 'low'
  }
  return map[level] || ''
}

// 加载模型列表
const loadModelList = async () => {
  try {
    modelList.value = await getActiveModels()
  } catch (error) {
    console.error('加载模型列表失败', error)
  }
}

// 加载患者列表
const loadPatientList = async () => {
  try {
    const res = await getPatients({ page: 1, page_size: 50 })
    patientList.value = res.items || res || []
  } catch (error) {
    console.error('加载患者列表失败', error)
  }
}

// 选择患者时填充信息
const onPatientSelect = (patientId) => {
  const patient = patientList.value.find(p => p.id === patientId)
  if (patient) {
    caseForm.patient_name = patient.name
    caseForm.gender = patient.gender
    caseForm.age = patient.age
  }
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
    compareResults.value = res.results || []

    // 更新一致性图表
    if (compareResults.value.length > 0) {
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

    ElMessage.success('对比诊断完成')
  } catch (error) {
    console.error('对比诊断失败', error)
    ElMessage.error('对比诊断失败')
  } finally {
    submitting.value = false
  }
}

// 重置表单
const resetForm = () => {
  Object.assign(caseForm, {
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
  selectedModelIds.value = []
  compareResults.value = []
}

// 加载演示数据
const loadDemoData = () => {
  compareResults.value = [
    {
      model_id: '1',
      model_name: '宫颈癌筛查模型 v2.0',
      status: 'completed',
      risk_level: '高风险',
      risk_score: 0.85,
      confidence: 0.92,
      duration: 12.5,
      diagnosis_summary: '根据细胞学图像分析，发现高度鳞状上皮内病变细胞，建议进一步阴道镜检查及活检。',
      primary_diagnosis: 'HSIL (CIN II-III)',
      recommendation: '建议阴道镜检查+宫颈活检',
      findings: ['发现ASC-H细胞', 'LSIL细胞', 'HPV16/18阳性可能']
    },
    {
      model_id: '2',
      model_name: '宫颈病变智能诊断系统',
      status: 'completed',
      risk_level: '高风险',
      risk_score: 0.78,
      confidence: 0.88,
      duration: 15.2,
      diagnosis_summary: '检测到异常鳞状上皮细胞，高度提示宫颈上皮内瘤变。',
      primary_diagnosis: 'HSIL',
      recommendation: '阴道镜检查，必要时LEEP术',
      findings: ['异常细胞形态', '核质比增高', '染色质异常']
    },
    {
      model_id: '3',
      model_name: '妇科肿瘤AI辅助诊断',
      status: 'completed',
      risk_level: '中风险',
      risk_score: 0.62,
      confidence: 0.75,
      duration: 10.8,
      diagnosis_summary: '发现不典型鳞状细胞，不能排除高度病变，建议结合临床。',
      primary_diagnosis: 'ASC-H',
      recommendation: 'HPV分型检测，必要时活检',
      findings: ['不典型鳞状细胞', '建议进一步检查']
    }
  ]
  ElMessage.success('演示数据已加载')
}

// 查看模型详情
const viewModelDetail = (result) => {
  currentResult.value = result
  detailDialogVisible.value = true
}

// 导出对比报告
const exportCompareReport = async () => {
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
    console.error('导出失败', error)
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

.case-form {
  width: 100%;
}

.empty-result {
  padding: 60px 0;
}

.compare-result {
  width: 100%;
}

.compare-overview h4 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px;
}

.consensus-chart {
  width: 100%;
}

.model-result-card {
  padding: 20px;
  background: var(--bg-card);
  border: 2px solid var(--border-light);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.model-result-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.model-result-card.highlight {
  border-color: var(--danger-color);
  background: linear-gradient(135deg, #FFF1F0 0%, #FFECE8 100%);
}

.model-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.model-header h5 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.risk-display {
  text-align: center;
  margin-bottom: 16px;
}

.risk-score {
  font-size: 42px;
  font-weight: 700;
  margin-bottom: 8px;
}

.risk-score.high {
  color: var(--danger-color);
}

.risk-score.medium {
  color: var(--warning-color);
}

.risk-score.low {
  color: var(--success-color);
}

.result-meta {
  display: flex;
  justify-content: space-between;
  padding: 12px;
  background: var(--bg-hover);
  border-radius: 8px;
  margin-bottom: 12px;
}

.meta-item {
  text-align: center;
}

.meta-label {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.meta-value {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.diagnosis-content h6,
.findings-section h6 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px;
}

.diagnosis-content p {
  font-size: 13px;
  color: var(--text-regular);
  line-height: 1.6;
  margin: 0;
}

.findings-section ul {
  margin: 0;
  padding-left: 16px;
}

.findings-section li {
  font-size: 13px;
  color: var(--text-regular);
  margin-bottom: 4px;
}

.card-footer {
  margin-top: 12px;
  text-align: center;
}

.detail-compare-section {
  margin-top: 20px;
}

.detail-compare-section h4 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px;
}
</style>