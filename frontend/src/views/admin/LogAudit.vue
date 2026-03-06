<template>
  <div class="log-audit-page">
    <PageHeader
      title="日志审计"
      description="查询和导出平台操作日志、登录日志、推理任务日志，满足合规审计需求"
    />

    <el-card class="common-card">
      <el-tabs v-model="activeTab" type="border-card" @tab-change="handleTabChange">
        <!-- 操作日志 -->
        <el-tab-pane label="操作日志" name="operation">
          <SearchBar
            :show-keyword="true"
            keyword-placeholder="搜索操作人、操作内容、IP地址"
            :show-time-range="true"
            @search="handleSearch"
            @reset="handleReset"
          >
            <el-form-item label="操作类型">
              <el-select v-model="searchForm.operation_type" placeholder="全部" clearable style="width: 160px">
                <el-option label="新增" value="create" />
                <el-option label="编辑" value="update" />
                <el-option label="删除" value="delete" />
                <el-option label="查询" value="query" />
                <el-option label="上传" value="upload" />
                <el-option label="下载" value="download" />
                <el-option label="登录" value="login" />
                <el-option label="登出" value="logout" />
              </el-select>
            </el-form-item>
            <el-form-item label="操作状态">
              <el-select v-model="searchForm.status" placeholder="全部" clearable style="width: 160px">
                <el-option label="成功" value="success" />
                <el-option label="失败" value="fail" />
              </el-select>
            </el-form-item>
          </SearchBar>

          <el-table :data="operationLogList" border class="common-table" v-loading="loading">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="operator_name" label="操作人" width="120" />
            <el-table-column prop="operation_type" label="操作类型" width="100">
              <template #default="{ row }">
                <el-tag size="small">{{ row.operation_type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="operation_content" label="操作内容" min-width="200" show-overflow-tooltip />
            <el-table-column prop="resource_type" label="资源类型" width="120" />
            <el-table-column prop="resource_id" label="资源ID" width="100" />
            <el-table-column prop="ip_address" label="IP地址" width="140" />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.status === 'success' ? 'success' : 'danger'" size="small">
                  {{ row.status === 'success' ? '成功' : '失败' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="duration" label="耗时" width="80">
              <template #default="{ row }">
                {{ row.duration ? row.duration + 'ms' : '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="操作时间" width="180" />
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="viewOperationDetail(row)">详情</el-button>
              </template>
            </el-table-column>
          </el-table>

          <Pagination
            v-model:model-value="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            @change="loadOperationLogList"
          />

          <div class="export-section">
            <el-button type="primary" @click="exportLog('operation')">
              <el-icon><Download /></el-icon>
              导出当前筛选结果
            </el-button>
          </div>
        </el-tab-pane>

        <!-- 登录日志 -->
        <el-tab-pane label="登录日志" name="login">
          <SearchBar
            :show-keyword="true"
            keyword-placeholder="搜索用户名、姓名、IP地址"
            :show-time-range="true"
            @search="handleSearch"
            @reset="handleReset"
          >
            <el-form-item label="登录状态">
              <el-select v-model="searchForm.login_status" placeholder="全部" clearable style="width: 160px">
                <el-option label="成功" value="success" />
                <el-option label="失败" value="fail" />
              </el-select>
            </el-form-item>
          </SearchBar>

          <el-table :data="loginLogList" border class="common-table" v-loading="loading">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="username" label="用户名" width="120" />
            <el-table-column prop="full_name" label="姓名" width="120" />
            <el-table-column prop="role" label="角色" width="100">
              <template #default="{ row }">
                <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'" size="small">
                  {{ row.role === 'admin' ? '管理员' : '医生' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="ip_address" label="IP地址" width="140" />
            <el-table-column prop="user_agent" label="设备信息" min-width="200" show-overflow-tooltip />
            <el-table-column prop="location" label="登录地点" width="150" />
            <el-table-column prop="status" label="登录状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'success' ? 'success' : 'danger'" size="small">
                  {{ row.status === 'success' ? '成功' : '失败' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="fail_reason" label="失败原因" min-width="150" show-overflow-tooltip />
            <el-table-column prop="login_time" label="登录时间" width="180" />
          </el-table>

          <Pagination
            v-model:model-value="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            @change="loadLoginLogList"
          />

          <div class="export-section">
            <el-button type="primary" @click="exportLog('login')">
              <el-icon><Download /></el-icon>
              导出当前筛选结果
            </el-button>
          </div>
        </el-tab-pane>

        <!-- 推理日志 -->
        <el-tab-pane label="推理日志" name="inference">
          <SearchBar
            :show-keyword="true"
            keyword-placeholder="搜索任务ID、模型名称、医生姓名、患者姓名"
            :show-time-range="true"
            @search="handleSearch"
            @reset="handleReset"
          >
            <el-form-item label="推理状态">
              <el-select v-model="searchForm.inference_status" placeholder="全部" clearable style="width: 160px">
                <el-option label="成功" value="completed" />
                <el-option label="失败" value="failed" />
                <el-option label="处理中" value="processing" />
                <el-option label="等待中" value="pending" />
              </el-select>
            </el-form-item>
          </SearchBar>

          <el-table :data="inferenceLogList" border class="common-table" v-loading="loading">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="task_id" label="任务ID" width="180" show-overflow-tooltip />
            <el-table-column prop="model_name" label="模型名称" width="150" />
            <el-table-column prop="doctor_name" label="医生姓名" width="120" />
            <el-table-column prop="patient_name" label="患者姓名" width="120" />
            <el-table-column prop="worker_name" label="处理节点" width="120" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <StatusTag :status="row.status" />
              </template>
            </el-table-column>
            <el-table-column prop="input_data_size" label="输入数据量" width="120" />
            <el-table-column prop="duration" label="推理耗时" width="100">
              <template #default="{ row }">
                {{ row.duration ? row.duration + 's' : '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180" />
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="viewInferenceDetail(row)">详情</el-button>
              </template>
            </el-table-column>
          </el-table>

          <Pagination
            v-model:model-value="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            @change="loadInferenceLogList"
          />

          <div class="export-section">
            <el-button type="primary" @click="exportLog('inference')">
              <el-icon><Download /></el-icon>
              导出当前筛选结果
            </el-button>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 日志详情抽屉 -->
    <el-drawer v-model="detailDrawerVisible" title="日志详情" size="40%">
      <div v-if="currentLog" class="log-detail-content">
        <el-descriptions :column="1" border>
          <el-descriptions-item
            v-for="(value, key) in currentLog"
            :key="key"
            :label="keyMap[key] || key"
          >
            <template v-if="typeof value === 'object' && value !== null">
              <pre class="json-block">{{ JSON.stringify(value, null, 2) }}</pre>
            </template>
            <template v-else>
              {{ value || '-' }}
            </template>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import SearchBar from '@/components/SearchBar.vue'
import Pagination from '@/components/Pagination.vue'
import StatusTag from '@/components/StatusTag.vue'
import { getOperationLogs, getLoginLogs, getInferenceLogs, exportLogs } from '@/api/log'

const activeTab = ref('operation')
const loading = ref(false)
const detailDrawerVisible = ref(false)
const currentLog = ref(null)

// 字段映射
const keyMap = {
  id: 'ID',
  operator_name: '操作人',
  operation_type: '操作类型',
  operation_content: '操作内容',
  resource_type: '资源类型',
  resource_id: '资源ID',
  ip_address: 'IP地址',
  status: '状态',
  duration: '耗时',
  created_at: '操作时间',
  username: '用户名',
  full_name: '姓名',
  role: '角色',
  user_agent: '设备信息',
  location: '登录地点',
  fail_reason: '失败原因',
  login_time: '登录时间',
  task_id: '任务ID',
  model_name: '模型名称',
  doctor_name: '医生姓名',
  patient_name: '患者姓名',
  worker_name: '处理节点',
  input_data_size: '输入数据量',
  request_params: '请求参数',
  response_data: '响应数据',
  error_msg: '错误信息'
}

// 搜索表单
const searchForm = reactive({
  keyword: '',
  timeRange: [],
  operation_type: '',
  status: '',
  login_status: '',
  inference_status: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 日志列表
const operationLogList = ref([])
const loginLogList = ref([])
const inferenceLogList = ref([])

// Tab切换
const handleTabChange = () => {
  pagination.page = 1
  loadLogList()
}

// 搜索
const handleSearch = (params) => {
  Object.assign(searchForm, params)
  pagination.page = 1
  loadLogList()
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
  loadLogList()
}

// 加载对应类型的日志列表
const loadLogList = () => {
  switch (activeTab.value) {
    case 'operation':
      loadOperationLogList()
      break
    case 'login':
      loadLoginLogList()
      break
    case 'inference':
      loadInferenceLogList()
      break
  }
}

// 加载操作日志
const loadOperationLogList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      keyword: searchForm.keyword,
      operation_type: searchForm.operation_type,
      status: searchForm.status
    }
    if (searchForm.timeRange && searchForm.timeRange.length === 2) {
      params.start_time = searchForm.timeRange[0]
      params.end_time = searchForm.timeRange[1]
    }
    const res = await getOperationLogs(params)
    operationLogList.value = res.items || res || []
    pagination.total = res.total || operationLogList.value.length
  } catch (error) {
    console.error('加载操作日志失败', error)
    ElMessage.error('加载操作日志失败')
  } finally {
    loading.value = false
  }
}

// 加载登录日志
const loadLoginLogList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      keyword: searchForm.keyword,
      status: searchForm.login_status
    }
    if (searchForm.timeRange && searchForm.timeRange.length === 2) {
      params.start_time = searchForm.timeRange[0]
      params.end_time = searchForm.timeRange[1]
    }
    const res = await getLoginLogs(params)
    loginLogList.value = res.items || res || []
    pagination.total = res.total || loginLogList.value.length
  } catch (error) {
    console.error('加载登录日志失败', error)
    ElMessage.error('加载登录日志失败')
  } finally {
    loading.value = false
  }
}

// 加载推理日志
const loadInferenceLogList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      keyword: searchForm.keyword,
      status: searchForm.inference_status
    }
    if (searchForm.timeRange && searchForm.timeRange.length === 2) {
      params.start_time = searchForm.timeRange[0]
      params.end_time = searchForm.timeRange[1]
    }
    const res = await getInferenceLogs(params)
    inferenceLogList.value = res.items || res || []
    pagination.total = res.total || inferenceLogList.value.length
  } catch (error) {
    console.error('加载推理日志失败', error)
    ElMessage.error('加载推理日志失败')
  } finally {
    loading.value = false
  }
}

// 查看操作日志详情
const viewOperationDetail = (row) => {
  currentLog.value = row
  detailDrawerVisible.value = true
}

// 查看推理日志详情
const viewInferenceDetail = (row) => {
  currentLog.value = row
  detailDrawerVisible.value = true
}

// 导出日志
const exportLog = async (type) => {
  try {
    const params = {
      keyword: searchForm.keyword,
      status: type === 'operation' ? searchForm.status : type === 'login' ? searchForm.login_status : searchForm.inference_status
    }
    if (type === 'operation') params.operation_type = searchForm.operation_type
    if (searchForm.timeRange && searchForm.timeRange.length === 2) {
      params.start_time = searchForm.timeRange[0]
      params.end_time = searchForm.timeRange[1]
    }

    const res = await exportLogs(type, params)
    // 处理blob下载
    const blob = new Blob([res], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${type}_log_${new Date().toLocaleDateString()}.xlsx`
    a.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出日志失败', error)
    ElMessage.error('导出失败')
  }
}

onMounted(() => {
  loadLogList()
})
</script>

<style scoped>
.log-audit-page {
  width: 100%;
}

.export-section {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.log-detail-content {
  width: 100%;
}

.json-block {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  line-height: 1.6;
  max-height: 300px;
  overflow-x: auto;
  margin: 0;
}
</style>