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

    <el-row :gutter="20" class="stat-row">
      <el-col :xs="24" :sm="12" :md="6">
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
      <el-col :xs="24" :sm="12" :md="6">
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
      <el-col :xs="24" :sm="12" :md="6">
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
      <el-col :xs="24" :sm="12" :md="6">
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

    <div class="worker-cluster-section">
      <div class="section-header">
        <span class="section-title">计算节点集群状态</span>
        <el-tag type="info" size="small" effect="plain" round>共 {{ workerList.length }} 个节点接入</el-tag>
      </div>
      
      <div class="worker-grid">
        <div v-for="worker in workerList" :key="worker.id" class="worker-card" :class="{ offline: !worker.is_online }">
          <div class="worker-header">
            <div class="worker-name">
              <el-icon :color="worker.is_online ? '#00B42A' : '#F53F3F'">
                <CircleCheck v-if="worker.is_online" />
                <CircleClose v-else />
              </el-icon>
              {{ worker.worker_name }}
            </div>
            <el-tag :type="worker.is_online ? 'success' : 'danger'" size="small" effect="light">
              {{ worker.is_online ? '在线' : '离线' }}
            </el-tag>
          </div>
          <div class="worker-meta">
            <div class="meta-item">
              <span class="meta-label">节点地址</span>
              <span class="meta-value" :title="worker.hostname">{{ worker.hostname || '-' }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">加载模型</span>
              <span class="meta-value" :title="worker.model_names?.join(', ')">{{ worker.model_names?.join(', ') || '-' }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">当前任务</span>
              <span class="meta-value">{{ worker.current_task_id ? worker.current_task_id.slice(0, 12) + '...' : '空闲' }}</span>
            </div>
          </div>
          <div class="worker-progress" v-if="worker.is_online">
            <div class="progress-row">
              <span class="progress-label">CPU</span>
              <el-progress :percentage="worker.cpu_usage || 0" :color="getCpuColor(worker.cpu_usage)" :stroke-width="6" class="flex-1" />
            </div>
            <div class="progress-row">
              <span class="progress-label">内存</span>
              <el-progress :percentage="worker.memory_usage || 0" :color="getMemoryColor(worker.memory_usage)" :stroke-width="6" class="flex-1" />
            </div>
          </div>
          <div class="worker-footer">
            <span>已处理: <b>{{ worker.processed_count || 0 }}</b></span>
            <span>心跳: {{ worker.last_heartbeat || '-' }}</span>
          </div>
        </div>
      </div>
    </div>

    <el-card class="common-card task-queue-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">全局诊断任务队列</span>
        </div>
      </template>

      <div class="task-filter-bar">
        <el-form :inline="true" :model="searchForm" class="filter-form">
          <el-form-item label="任务状态">
            <el-select v-model="searchForm.status" placeholder="全部" clearable style="width: 140px" @change="loadTaskList">
              <el-option label="等待中" value="pending" />
              <el-option label="处理中" value="processing" />
              <el-option label="已完成" value="completed" />
              <el-option label="失败" value="failed" />
            </el-select>
          </el-form-item>
          <el-form-item label="使用模型">
            <el-select v-model="searchForm.modelId" placeholder="全部" clearable style="width: 180px" @change="loadTaskList">
              <el-option
                v-for="model in modelList"
                :key="model.id"
                :label="model.model_name"
                :value="model.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-input v-model="searchForm.keyword" placeholder="搜索任务ID、医生姓名" clearable style="width: 220px" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="loadTaskList">
              <el-icon><Search /></el-icon> 搜索
            </el-button>
            <el-button @click="resetSearch">
              <el-icon><RefreshLeft /></el-icon> 重置
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-table :data="taskList" border stripe class="common-table" v-loading="loading" max-height="600">
        <el-table-column prop="task_id" label="任务ID" width="170" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="task-id-text" @click="viewTaskDetail(row)" title="点击查看详情">
              {{ row.task_id?.slice(0, 16) }}...
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="model_name" label="使用模型" min-width="150" />
        <el-table-column prop="doctor_name" label="提交医生" width="120" />
        <el-table-column prop="patient_name" label="患者姓名" width="120">
          <template #default="{ row }">
            {{ row.patient_name || '匿名' }}
          </template>
        </el-table-column>
        <el-table-column prop="worker_name" label="处理节点" width="140">
          <template #default="{ row }">
            <span v-if="row.worker_name"><el-icon><Cpu /></el-icon> {{ row.worker_name }}</span>
            <span v-else style="color: #86909c">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <StatusTag :status="row.status" />
          </template>
        </el-table-column>
        <el-table-column prop="queue_position" label="队列位置" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.status === 'pending'" type="info" size="small" effect="plain">
              # {{ row.queue_position || '-' }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column prop="duration" label="耗时" width="100">
          <template #default="{ row }">
            {{ row.duration ? row.duration + 's' : row.status === 'processing' ? '处理中...' : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewTaskDetail(row)">详情</el-button>
            <el-button
              v-if="row.status === 'failed'"
              type="warning" link size="small"
              @click="handleRetryTask(row)"
            >
              重试
            </el-button>
            <el-button
              v-if="row.status === 'pending' || row.status === 'processing'"
              type="danger" link size="small"
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

    <el-drawer v-model="detailDrawerVisible" title="任务详情诊断追踪" size="55%" class="task-drawer">
      <div v-if="currentTask" class="task-detail-content">
        
        <div class="lifecycle-steps">
          <el-steps :active="activeStep" :process-status="stepProcessStatus" finish-status="success" align-center>
            <el-step title="排队中" :description="currentTask.created_at" />
            <el-step title="分配节点" :description="currentTask.worker_name ? `节点: ${currentTask.worker_name}` : '等待分配'" />
            <el-step title="AI 推理中" :description="currentTask.started_at ? `开始: ${currentTask.started_at}` : ''" />
            <el-step title="结果生成" :description="currentTask.completed_at ? `完成: ${currentTask.completed_at}` : (currentTask.status === 'failed' ? '推理失败' : '')" />
          </el-steps>
        </div>

        <el-descriptions :column="2" border class="mb-20">
          <el-descriptions-item label="任务ID" :span="2">{{ currentTask.task_id }}</el-descriptions-item>
          <el-descriptions-item label="当前状态">
            <StatusTag :status="currentTask.status" />
          </el-descriptions-item>
          <el-descriptions-item label="任务耗时">{{ currentTask.duration ? currentTask.duration + 's' : '-' }}</el-descriptions-item>
          <el-descriptions-item label="使用模型">{{ currentTask.model_name }}</el-descriptions-item>
          <el-descriptions-item label="处理节点">{{ currentTask.worker_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="提交医生">{{ currentTask.doctor_name }}</el-descriptions-item>
          <el-descriptions-item label="患者姓名">{{ currentTask.patient_name || '匿名' }}</el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">输入数据 (Input Payload)</el-divider>
        <div class="data-section">
          <pre class="json-block">{{ JSON.stringify(currentTask.input_data || {}, null, 2) }}</pre>
        </div>

        <el-divider content-position="left">诊断结果 (Output Result)</el-divider>
        <div v-if="currentTask.status === 'completed' && currentTask.result" class="data-section">
          <pre class="json-block success-block">{{ JSON.stringify(currentTask.result, null, 2) }}</pre>
        </div>
        <div v-else-if="currentTask.status === 'failed'" class="error-section">
          <div class="error-title"><el-icon><WarningFilled /></el-icon> 推理异常中止</div>
          <pre class="error-block">{{ currentTask.error_msg || '未知错误，请检查 Worker 节点日志。' }}</pre>
        </div>
        <el-empty v-else description="正在处理或等待中，暂无结果" :image-size="60" />

      </div>
      <template #footer>
        <div style="flex: auto; text-align: right;">
          <el-button @click="detailDrawerVisible = false">关闭</el-button>
          <el-button
            v-if="currentTask?.status === 'failed'"
            type="warning"
            @click="handleRetryTask(currentTask)"
          >
            <el-icon><RefreshRight /></el-icon> 重试任务
          </el-button>
          <el-button
            v-if="currentTask?.status === 'pending' || currentTask?.status === 'processing'"
            type="danger"
            @click="handleTerminateTask(currentTask)"
          >
            终止任务
          </el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, RefreshLeft, Cpu, WarningFilled, RefreshRight } from '@element-plus/icons-vue'
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
const detailDrawerVisible = ref(false)
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

// 计算任务生命周期的激活步数
const activeStep = computed(() => {
  if (!currentTask.value) return 0
  const status = currentTask.value.status
  if (status === 'pending') return 0
  if (status === 'processing') return 2 // 已经分配并在推理
  if (status === 'completed') return 4 // 全部完成
  if (status === 'failed') return 2 // 停留在推理步骤报错
  return 0
})

// 计算步骤条的状态（成功或失败）
const stepProcessStatus = computed(() => {
  if (currentTask.value?.status === 'failed') return 'error'
  return 'process'
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
    detailDrawerVisible.value = true
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
      detailDrawerVisible.value = false
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
      if(detailDrawerVisible.value) detailDrawerVisible.value = false
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
    // 如果没有正在搜索或翻页，可以自动刷新表格
    if(pagination.page === 1 && !searchForm.keyword && !searchForm.status && !searchForm.modelId){
        loadTaskList()
    }
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

/* 统计卡片 */
.stat-row {
  margin-bottom: 24px;
}
.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 16px; /* 移动端适配 */
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}
.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
}
.stat-card.primary { background: linear-gradient(135deg, #165DFF 0%, #4080FF 100%); color: #fff; }
.stat-card.success { background: linear-gradient(135deg, #00B42A 0%, #23C343 100%); color: #fff; }
.stat-card.warning { background: linear-gradient(135deg, #FF7D00 0%, #FF9A2E 100%); color: #fff; }
.stat-card.danger { background: linear-gradient(135deg, #F53F3F 0%, #F76560 100%); color: #fff; }

.stat-icon {
  width: 56px; height: 56px; border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.stat-number { font-size: 32px; font-weight: 700; line-height: 1.2; margin-bottom: 4px; }
.stat-label { font-size: 14px; opacity: 0.9; }

/* ---------------------------------
   Worker 集群区块 (CSS Grid 平铺)
---------------------------------- */
.worker-cluster-section {
  margin-bottom: 24px;
}
.section-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  gap: 12px;
}
.section-title {
  font-size: 18px;
  font-weight: bold;
  color: var(--text-primary);
  position: relative;
  padding-left: 12px;
}
.section-title::before {
  content: '';
  position: absolute;
  left: 0; top: 2px; bottom: 2px;
  width: 4px;
  background-color: var(--primary-color);
  border-radius: 2px;
}

.worker-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.worker-card {
  padding: 16px;
  background: #fff;
  border: 1px solid var(--border-light);
  border-radius: 10px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
  display: flex;
  flex-direction: column;
}
.worker-card:hover {
  border-color: #165DFF;
  box-shadow: 0 4px 16px rgba(22, 93, 255, 0.1);
  transform: translateY(-2px);
}
.worker-card.offline {
  background: #f7f8fa;
  border-color: #e5e6eb;
  opacity: 0.7;
}
.worker-card.offline:hover {
  transform: none;
  box-shadow: none;
  border-color: #e5e6eb;
}

.worker-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 16px;
}
.worker-name {
  display: flex; align-items: center; gap: 8px;
  font-size: 16px; font-weight: 600; color: var(--text-primary);
}

.worker-meta { flex: 1; }
.meta-item {
  display: flex; justify-content: space-between;
  margin-bottom: 10px; font-size: 13px;
}
.meta-label { color: var(--text-secondary); }
.meta-value { color: var(--text-primary); font-weight: 500; max-width: 140px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.worker-progress {
  margin-top: 8px;
  padding-top: 12px;
  border-top: 1px dashed var(--border-light);
}
.progress-row {
  display: flex; align-items: center; margin-bottom: 8px; font-size: 12px;
}
.progress-label { width: 40px; color: var(--text-secondary); }
.flex-1 { flex: 1; margin-left: 8px; }

.worker-footer {
  margin-top: 12px; padding-top: 12px;
  border-top: 1px solid var(--border-light);
  display: flex; justify-content: space-between;
  font-size: 12px; color: var(--text-secondary);
}
.worker-footer b { color: var(--primary-color); font-size: 14px; }

/* ---------------------------------
   底部全宽任务队列
---------------------------------- */
.task-filter-bar {
  margin-bottom: 16px; padding: 16px;
  background: #f7f8fa; border-radius: 8px;
}
.filter-form { margin: 0; }
.task-id-text {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 13px; color: var(--primary-color);
  cursor: pointer; text-decoration: underline; text-underline-offset: 4px;
}
.task-id-text:hover { color: #4080FF; }

/* ---------------------------------
   任务详情抽屉
---------------------------------- */
.lifecycle-steps {
  padding: 20px 0 40px;
  background: #f7f8fa;
  border-radius: 8px;
  margin-bottom: 24px;
}

.mb-20 { margin-bottom: 20px; }

.data-section { width: 100%; margin-bottom: 24px; }
.json-block {
  background: #f5f7fa; padding: 16px; border-radius: 6px;
  font-family: 'Monaco', 'Menlo', monospace; font-size: 13px;
  line-height: 1.6; max-height: 400px; overflow: auto; margin: 0;
  border: 1px solid #e5e6eb;
}
.success-block {
  background: #f6ffed; border-color: #b7eb8f;
}

.error-section {
  width: 100%; margin-bottom: 24px;
  background: #FFF1F0; border: 1px solid #ffa39e;
  border-radius: 8px; padding: 16px;
}
.error-title {
  color: #cf1322; font-size: 15px; font-weight: bold;
  display: flex; align-items: center; gap: 8px; margin-bottom: 12px;
}
.error-block {
  font-family: 'Monaco', 'Menlo', monospace; font-size: 13px;
  line-height: 1.6; color: #cf1322;
  max-height: 300px; overflow: auto; margin: 0;
}
</style>