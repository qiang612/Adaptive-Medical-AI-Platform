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

    <!-- 搜索筛选区 -->
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
      <el-form-item label="任务状态">
        <el-select v-model="searchForm.status" placeholder="全部" clearable style="width: 160px" @change="loadTaskList">
          <el-option label="等待中" value="pending" />
          <el-option label="处理中" value="processing" />
          <el-option label="已完成" value="completed" />
          <el-option label="失败" value="failed" />
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

    <!-- 批量操作栏 -->
    <div v-if="selectedRows.length > 0" class="batch-action-bar">
      <span class="selected-count">已选择 {{ selectedRows.length }} 项</span>
      <el-button type="danger" size="small" @click="batchDelete">
        <el-icon><Delete /></el-icon>
        批量删除
      </el-button>
      <el-button type="default" size="small" @click="clearSelection">取消选择</el-button>
    </div>

    <!-- 任务列表 -->
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
        <el-table-column prop="status" label="状态" width="100">
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
        <el-table-column label="操作" width="280" fixed="right">
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
            <el-button
              type="success"
              link
              size="small"
              @click="handleDownloadReport(row)"
              :disabled="row.status !== 'completed'"
            >
              下载报告
            </el-button>
            <el-button
              type="warning"
              link
              size="small"
              @click="handleRetryTask(row)"
              :disabled="row.status !== 'failed'"
            >
              重试
            </el-button>
            <el-popconfirm
              title="确定要删除这个任务吗？"
              @confirm="deleteTask(row)"
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
        @change="loadTaskList"
      />
    </el-card>

    <!-- 诊断结果对话框 -->
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

// 搜索表单
const searchForm = reactive({
  keyword: '',
  timeRange: [],
  modelId: '',
  status: '',
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

// 加载任务列表
const loadTaskList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      keyword: searchForm.keyword,
      model_id: searchForm.modelId,
      status: searchForm.status,
      risk_level: searchForm.riskLevel
    }
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
    // 这里的 downloadReport 调用的就是第179行 import 进来的 API 接口
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
    // 这里调用的 retryTask 是从 api/task.js 导入的接口函数
    await retryTask(row.id) 
    ElMessage.success('任务已重新提交')
    loadTaskList()
  } catch (error) {
    console.error('重试任务失败', error)
    ElMessage.error('重试任务失败')
  }
}

// 删除任务
const deleteTask = async (row) => {
  try {
    await batchDeleteTasks([row.id])
    ElMessage.success('删除成功')
    loadTaskList()
  } catch (error) {
    console.error('删除任务失败', error)
    ElMessage.error('删除任务失败')
  }
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
</style>