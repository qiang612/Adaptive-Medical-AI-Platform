<template>
  <div class="task-monitor-page">
    <PageHeader
      title="任务监控中心"
      description="实时监控平台诊断任务队列、Worker节点运行状态，支持任务重试、终止等操作"
    >
      <template #extra>
        <el-button type="primary" @click="refreshAllData">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
      </template>
    </PageHeader>

    <!-- 队列统计卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :span="6">
        <div class="stat-card primary">
          <div class="stat-icon">
            <el-icon :size="28"><Clock /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ queueStats.pending || 0 }}</div>
            <div class="stat-label">等待中</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card warning">
          <div class="stat-icon">
            <el-icon :size="28"><Loading /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ queueStats.processing || 0 }}</div>
            <div class="stat-label">处理中</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card success">
          <div class="stat-icon">
            <el-icon :size="28"><CircleCheck /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ queueStats.completed || 0 }}</div>
            <div class="stat-label">今日完成</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card danger">
          <div class="stat-icon">
            <el-icon :size="28"><CircleClose /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ queueStats.failed || 0 }}</div>
            <div class="stat-label">今日失败</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <!-- 左侧：Worker节点监控 -->
      <el-col :span="8">
        <el-card class="common-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">Worker节点</span>
              <span class="node-count">共 {{ workerList.length }} 个节点</span>
            </div>
          </template>
          <div class="worker-list">
            <div v-for="worker in workerList" :key="worker.id" class="worker-card" :class="{ offline: !worker.is_online }">
              <div class="worker-header">
                <div class="worker-name">
                  <el-icon :color="worker.is_online ? '#00B42A' : '#F53F3F'">
                    <CircleCheck v-if="worker.is_online" />
                    <CircleClose v-else />
                  </el-icon>
                  {{ worker.worker_name }}
                </div>
                <el-tag :type="worker.is_online ? 'success' : 'danger'" size="small">
                  {{ worker.is_online ? '在线' : '离线' }}
                </el-tag>
              </div>
              <div class="worker-meta">
                <div class="meta-item">
                  <span class="meta-label">节点地址</span>
                  <span class="meta-value">{{ worker.hostname || '-' }}</span>
                </div>
                <div class="meta-item">
                  <span class="meta-label">处理模型</span>
                  <span class="meta-value">{{ worker.model_names?.join(', ') || '-' }}</span>
                </div>
                <div class="meta-item">
                  <span class="meta-label">当前任务</span>
                  <span class="meta-value">{{ worker.current_task_id ? worker.current_task_id.slice(0, 16) + '...' : '空闲' }}</span>
                </div>
                <div class="meta-item">
                  <span class="meta-label">已处理任务</span>
                  <span class="meta-value">{{ worker.processed_count || 0 }}</span>
                </div>
                <div class="meta-item">
                  <span class="meta-label">最后心跳</span>
                  <span class="meta-value">{{ worker.last_heartbeat || '-' }}</span>
                </div>
              </div>
              <el-progress
                v-if="worker.is_online"
                :percentage="worker.cpu_usage || 0"
                :color="getCpuColor(worker.cpu_usage)"
                :stroke-width="8"
                style="margin-top: 12px"
              >
                <template #default="{ percentage }">
                  <span class="percentage-text">{{ percentage }}% CPU</span>
                </template>
              </el-progress>
              <el-progress
                v-if="worker.is_online"
                :percentage="worker.memory_usage || 0"
                :color="getMemoryColor(worker.memory_usage)"
                :stroke-width="8"
                style="margin-top: 8px"
              >
                <template #default="{ percentage }">
                  <span class="percentage-text">{{ percentage }}% 内存</span>
                </template>
              </el-progress>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：任务列表 -->
      <el-col :span="16">
        <el-card class="common-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">任务队列</span>
            </div>
          </template>

          <!-- 搜索筛选 -->
          <div class="task-filter-bar">
            <el-form :inline="true" :model="searchForm" class="filter-form">
              <el-form-item label="任务状态">
                <el-select v-model="searchForm.status" placeholder="全部" clearable style="width: 160px" @change="loadTaskList">
                  <el-option label="等待中" value="pending" />
                  <el-option label="处理中" value="processing" />
                  <el-option label="已完成" value="completed" />
                  <el-option label="失败" value="failed" />
                </el-select>
              </el-form-item>
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
              <el-form-item>
                <el-input v-model="searchForm.keyword" placeholder="搜索任务ID、医生姓名" clearable style="width: 240px" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="loadTaskList">
                  <el-icon><Search /></el-icon>
                  搜索
                </el-button>
                <el-button @click="resetSearch">
                  <el-icon><RefreshLeft /></el-icon>
                  重置
                </el-button>
              </el-form-item>
            </el-form>
          </div>

          <!-- 任务表格 -->
          <el-table :data="taskList" border class="common-table" v-loading="loading" max-height="500">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="task_id" label="任务ID" width="180" show-overflow-tooltip>
              <template #default="{ row }">
                <el-tooltip :content="row.task_id" placement="top">
                  <span class="task-id-text">{{ row.task_id?.slice(0, 16) }}...</span>
                </el-tooltip>
              </template>
            </el-table-column>
            <el-table-column prop="model_name" label="使用模型" width="150" />
            <el-table-column prop="doctor_name" label="提交医生" width="120" />
            <el-table-column prop="patient_name" label="患者姓名" width="120">
              <template #default="{ row }">
                {{ row.patient_name || '匿名' }}
              </template>
            </el-table-column>
            <el-table-column prop="worker_name" label="处理节点" width="120">
              <template #default="{ row }">
                {{ row.worker_name || '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <StatusTag :status="row.status" />
              </template>
            </el-table-column>
            <el-table-column prop="queue_position" label="队列位置" width="100">
              <template #default="{ row }">
                {{ row.status === 'pending' ? '#' + (row.queue_position || '-') : '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180" />
            <el-table-column prop="duration" label="耗时" width="100">
              <template #default="{ row }">
                {{ row.duration ? row.duration + 's' : row.status === 'processing' ? '处理中...' : '-' }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="viewTaskDetail(row)">
                  详情
                </el-button>
                <el-button
                  v-if="row.status === 'failed'"
                  type="warning"
                  link
                  size="small"
                  @click="retryTask(row)"
                >
                  重试
                </el-button>
                <el-button
                  v-if="row.status === 'pending' || row.status === 'processing'"
                  type="danger"
                  link
                  size="small"
                  @click="handleTerminateTask(row)"
                >
                  终止
                </el-button>
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
      </el-col>
    </el-row>

    <!-- 任务详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="任务详情" width="900px" fullscreen>
      <div v-if="currentTask" class="task-detail-content">
        <el-descriptions :column="2" border class="mb-20">
          <el-descriptions-item label="任务ID">{{ currentTask.task_id }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <StatusTag :status="currentTask.status" />
          </el-descriptions-item>
          <el-descriptions-item label="使用模型">{{ currentTask.model_name }}</el-descriptions-item>
          <el-descriptions-item label="处理节点">{{ currentTask.worker_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="提交医生">{{ currentTask.doctor_name }}</el-descriptions-item>
          <el-descriptions-item label="患者姓名">{{ currentTask.patient_name || '匿名' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ currentTask.created_at }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ currentTask.started_at || '-' }}</el-descriptions-item>
          <el-descriptions-item label="完成时间">{{ currentTask.completed_at || '-' }}</el-descriptions-item>
          <el-descriptions-item label="耗时">{{ currentTask.duration ? currentTask.duration + 's' : '-' }}</el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">输入数据</el-divider>
        <div class="data-section">
          <pre class="json-block">{{ JSON.stringify(currentTask.input_data || {}, null, 2) }}</pre>
        </div>

        <el-divider content-position="left">诊断结果</el-divider>
        <div v-if="currentTask.result" class="data-section">
          <pre class="json-block">{{ JSON.stringify(currentTask.result, null, 2) }}</pre>
        </div>
        <el-empty v-else description="暂无结果" :image-size="60" />

        <el-divider content-position="left" v-if="currentTask.error_msg">错误信息</el-divider>
        <div v-if="currentTask.error_msg" class="error-section">
          <pre class="error-block">{{ currentTask.error_msg }}</pre>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button
          v-if="currentTask?.status === 'failed'"
          type="warning"
          @click="handleRetryTask(currentTask)"
        >
          重试任务
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import Pagination from '@/components/Pagination.vue'
import StatusTag from '@/components/StatusTag.vue'
import { 
  getTaskQueueStats as getQueueStats, 
  getWorkerNodes as getWorkerList, 
  getAllTasks as getTaskList, 
  getTaskDetail, 
  retryTask, 
  terminateTask 
} from '@/api/task'
import { getActiveModels } from '@/api/model'

const loading = ref(false)
const queueStats = ref({})
const workerList = ref([])
const taskList = ref([])
const modelList = ref([])
const detailDialogVisible = ref(false)
const currentTask = ref(null)
let refreshTimer = null

// 搜索表单
const searchForm = reactive({
  keyword: '',
  status: '',
  modelId: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 获取CPU使用率颜色
const getCpuColor = (percentage) => {
  if (percentage >= 80) return '#F53F3F'
  if (percentage >= 60) return '#FF7D00'
  return '#00B42A'
}

// 获取内存使用率颜色
const getMemoryColor = (percentage) => {
  if (percentage >= 85) return '#F53F3F'
  if (percentage >= 70) return '#FF7D00'
  return '#165DFF'
}

// 加载队列统计
const loadQueueStats = async () => {
  try {
    queueStats.value = await getQueueStats()
  } catch (error) {
    console.error('加载队列统计失败', error)
  }
}

// 加载Worker列表
const loadWorkerList = async () => {
  try {
    workerList.value = await getWorkerList()
  } catch (error) {
    console.error('加载Worker列表失败', error)
  }
}

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
      status: searchForm.status,
      model_id: searchForm.modelId
    }
    const res = await getTaskList(params)
    taskList.value = res.items || res || []
    pagination.total = res.total || taskList.value.length
  } catch (error) {
    console.error('加载任务列表失败', error)
    ElMessage.error('加载任务列表失败')
  } finally {
    loading.value = false
  }
}

// 刷新所有数据
const refreshAllData = () => {
  loadQueueStats()
  loadWorkerList()
  loadTaskList()
  ElMessage.success('数据已刷新')
}

// 重置搜索
const resetSearch = () => {
  searchForm.keyword = ''
  searchForm.status = ''
  searchForm.modelId = ''
  pagination.page = 1
  loadTaskList()
}

// 查看任务详情
const viewTaskDetail = async (row) => {
  try {
    currentTask.value = await getTaskDetail(row.id)
    detailDialogVisible.value = true
  } catch (error) {
    console.error('获取任务详情失败', error)
    ElMessage.error('获取任务详情失败')
  }
}

// 重试任务
const handleRetryTask = async (row) => {
  ElMessageBox.confirm(`确定要重试任务"${row.task_id?.slice(0, 16)}..."吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await retryTask(row.id)
      ElMessage.success('任务已重新提交')
      detailDialogVisible.value = false
      refreshAllData()
    } catch (error) {
      console.error('重试任务失败', error)
      ElMessage.error('重试任务失败')
    }
  })
}

// 终止任务
const handleTerminateTask = async (row) => {
  ElMessageBox.confirm(`确定要终止任务"${row.task_id?.slice(0, 16)}..."吗？此操作不可恢复！`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'danger'
  }).then(async () => {
    try {
      await terminateTask(row.id)
      ElMessage.success('任务已终止')
      refreshAllData()
    } catch (error) {
      console.error('终止任务失败', error)
      ElMessage.error('终止任务失败')
    }
  })
}

onMounted(() => {
  loadModelList()
  refreshAllData()
  // 每5秒自动刷新
  refreshTimer = setInterval(() => {
    loadQueueStats()
    loadWorkerList()
  }, 5000)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style scoped>
.task-monitor-page {
  width: 100%;
}

.stat-row {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
}

.stat-card.primary {
  background: linear-gradient(135deg, #165DFF 0%, #4080FF 100%);
  color: #fff;
}

.stat-card.success {
  background: linear-gradient(135deg, #00B42A 0%, #23C343 100%);
  color: #fff;
}

.stat-card.warning {
  background: linear-gradient(135deg, #FF7D00 0%, #FF9A2E 100%);
  color: #fff;
}

.stat-card.danger {
  background: linear-gradient(135deg, #F53F3F 0%, #F76560 100%);
  color: #fff;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

.worker-list {
  width: 100%;
}

.worker-card {
  padding: 16px;
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  margin-bottom: 16px;
  transition: all 0.3s ease;
}

.worker-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 2px 8px rgba(22, 93, 255, 0.1);
}

.worker-card.offline {
  opacity: 0.6;
  background: var(--bg-hover);
}

.worker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.worker-name {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.worker-meta {
  width: 100%;
}

.meta-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 13px;
}

.meta-label {
  color: var(--text-secondary);
}

.meta-value {
  color: var(--text-primary);
  font-weight: 500;
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.percentage-text {
  font-size: 12px;
  color: var(--text-secondary);
}

.node-count {
  font-size: 14px;
  color: var(--text-secondary);
}

.task-filter-bar {
  margin-bottom: 16px;
  padding: 12px;
  background: var(--bg-hover);
  border-radius: 8px;
}

.filter-form {
  margin: 0;
}

.task-id-text {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  color: var(--primary-color);
  cursor: pointer;
}

.mb-20 {
  margin-bottom: 20px;
}

.data-section {
  width: 100%;
}

.json-block {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 6px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  line-height: 1.6;
  max-height: 400px;
  overflow: auto;
  margin: 0;
}

.error-section {
  width: 100%;
}

.error-block {
  background: #FFF1F0;
  padding: 16px;
  border-radius: 6px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  line-height: 1.6;
  color: var(--danger-color);
  max-height: 300px;
  overflow: auto;
  margin: 0;
}
</style>