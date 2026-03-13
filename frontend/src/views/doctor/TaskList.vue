<template>
  <div class="task-list-page">
    <PageHeader
      title="我的诊断任务"
      description="查看和管理您提交的所有AI诊断任务，支持筛选、搜索、批量操作"
    >
      <template #extra>
        <el-button type="primary" @click="$router.push('/inference')">
          <el-icon><Plus /></el-icon>
          新建诊断
        </el-button>
      </template>
    </PageHeader>

    <el-tabs v-model="activeStatusTab" @tab-change="handleTabChange" class="status-tabs">
      <el-tab-pane label="全部任务" name="all"></el-tab-pane>
      <el-tab-pane label="⏳ 等待中" name="pending"></el-tab-pane>
      <el-tab-pane label="⚙️ 处理中" name="processing"></el-tab-pane>
      <el-tab-pane label="✅ 已完成" name="completed"></el-tab-pane>
      <el-tab-pane label="❌ 失败" name="failed"></el-tab-pane>
    </el-tabs>

    <SearchBar
      :show-keyword="true"
      keyword-placeholder="搜索患者姓名、患者ID、任务ID"
      :show-time-range="true"
      @search="handleSearch"
      @reset="handleReset"
    >
      <el-form-item label="使用模型">
        <el-select v-model="searchForm.modelId" placeholder="全部" clearable style="width: 200px" @change="loadTaskList">
          <el-option
            v-for="model in modelList"
            :key="model.id"
            :label="model.model_name"
            :value="model.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="风险等级">
        <el-select v-model="searchForm.riskLevel" placeholder="全部" clearable style="width: 160px" @change="loadTaskList">
          <el-option label="低风险" value="低风险" />
          <el-option label="中风险" value="中风险" />
          <el-option label="高风险" value="高风险" />
        </el-select>
      </el-form-item>
    </SearchBar>

    <div v-if="selectedRows.length > 0" class="batch-action-bar">
      <span class="selected-count">已选择 {{ selectedRows.length }} 项</span>
      <el-button type="danger" size="small" @click="batchDelete">
        <el-icon><Delete /></el-icon>
        批量删除
      </el-button>
      <el-button type="default" size="small" @click="clearSelection">取消选择</el-button>
    </div>

    <el-card class="common-card">
      <el-table
        :data="taskList"
        border
        class="common-table"
        v-loading="loading"
        @selection-change="handleSelectionChange"
        row-key="id"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="task_id" label="任务ID" width="180" show-overflow-tooltip />
        <el-table-column prop="patient_name" label="患者姓名" width="120">
          <template #default="{ row }">
            {{ row.patient_name || '匿名患者' }}
          </template>
        </el-table-column>
        <el-table-column prop="patient_id" label="患者ID" width="120">
          <template #default="{ row }">
            {{ row.patient_id || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="model_name" label="使用模型" width="150" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <StatusTag :status="row.status" />
          </template>
        </el-table-column>
        <el-table-column prop="risk_level" label="风险等级" width="100">
          <template #default="{ row }">
            <el-tag
              v-if="row.risk_level"
              :type="row.risk_level === '高风险' ? 'danger' : row.risk_level === '中风险' ? 'warning' : 'success'"
              size="small"
              effect="light"
            >
              {{ row.risk_level }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column prop="duration" label="耗时" width="100">
          <template #default="{ row }">
            {{ row.duration ? row.duration + 's' : '-' }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              link
              size="small"
              @click="viewResult(row)"
              :disabled="row.status !== 'completed'"
            >
              查看结果
            </el-button>
            
            <el-divider direction="vertical" />
            
            <el-dropdown trigger="click" @command="handleCommand($event, row)">
              <span class="el-dropdown-link" :class="{'is-disabled': false}">
                更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="download" :disabled="row.status !== 'completed'">
                    下载报告
                  </el-dropdown-item>
                  <el-dropdown-item command="retry" :disabled="row.status !== 'failed'">
                    重试任务
                  </el-dropdown-item>
                  <el-dropdown-item command="delete" divided class="danger-item">
                    删除任务
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
      
      <Pagination
        v-model:model-value="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        @change="loadTaskList"
      />
    </el-card>

    <el-dialog v-model="resultDialogVisible" title="诊断结果" width="900px" fullscreen>
      <ResultVisual :result="currentResult" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import SearchBar from '@/components/SearchBar.vue'
import Pagination from '@/components/Pagination.vue'
import StatusTag from '@/components/StatusTag.vue'
import ResultVisual from '@/components/ResultVisual.vue'
import { getMyTasks, getTaskStatus, retryTask, terminateTask, downloadReport, batchDeleteTasks } from '@/api/task'
import { getActiveModels } from '@/api/model'

const loading = ref(false)
const taskList = ref([])
const modelList = ref([])
const selectedRows = ref([])
const resultDialogVisible = ref(false)
const currentResult = ref(null)

// 状态Tabs
const activeStatusTab = ref('all')

// 搜索表单 (去掉了 status 字段，交由 Tab 管理)
const searchForm = reactive({
  keyword: '',
  timeRange: [],
  modelId: '',
  riskLevel: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 加载模型列表
const loadModelList = async () => {
  try {
    modelList.value = await getActiveModels()
  } catch (error) {
    console.error('加载模型列表失败', error)
  }
}

// 切换状态 Tab
const handleTabChange = (name) => {
  pagination.page = 1
  loadTaskList()
}

// 加载任务列表 (修复 422 错误的核心部分)
const loadTaskList = async () => {
  loading.value = true
  try {
    // 先构建必须要传的基础参数
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
    }
    
    // 只有当对应的值存在（且不是空字符串）时，才添加到参数对象中
    if (searchForm.keyword) {
      params.keyword = searchForm.keyword
    }
    if (searchForm.modelId) {
      params.model_id = searchForm.modelId
    }
    if (activeStatusTab.value && activeStatusTab.value !== 'all') {
      params.status = activeStatusTab.value
    }
    if (searchForm.riskLevel) {
      params.risk_level = searchForm.riskLevel
    }
    
    // 处理时间范围
    if (searchForm.timeRange && searchForm.timeRange.length === 2) {
      params.start_time = searchForm.timeRange[0]
      params.end_time = searchForm.timeRange[1]
    }

    const res = await getMyTasks(params)
    taskList.value = res.items || res || []
    pagination.total = res.total || taskList.value.length
  } catch (error) {
    console.error('加载任务列表失败', error)
    ElMessage.error('加载任务列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = (params) => {
  Object.assign(searchForm, params)
  pagination.page = 1
  loadTaskList()
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
  activeStatusTab.value = 'all'
  pagination.page = 1
  loadTaskList()
}

// 表格选择
const handleSelectionChange = (selection) => {
  selectedRows.value = selection
}

// 清除选择
const clearSelection = () => {
  selectedRows.value = []
}

// 处理下拉菜单操作
const handleCommand = (command, row) => {
  if (command === 'download') {
    handleDownloadReport(row)
  } else if (command === 'retry') {
    handleRetryTask(row)
  } else if (command === 'delete') {
    deleteTask(row)
  }
}

// 查看结果
const viewResult = async (row) => {
  if (row.result) {
    currentResult.value = row.result
  } else {
    try {
      const status = await getTaskStatus(row.task_id)
      currentResult.value = status.result
    } catch (error) {
      console.error('获取任务结果失败', error)
      ElMessage.error('获取任务结果失败')
      return
    }
  }
  resultDialogVisible.value = true
}

// 下载报告
const handleDownloadReport = async (row) => {
  try {
    const res = await downloadReport(row.id) 
    const blob = new Blob([res], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `诊断报告_${row.patient_name || '未知'}_${row.created_at}.pdf`
    a.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('报告下载成功')
  } catch (error) {
    console.error('下载报告失败', error)
    ElMessage.error('下载报告失败')
  }
}

// 重试任务
const handleRetryTask = async (row) => {
  try {
    await retryTask(row.id) 
    ElMessage.success('任务已重新提交')
    loadTaskList()
  } catch (error) {
    console.error('重试任务失败', error)
    ElMessage.error('重试任务失败')
  }
}

// 删除任务
const deleteTask = (row) => {
  ElMessageBox.confirm('确定要删除这个诊断任务吗？此操作不可恢复。', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await batchDeleteTasks([row.id])
      ElMessage.success('删除成功')
      loadTaskList()
    } catch (error) {
      console.error('删除任务失败', error)
      ElMessage.error('删除任务失败')
    }
  }).catch(() => {})
}

// 批量删除
const batchDelete = () => {
  ElMessageBox.confirm(`确定要删除选中的 ${selectedRows.value.length} 个任务吗？`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'danger'
  }).then(async () => {
    try {
      const ids = selectedRows.value.map(row => row.id)
      await batchDeleteTasks(ids)
      ElMessage.success('批量删除成功')
      clearSelection()
      loadTaskList()
    } catch (error) {
      console.error('批量删除失败', error)
      ElMessage.error('批量删除失败')
    }
  })
}

onMounted(() => {
  loadModelList()
  loadTaskList()
})
</script>

<style scoped>
.task-list-page {
  width: 100%;
}

.status-tabs {
  margin-bottom: 20px;
  background-color: #fff;
  padding: 10px 20px 0;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.batch-action-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 20px;
  background: linear-gradient(135deg, #FFF7E6 0%, #FFF2CC 100%);
  border-radius: 8px;
  margin-bottom: 20px;
}

.selected-count {
  font-size: 14px;
  color: var(--text-regular);
  font-weight: 500;
}

.el-dropdown-link {
  color: var(--el-color-primary);
  cursor: pointer;
  font-size: 13px;
  display: inline-flex;
  align-items: center;
  transition: opacity 0.2s;
}

.el-dropdown-link:hover {
  opacity: 0.8;
}

.danger-item {
  color: var(--el-color-danger) !important;
}
</style>