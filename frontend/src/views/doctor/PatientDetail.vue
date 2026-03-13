<template>
  <div class="patient-detail-page">
    <div class="page-nav">
      <el-button type="primary" link @click="goBack">
        <el-icon><ArrowLeft /></el-icon>
        返回病例列表
      </el-button>
    </div>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="common-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">患者档案</span>
              <el-button type="primary" link size="small" @click="editPatient">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
            </div>
          </template>

          <div class="patient-profile">
            <div class="profile-header">
              <el-avatar :size="80" :src="patientDetail.avatar">
                {{ patientDetail.gender === '男' ? '男' : '女' }}
              </el-avatar>
              <div class="profile-info">
                <h2 class="patient-name">{{ patientDetail.name }}</h2>
                <div class="patient-tags">
                  <el-tag size="small">{{ patientDetail.gender }}</el-tag>
                  <el-tag size="small">{{ patientDetail.age }}岁</el-tag>
                  <el-tag v-if="patientDetail.risk_level" :type="patientDetail.risk_level === '高风险' ? 'danger' : 'warning'" size="small">
                    {{ patientDetail.risk_level }}
                  </el-tag>
                </div>
              </div>
            </div>

            <el-divider />

            <el-descriptions :column="1" border size="small">
              <el-descriptions-item label="患者ID(门诊号)">
                {{ patientDetail.patient_id || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="身份证号">
                {{ patientDetail.id_card ? patientDetail.id_card.replace(/^(.{6})(.+)(.{4})$/, '$1********$3') : '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="联系电话">
                {{ patientDetail.phone ? patientDetail.phone.replace(/^(.{3})(.+)(.{4})$/, '$1****$3') : '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="电子邮箱">
                {{ patientDetail.email || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="出生日期">
                {{ patientDetail.birthday || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="家庭住址">
                {{ patientDetail.address || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="建档时间">
                {{ patientDetail.created_at }}
              </el-descriptions-item>
              <el-descriptions-item label="最后诊断时间">
                {{ patientDetail.last_diagnosis_time || '-' }}
              </el-descriptions-item>
            </el-descriptions>

            <el-divider content-position="left">既往病史</el-divider>
            <div class="medical-history">
              <p v-if="patientDetail.medical_history">{{ patientDetail.medical_history }}</p>
              <el-empty v-else description="暂无记录" :image-size="60" />
            </div>

            <el-divider content-position="left">备注</el-divider>
            <div class="remark">
              <p v-if="patientDetail.remark">{{ patientDetail.remark }}</p>
              <el-empty v-else description="暂无备注" :image-size="60" />
            </div>
          </div>
        </el-card>

        <el-card class="common-card mt-20">
          <template #header>
            <span class="card-title">诊断统计</span>
          </template>
          <el-row :gutter="16">
            <el-col :span="12">
              <div class="stat-item">
                <div class="stat-number">{{ patientDetail.diagnosis_count || 0 }}</div>
                <div class="stat-label">总诊断次数</div>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="stat-item">
                <div class="stat-number">{{ highRiskCount }}</div>
                <div class="stat-label">高风险次数</div>
              </div>
            </el-col>
          </el-row>
        </el-card>

        <el-card class="common-card mt-20">
          <template #header>
            <span class="card-title">快捷操作</span>
          </template>
          <div class="quick-actions">
            <el-button type="primary" style="width: 100%; margin-bottom: 10px" @click="startNewDiagnosis">
              <el-icon><Plus /></el-icon>
              新建诊断
            </el-button>
            <el-button type="success" style="width: 100%; margin-bottom: 10px" @click="handleExportPatientData">
              <el-icon><Download /></el-icon>
              导出患者数据
            </el-button>
            <el-button type="default" style="width: 100%" @click="printPatientInfo">
              <el-icon><Printer /></el-icon>
              打印档案
            </el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card class="common-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">诊断历史</span>
              <span class="record-count">共 {{ diagnosisHistory.length }} 条记录</span>
            </div>
          </template>

          <div v-if="diagnosisHistory.length === 0" class="empty-history">
            <el-empty description="暂无诊断记录" />
          </div>

          <div v-else class="diagnosis-timeline">
            <el-timeline>
              <el-timeline-item
                v-for="(item, index) in diagnosisHistory"
                :key="item.id"
                :timestamp="item.created_at"
                :type="item.risk_level === '高风险' ? 'danger' : item.risk_level === '中风险' ? 'warning' : 'primary'"
                placement="top"
              >
                <div class="timeline-card">
                  <div class="timeline-header">
                    <div class="timeline-title">
                      <span class="model-name">{{ item.model_name }}</span>
                      <el-tag v-if="item.risk_level" :type="item.risk_level === '高风险' ? 'danger' : item.risk_level === '中风险' ? 'warning' : 'success'" size="small">
                        {{ item.risk_level }}
                      </el-tag>
                      <StatusTag :status="item.status" size="small" />
                    </div>
                    <div class="timeline-actions">
                      <el-button type="primary" link size="small" @click="viewDiagnosisDetail(item)">
                        查看详情
                      </el-button>
                      <el-button
                        v-if="item.status === 'completed'"
                        type="success"
                        link
                        size="small"
                        @click="downloadDiagnosisReport(item)"
                      >
                        下载报告
                      </el-button>
                    </div>
                  </div>

                  <div class="timeline-content">
                    <el-descriptions :column="3" border size="small">
                      <el-descriptions-item label="患者姓名">
                        {{ item.patient_name || patientDetail.name }}
                      </el-descriptions-item>
                      <el-descriptions-item label="任务ID">
                        <el-tooltip :content="item.task_id" placement="top">
                          <span class="task-id">{{ item.task_id?.slice(0, 16) }}...</span>
                        </el-tooltip>
                      </el-descriptions-item>
                      <el-descriptions-item label="耗时">
                        {{ item.duration ? item.duration + 's' : '-' }}
                      </el-descriptions-item>
                    </el-descriptions>

                    <div v-if="item.summary" class="diagnosis-summary">
                      <h4>诊断摘要</h4>
                      <p>{{ item.summary }}</p>
                    </div>
                  </div>
                </div>
              </el-timeline-item>
            </el-timeline>
          </div>

          <Pagination
            v-if="diagnosisHistory.length > 0"
            v-model:model-value="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            @change="loadDiagnosisHistory"
          />
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="resultDialogVisible" title="诊断详情" width="900px" fullscreen>
      <ResultVisual :result="currentResult" />
    </el-dialog>

    <el-dialog v-model="patientDialogVisible" title="编辑患者" width="700px" :close-on-click-modal="false">
      <el-form :model="patientForm" :rules="patientRules" ref="patientFormRef" label-width="120px" class="common-form">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="患者ID(门诊号)">
              <el-input v-model="patientForm.patient_id" placeholder="请输入门诊/住院号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="患者姓名" prop="name">
              <el-input v-model="patientForm.name" placeholder="请输入患者姓名" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="性别" prop="gender">
              <el-radio-group v-model="patientForm.gender">
                <el-radio label="男">男</el-radio>
                <el-radio label="女">女</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="出生日期">
              <el-date-picker
                v-model="patientForm.birthday"
                type="date"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="年龄">
              <el-input-number v-model="patientForm.age" :min="0" :max="150" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="身份证号">
              <el-input v-model="patientForm.id_card" placeholder="请输入身份证号" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="联系电话">
              <el-input v-model="patientForm.phone" placeholder="请输入联系电话" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="电子邮箱">
              <el-input v-model="patientForm.email" placeholder="请输入电子邮箱" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="家庭住址">
          <el-input v-model="patientForm.address" type="textarea" :rows="2" placeholder="请输入家庭住址" />
        </el-form-item>
        <el-form-item label="既往病史">
          <el-input v-model="patientForm.medical_history" type="textarea" :rows="3" placeholder="请输入患者的既往病史、过敏史等信息" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="patientForm.remark" type="textarea" :rows="2" placeholder="请输入其他备注信息" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="patientDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="patientSaving" @click="savePatient">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import Pagination from '@/components/Pagination.vue'
import StatusTag from '@/components/StatusTag.vue'
import ResultVisual from '@/components/ResultVisual.vue'
import { getPatientDetail, getPatientDiagnosisHistory, updatePatient, exportPatientData } from '@/api/patient'
import { downloadReport } from '@/api/task'

const router = useRouter()
const route = useRoute()
const patientId = computed(() => route.params.id)

const patientDetail = ref({})
const diagnosisHistory = ref([])
const resultDialogVisible = ref(false)
const currentResult = ref(null)
const patientDialogVisible = ref(false)
const patientSaving = ref(false)
const patientFormRef = ref(null)

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 患者表单（用于编辑）
const patientForm = reactive({
  id: null,
  patient_id: '',
  name: '',
  gender: '',
  birthday: '',
  age: null,
  id_card: '',
  phone: '',
  email: '',
  address: '',
  medical_history: '',
  remark: ''
})

// 表单校验规则
const patientRules = {
  name: [{ required: true, message: '请输入患者姓名', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }]
}

// 高风险次数统计
const highRiskCount = computed(() => {
  return diagnosisHistory.value.filter(item => item.risk_level === '高风险').length
})

// 加载患者详情
const loadPatientDetail = async () => {
  try {
    patientDetail.value = await getPatientDetail(patientId.value)
    Object.assign(patientForm, patientDetail.value)
  } catch (error) {
    console.error('加载患者详情失败', error)
    ElMessage.error('加载患者详情失败')
  }
}

// 加载诊断历史
const loadDiagnosisHistory = async () => {
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    const res = await getPatientDiagnosisHistory(patientId.value, params)
    diagnosisHistory.value = res.items || res || []
    pagination.total = res.total || diagnosisHistory.value.length
  } catch (error) {
    console.error('加载诊断历史失败', error)
  }
}

// 返回上一页
const goBack = () => {
  router.push('/patient')
}

// 编辑患者
const editPatient = () => {
  Object.assign(patientForm, patientDetail.value)
  patientDialogVisible.value = true
}

// 保存患者
const savePatient = async () => {
  if (patientFormRef.value) {
    await patientFormRef.value.validate()
  }
  patientSaving.value = true
  try {
    await updatePatient(patientForm.id, patientForm)
    ElMessage.success('更新成功')
    patientDialogVisible.value = false
    loadPatientDetail()
  } catch (error) {
    console.error('保存患者失败', error)
  } finally {
    patientSaving.value = false
  }
}

// 查看诊断详情
const viewDiagnosisDetail = (item) => {
  if (item.result) {
    currentResult.value = item.result
  } else {
    currentResult.value = {
      diagnosis_summary: item.summary,
      risk_level: item.risk_level,
      risk_score: item.risk_score
    }
  }
  resultDialogVisible.value = true
}

// 下载诊断报告
const downloadDiagnosisReport = async (item) => {
  try {
    const res = await downloadReport(item.id)
    const blob = new Blob([res], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `诊断报告_${patientDetail.value.name}_${item.created_at}.pdf`
    a.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('报告下载成功')
  } catch (error) {
    console.error('下载报告失败', error)
    ElMessage.error('下载报告失败')
  }
}

// 新建诊断
const startNewDiagnosis = () => {
  router.push({
    path: '/inference',
    query: {
      patient_id: patientDetail.value.patient_id || '',
      patient_name: patientDetail.value.name || '',
      gender: patientDetail.value.gender || '',
      age: patientDetail.value.age || '',
      phone: patientDetail.value.phone || ''
    }
  })
}

// 导出患者数据
const handleExportPatientData = async () => {
  try {
    const res = await exportPatientData(patientId.value)
    const blob = new Blob([res], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `患者档案_${patientDetail.value.name}_${new Date().toLocaleDateString()}.xlsx`
    a.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出患者数据失败', error)
    ElMessage.error('导出失败')
  }
}

// 打印患者信息
const printPatientInfo = () => {
  window.print()
}

onMounted(() => {
  loadPatientDetail()
  loadDiagnosisHistory()
})
</script>

<style scoped>
.patient-detail-page {
  width: 100%;
}

.page-nav {
  margin-bottom: 20px;
}

.patient-profile {
  width: 100%;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 10px;
}

.profile-info {
  flex: 1;
}

.patient-name {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 12px;
}

.patient-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.medical-history,
.remark {
  line-height: 1.8;
  color: var(--text-regular);
  padding: 10px;
  background: var(--bg-hover);
  border-radius: 6px;
  min-height: 60px;
}

.medical-history p,
.remark p {
  margin: 0;
}

.mt-20 {
  margin-top: 20px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: var(--bg-hover);
  border-radius: 8px;
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 6px;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
}

.quick-actions {
  width: 100%;
}

.record-count {
  font-size: 14px;
  color: var(--text-secondary);
}

.empty-history {
  padding: 40px 0;
}

.diagnosis-timeline {
  width: 100%;
}

.timeline-card {
  width: 100%;
  padding: 16px;
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: 8px;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 12px;
}

.timeline-title {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.model-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.timeline-actions {
  display: flex;
  gap: 8px;
}

.timeline-content {
  width: 100%;
}

.task-id {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  color: var(--text-secondary);
  cursor: pointer;
}

.diagnosis-summary {
  margin-top: 12px;
  padding: 12px;
  background: linear-gradient(135deg, #F0F7FF 0%, #E6F4FF 100%);
  border-radius: 6px;
}

.diagnosis-summary h4 {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary-color);
  margin: 0 0 8px;
}

.diagnosis-summary p {
  font-size: 14px;
  color: var(--text-regular);
  margin: 0;
  line-height: 1.6;
}
</style>