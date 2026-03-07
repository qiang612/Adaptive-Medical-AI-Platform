<template>
  <div class="patient-manage-page">
    <PageHeader
      title="病例管理"
      description="管理您的患者档案，查看诊断历史，支持新增、编辑、删除患者信息"
    >
      <template #extra>
        <el-button type="primary" @click="openPatientDialog">
          <el-icon><Plus /></el-icon>
          新增患者
        </el-button>
      </template>
    </PageHeader>

    <!-- 搜索筛选区 -->
    <SearchBar
      :show-keyword="true"
      keyword-placeholder="搜索患者姓名、身份证号、手机号"
      :show-time-range="true"
      @search="handleSearch"
      @reset="handleReset"
    >
      <el-form-item label="性别">
        <el-select v-model="searchForm.gender" placeholder="全部" clearable style="width: 160px" @change="loadPatientList">
          <el-option label="男" value="男" />
          <el-option label="女" value="女" />
        </el-select>
      </el-form-item>
      <el-form-item label="年龄段">
        <el-select v-model="searchForm.ageRange" placeholder="全部" clearable style="width: 160px" @change="loadPatientList">
          <el-option label="0-18岁" value="0-18" />
          <el-option label="19-40岁" value="19-40" />
          <el-option label="41-60岁" value="41-60" />
          <el-option label="60岁以上" value="60+" />
        </el-select>
      </el-form-item>
    </SearchBar>

    <!-- 患者列表 -->
    <el-card class="common-card">
      <el-table :data="patientList" border class="common-table" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="患者信息" width="200">
          <template #default="{ row }">
            <div class="patient-info-cell">
              <el-avatar :size="40" :src="row.avatar">
                {{ row.gender === '男' ? '男' : '女' }}
              </el-avatar>
              <div class="patient-info">
                <div class="patient-name">{{ row.name }}</div>
                <div class="patient-meta">
                  {{ row.gender }} · {{ row.age }}岁
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="id_card" label="身份证号" width="180" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.id_card ? row.id_card.replace(/^(.{6})(.+)(.{4})$/, '$1********$3') : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="联系电话" width="130">
          <template #default="{ row }">
            {{ row.phone ? row.phone.replace(/^(.{3})(.+)(.{4})$/, '$1****$3') : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="diagnosis_count" label="诊断次数" width="100" sortable>
          <template #default="{ row }">
            <el-tag type="primary" size="small">{{ row.diagnosis_count || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_diagnosis_time" label="最后诊断时间" width="180">
          <template #default="{ row }">
            {{ row.last_diagnosis_time || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="建档时间" width="180" />
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewPatientDetail(row)">
              详情
            </el-button>
            <el-button type="primary" link size="small" @click="openPatientDialog(row)">
              编辑
            </el-button>
            <el-popconfirm
              title="确定要删除这个患者档案吗？删除后相关诊断记录将保留但不再关联此患者。"
              @confirm="handleDeletePatient(row)"
            >
              <template #reference>
                <el-button type="danger" link size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <Pagination
        v-model:model-value="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        @change="loadPatientList"
      />
    </el-card>

    <!-- 患者编辑对话框 -->
    <el-dialog v-model="patientDialogVisible" :title="isEdit ? '编辑患者' : '新增患者'" width="700px" :close-on-click-modal="false">
      <el-form :model="patientForm" :rules="patientRules" ref="patientFormRef" label-width="120px" class="common-form">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="患者姓名" prop="name">
              <el-input v-model="patientForm.name" placeholder="请输入患者姓名" />
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
              <el-date-picker
                v-model="patientForm.birthday"
                type="date"
                style="width: 100%"
                value-format="YYYY-MM-DD"
                @change="calculateAge"
              />
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
        <el-form-item label="电子邮箱">
          <el-input v-model="patientForm.email" placeholder="请输入电子邮箱" />
        </el-form-item>
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
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import PageHeader from '@/components/PageHeader.vue'
import SearchBar from '@/components/SearchBar.vue'
import Pagination from '@/components/Pagination.vue'
import { getPatients, createPatient, updatePatient, deletePatient } from '@/api/patient'

const router = useRouter()
const loading = ref(false)
const patientList = ref([])
const patientDialogVisible = ref(false)
const isEdit = ref(false)
const patientSaving = ref(false)
const patientFormRef = ref(null)

// 搜索表单
const searchForm = reactive({
  keyword: '',
  timeRange: [],
  gender: '',
  ageRange: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 患者表单
const patientForm = reactive({
  id: null,
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
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  idCard: [
    { pattern: /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/, message: '请输入正确的身份证号', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

// 根据出生日期计算年龄
const calculateAge = () => {
  if (patientForm.birthday) {
    const birth = dayjs(patientForm.birthday)
    const now = dayjs()
    patientForm.age = now.diff(birth, 'year')
  }
}

// 加载患者列表
const loadPatientList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      keyword: searchForm.keyword,
      gender: searchForm.gender
    }
    if (searchForm.timeRange && searchForm.timeRange.length === 2) {
      params.start_time = searchForm.timeRange[0]
      params.end_time = searchForm.timeRange[1]
    }
    if (searchForm.ageRange) {
      const [min, max] = searchForm.ageRange.split('-')
      params.min_age = min
      params.max_age = max === '+' ? 150 : max
    }
    const res = await getPatients(params)
    patientList.value = res.items || res || []
    pagination.total = res.total || patientList.value.length
  } catch (error) {
    console.error('加载患者列表失败', error)
    ElMessage.error('加载患者列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = (params) => {
  Object.assign(searchForm, params)
  pagination.page = 1
  loadPatientList()
}

// 重置
const handleReset = () => {
  Object.keys(searchForm).forEach(key => {
    if (Array.isArray(searchForm[key])) {
      searchForm[key] = []
    } else {
      searchForm[key] = ''
    }
  })
  pagination.page = 1
  loadPatientList()
}

// 打开患者对话框
const openPatientDialog = (row = null) => {
  isEdit.value = !!row
  if (row) {
    Object.assign(patientForm, row)
  } else {
    Object.assign(patientForm, {
      id: null,
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
  }
  patientDialogVisible.value = true
}

// 保存患者
const savePatient = async () => {
  await patientFormRef.value.validate()
  patientSaving.value = true
  try {
    if (isEdit.value) {
      await updatePatient(patientForm.id, patientForm)
      ElMessage.success('更新成功')
    } else {
      await createPatient(patientForm)
      ElMessage.success('创建成功')
    }
    patientDialogVisible.value = false
    loadPatientList()
  } catch (error) {
    console.error('保存患者失败', error)
  } finally {
    patientSaving.value = false
  }
}

// 删除患者
const handleDeletePatient = async (row) => {
  try {
    await deletePatient(row.id)
    ElMessage.success('删除成功')
    loadPatientList()
  } catch (error) {
    console.error('删除患者失败', error)
    ElMessage.error('删除患者失败')
  }
}

// 查看患者详情
const viewPatientDetail = (row) => {
  router.push(`/patient/${row.id}`)
}

onMounted(() => {
  loadPatientList()
})
</script>

<style scoped>
.patient-manage-page {
  width: 100%;
}

.patient-info-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.patient-info {
  flex: 1;
  min-width: 0;
}

.patient-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.patient-meta {
  font-size: 12px;
  color: var(--text-secondary);
}
</style>