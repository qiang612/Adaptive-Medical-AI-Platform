<template>
  <div class="patient-manage-page">
    <PageHeader
      title="病例管理"
      description="管理您的患者档案，快速检索并查看患者的历史诊断记录"
    >
      <template #extra>
        <el-button type="primary" @click="openPatientDialog()">
          <el-icon><Plus /></el-icon>
          建档新患者
        </el-button>
      </template>
    </PageHeader>

    <SearchBar
      :show-keyword="true"
      keyword-placeholder="搜索姓名、身份证、手机号"
      :show-time-range="true"
      @search="handleSearch"
      @reset="handleReset"
    >
      <el-form-item label="性别">
        <el-select v-model="searchForm.gender" placeholder="全部" clearable style="width: 120px" @change="loadPatientList">
          <el-option label="男" value="男" />
          <el-option label="女" value="女" />
        </el-select>
      </el-form-item>
      <el-form-item label="年龄段">
        <el-select v-model="searchForm.ageRange" placeholder="全部" clearable style="width: 140px" @change="loadPatientList">
          <el-option label="0-18岁" value="0-18" />
          <el-option label="19-40岁" value="19-40" />
          <el-option label="41-60岁" value="41-60" />
          <el-option label="60岁以上" value="60+" />
        </el-select>
      </el-form-item>
    </SearchBar>

    <el-row :gutter="20" class="main-content">
      
      <el-col :span="9">
        <el-card class="common-card list-card" body-style="padding: 0;">
          <template #header>
            <div class="card-header">
              <span class="card-title">患者列表 ({{ pagination.total }})</span>
            </div>
          </template>
          
          <el-table 
            :data="patientList" 
            v-loading="loading" 
            highlight-current-row
            @row-click="handleRowClick"
            class="compact-table"
          >
            <el-table-column label="患者档案" min-width="180">
              <template #default="{ row }">
                <div class="patient-info-cell">
                  <el-avatar :size="40" :src="row.avatar" :class="row.gender === '男' ? 'avatar-boy' : 'avatar-girl'">
                    {{ row.name.charAt(0) }}
                  </el-avatar>
                  <div class="patient-info">
                    <div class="patient-name">{{ row.name }}</div>
                    <div class="patient-meta">
                      {{ row.gender }} | {{ row.age }}岁 | 诊断: {{ row.diagnosis_count || 0 }}次
                    </div>
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="last_diagnosis_time" label="最后就诊" width="110">
              <template #default="{ row }">
                <span class="time-text">{{ formatDate(row.last_diagnosis_time) }}</span>
              </template>
            </el-table-column>
          </el-table>
          
          <div class="pagination-wrapper">
            <el-pagination
              small
              layout="prev, pager, next"
              :total="pagination.total"
              v-model:current-page="pagination.page"
              :page-size="pagination.pageSize"
              @current-change="loadPatientList"
            />
          </div>
        </el-card>
      </el-col>

      <el-col :span="15">
        <el-card class="common-card detail-card">
          <div v-if="!selectedPatient" class="empty-state">
            <el-empty description="请在左侧点击选择患者，查看档案详情" />
          </div>
          
          <div v-else class="detail-content">
            <div class="detail-header">
              <div class="header-left">
                <h2>{{ selectedPatient.name }}</h2>
                <el-tag :type="selectedPatient.gender === '男' ? '' : 'danger'" size="small" effect="plain">
                  {{ selectedPatient.gender }}
                </el-tag>
                <el-tag type="info" size="small" effect="plain">{{ selectedPatient.age }} 岁</el-tag>
              </div>
              <div class="header-actions">
                <el-button type="primary" plain @click="viewPatientDetail(selectedPatient)">
                  <el-icon><Document /></el-icon> 完整病历
                </el-button>
                <el-button type="warning" plain @click="openPatientDialog(selectedPatient)">
                  <el-icon><Edit /></el-icon> 编辑
                </el-button>
                <el-popconfirm title="确定要删除此档案吗？" @confirm="handleDeletePatient(selectedPatient)">
                  <template #reference>
                    <el-button type="danger" plain><el-icon><Delete /></el-icon></el-button>
                  </template>
                </el-popconfirm>
              </div>
            </div>

            <el-divider />

            <el-descriptions title="基础信息" :column="2" border class="info-desc">
              <el-descriptions-item label="联系电话">{{ selectedPatient.phone || '-' }}</el-descriptions-item>
              <el-descriptions-item label="身份证号">{{ formatIdCard(selectedPatient.id_card) }}</el-descriptions-item>
              <el-descriptions-item label="出生日期">{{ selectedPatient.birthday || '-' }}</el-descriptions-item>
              <el-descriptions-item label="电子邮箱">{{ selectedPatient.email || '-' }}</el-descriptions-item>
              <el-descriptions-item label="家庭住址" :span="2">{{ selectedPatient.address || '未记录' }}</el-descriptions-item>
            </el-descriptions>

            <div class="medical-history-section">
              <div class="section-title">既往病史与备注</div>
              <el-alert
                v-if="selectedPatient.medical_history"
                :title="selectedPatient.medical_history"
                type="warning"
                :closable="false"
                class="history-alert"
              />
              <p v-else class="no-data-text">暂无既往病史记录</p>
              
              <div class="remark-box" v-if="selectedPatient.remark">
                <strong>备注：</strong>{{ selectedPatient.remark }}
              </div>
            </div>
            
            <div class="quick-action-box">
              <el-button type="primary" size="large" style="width: 100%" @click="$router.push({ path: '/inference', query: { patient_id: selectedPatient.id } })">
                <el-icon><VideoPlay /></el-icon> 为该患者发起新AI诊断
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="patientDialogVisible" :title="isEdit ? '编辑患者' : '新增患者'" width="700px" :close-on-click-modal="false">
      <el-form :model="patientForm" :rules="patientRules" ref="patientFormRef" label-width="120px" class="common-form">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="患者姓名" prop="name">
              <el-input v-model="patientForm.name" placeholder="请输入姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性别" prop="gender">
              <el-radio-group v-model="patientForm.gender">
                <el-radio label="男">男</el-radio>
                <el-radio label="女">女</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="出生日期" prop="birthday">
              <el-date-picker v-model="patientForm.birthday" type="date" style="width: 100%" value-format="YYYY-MM-DD" @change="calculateAge" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="年龄">
              <el-input-number v-model="patientForm.age" :min="0" :max="150" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="身份证号" prop="idCard">
              <el-input v-model="patientForm.id_card" placeholder="请输入身份证号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" prop="phone">
              <el-input v-model="patientForm.phone" placeholder="请输入联系电话" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="家庭住址">
          <el-input v-model="patientForm.address" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="既往病史">
          <el-input v-model="patientForm.medical_history" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="patientForm.remark" type="textarea" :rows="2" />
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
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import PageHeader from '@/components/PageHeader.vue'
import SearchBar from '@/components/SearchBar.vue'
import { getPatients, createPatient, updatePatient, deletePatient } from '@/api/patient'

const router = useRouter()
const loading = ref(false)
const patientList = ref([])
const selectedPatient = ref(null) // 记录当前选中的患者

const patientDialogVisible = ref(false)
const isEdit = ref(false)
const patientSaving = ref(false)
const patientFormRef = ref(null)

const searchForm = reactive({
  keyword: '', timeRange: [], gender: '', ageRange: ''
})

const pagination = reactive({ page: 1, pageSize: 10, total: 0 })

const patientForm = reactive({
  id: null, name: '', gender: '', birthday: '', age: null, id_card: '', phone: '', email: '', address: '', medical_history: '', remark: ''
})

const patientRules = {
  name: [{ required: true, message: '请输入患者姓名', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }]
}

// 格式化工具
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return dayjs(dateStr).format('YYYY-MM-DD')
}
const formatIdCard = (id) => {
  if (!id) return '-'
  return id.replace(/^(.{6})(.+)(.{4})$/, '$1********$3')
}

const calculateAge = () => {
  if (patientForm.birthday) {
    patientForm.age = dayjs().diff(dayjs(patientForm.birthday), 'year')
  }
}

const loadPatientList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page, page_size: pagination.pageSize,
      keyword: searchForm.keyword, gender: searchForm.gender
    }
    // 处理年龄段等逻辑...
    const res = await getPatients(params)
    patientList.value = res.items || res || []
    pagination.total = res.total || patientList.value.length
    
    // 如果列表有数据且当前未选中，默认选中第一项
    if (patientList.value.length > 0 && !selectedPatient.value) {
      selectedPatient.value = patientList.value[0]
    }
  } catch (error) {
    ElMessage.error('加载患者列表失败')
  } finally {
    loading.value = false
  }
}

// 点击左侧行，更新右侧详情
const handleRowClick = (row) => {
  selectedPatient.value = row
}

const handleSearch = (params) => {
  Object.assign(searchForm, params)
  pagination.page = 1
  selectedPatient.value = null // 重新搜索后清空右侧
  loadPatientList()
}

const handleReset = () => {
  Object.keys(searchForm).forEach(key => searchForm[key] = Array.isArray(searchForm[key]) ? [] : '')
  pagination.page = 1
  selectedPatient.value = null
  loadPatientList()
}

const openPatientDialog = (row = null) => {
  isEdit.value = !!row
  Object.assign(patientForm, row || {
    id: null, name: '', gender: '', birthday: '', age: null, id_card: '', phone: '', address: '', medical_history: '', remark: ''
  })
  patientDialogVisible.value = true
}

const savePatient = async () => {
  await patientFormRef.value.validate()
  patientSaving.value = true
  try {
    if (isEdit.value) await updatePatient(patientForm.id, patientForm)
    else await createPatient(patientForm)
    ElMessage.success('保存成功')
    patientDialogVisible.value = false
    loadPatientList()
  } finally {
    patientSaving.value = false
  }
}

const handleDeletePatient = async (row) => {
  try {
    await deletePatient(row.id)
    ElMessage.success('删除成功')
    if (selectedPatient.value?.id === row.id) selectedPatient.value = null
    loadPatientList()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const viewPatientDetail = (row) => {
  router.push(`/patient/${row.id}`)
}

onMounted(() => loadPatientList())
</script>

<style scoped>
.patient-manage-page {
  width: 100%;
}

/* 左侧紧凑列表样式 */
.list-card {
  height: calc(100vh - 280px);
  display: flex;
  flex-direction: column;
}

.compact-table :deep(.el-table__body tr) {
  cursor: pointer;
}

.patient-info-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}
.avatar-boy { background-color: #409EFF; }
.avatar-girl { background-color: #F56C6C; }

.patient-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}
.patient-meta {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
}
.time-text {
  font-size: 12px;
  color: #909399;
}

.pagination-wrapper {
  padding: 12px;
  display: flex;
  justify-content: center;
  border-top: 1px solid #ebeef5;
}

/* 右侧详情面板样式 */
.detail-card {
  height: calc(100vh - 280px);
  overflow-y: auto;
}

.empty-state {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.header-left h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.info-desc {
  margin-bottom: 24px;
}

.section-title {
  font-size: 15px;
  font-weight: bold;
  margin-bottom: 12px;
  position: relative;
  padding-left: 10px;
}
.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 2px;
  bottom: 2px;
  width: 4px;
  background-color: var(--el-color-primary);
  border-radius: 2px;
}

.history-alert {
  margin-bottom: 16px;
}
.no-data-text {
  color: #999;
  font-size: 13px;
}
.remark-box {
  background-color: #f8f9fa;
  padding: 12px;
  border-radius: 4px;
  font-size: 13px;
  color: #606266;
}

.quick-action-box {
  margin-top: 32px;
  padding-top: 20px;
  border-top: 1px dashed #e4e7ed;
}
</style>