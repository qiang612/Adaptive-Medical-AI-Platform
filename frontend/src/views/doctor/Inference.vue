<template>
  <div class="inference-page">
    <PageHeader
      title="AI辅助诊断"
      description="选择诊断模型，输入患者信息，提交AI智能诊断"
    >
      <template #extra>
        <el-button @click="handleSaveDraft">
          <el-icon><DocumentAdd /></el-icon>
          保存草稿
        </el-button>
        <el-button @click="resetForm">
          <el-icon><Refresh /></el-icon>
          重置表单
        </el-button>
      </template>
    </PageHeader>

    <el-row :gutter="20">
      <el-col :span="16">
        <!-- 基础信息卡片 -->
        <el-card class="common-card">
          <template #header>
            <span class="card-title">患者基础信息</span>
          </template>
          <el-form :model="taskForm" label-width="100px" class="common-form">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="选择模型" required>
                  <el-select
                    v-model="taskForm.modelId"
                    placeholder="请选择AI诊断模型"
                    style="width: 100%"
                    @change="onModelChange"
                    clearable
                  >
                    <el-option-group
                      v-for="group in modelGroup"
                      :key="group.type"
                      :label="group.label"
                    >
                      <el-option
                        v-for="model in group.models"
                        :key="model.id"
                        :label="model.model_name"
                        :value="model.id"
                        :description="`${model.model_type} | v${model.model_version}`"
                      />
                    </el-option-group>
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="常用模型">
                  <el-space wrap>
                    <el-tag
                      v-for="model in favoriteModels"
                      :key="model.id"
                      type="info"
                      effect="light"
                      closable
                      @click="taskForm.modelId = model.id; onModelChange(model.id)"
                      @close="removeFavorite(model.id)"
                    >
                      {{ model.model_name }}
                    </el-tag>
                  </el-space>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="患者姓名">
                  <el-input v-model="taskForm.patientName" placeholder="请输入患者姓名" clearable />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="患者ID">
                  <el-input v-model="taskForm.patientId" placeholder="请输入患者ID" clearable />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="性别">
                  <el-select v-model="taskForm.gender" placeholder="请选择" style="width: 100%" clearable>
                    <el-option label="男" value="男" />
                    <el-option label="女" value="女" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="年龄">
                  <el-input-number v-model="taskForm.age" :min="0" :max="150" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="联系方式">
                  <el-input v-model="taskForm.phone" placeholder="请输入手机号" clearable />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="检查日期">
                  <el-date-picker
                    v-model="taskForm.checkDate"
                    type="date"
                    style="width: 100%"
                    value-format="YYYY-MM-DD"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-card>

        <!-- 动态表单区域 -->
        <el-card v-if="selectedModel" class="common-card">
          <template #header>
            <span class="card-title">模型输入参数</span>
            <el-tag :type="selectedModel.model_type === '单模态' ? 'primary' : 'success'">
              {{ selectedModel.model_type }}
            </el-tag>
          </template>
          <DynamicForm v-model="taskForm.inputData" :schema="selectedModel.input_schema" />
        </el-card>

        <!-- 文件上传区域 -->
        <el-card class="common-card">
          <template #header>
            <span class="card-title">文件上传</span>
            <span class="upload-tip">支持JPG/PNG/DICOM格式影像、Excel数据表格</span>
          </template>
          <el-upload
            v-model:file-list="fileList"
            multiple
            :auto-upload="false"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            :file-list="fileList"
            accept=".jpg,.jpeg,.png,.dcm,.xlsx,.xls"
          >
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">单个文件大小不超过50MB</div>
            </template>
          </el-upload>
        </el-card>

        <!-- 提交按钮 -->
        <div class="submit-section">
          <el-button type="primary" size="large" :loading="submitting" @click="handleSubmit">
            <el-icon><VideoPlay /></el-icon>
            提交诊断任务
          </el-button>
          <el-button size="large" @click="goToTaskList">
            查看我的任务列表
          </el-button>
        </div>
      </el-col>

      <el-col :span="8">
        <!-- 模型说明卡片 -->
        <el-card v-if="selectedModel" class="common-card model-info">
          <template #header>
            <span class="card-title">模型说明</span>
            <el-button
              :type="isFavorite ? 'warning' : 'primary'"
              :icon="isFavorite ? 'StarFilled' : 'Star'"
              size="small"
              text
              @click="toggleFavorite"
            >
              {{ isFavorite ? '取消收藏' : '收藏模型' }}
            </el-button>
          </template>
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="模型名称">{{ selectedModel.model_name }}</el-descriptions-item>
            <el-descriptions-item label="模型编码">{{ selectedModel.model_code }}</el-descriptions-item>
            <el-descriptions-item label="模型类型">{{ selectedModel.model_type }}</el-descriptions-item>
            <el-descriptions-item label="版本号">{{ selectedModel.model_version }}</el-descriptions-item>
            <el-descriptions-item label="准确率">{{ selectedModel.accuracy || '-' }}</el-descriptions-item>
            <el-descriptions-item label="AUC值">{{ selectedModel.auc || '-' }}</el-descriptions-item>
          </el-descriptions>
          <el-divider content-position="left">模型描述</el-divider>
          <p class="model-desc">{{ selectedModel.description || '暂无描述' }}</p>
        </el-card>

        <!-- 诊断进度 -->
        <el-card v-if="currentTaskId" class="common-card">
          <template #header>
            <span class="card-title">诊断进度</span>
          </template>
          <el-steps :active="taskStep" direction="vertical">
            <el-step title="任务提交" :description="taskStatus.created_at" />
            <el-step title="排队中" :status="taskStatus.status === 'pending' ? 'processing' : 'finish'" />
            <el-step title="AI推理中" :status="taskStatus.status === 'processing' ? 'processing' : taskStatus.status === 'completed' || taskStatus.status === 'failed' ? 'finish' : 'wait'" />
            <el-step
              title="诊断完成"
              :status="taskStatus.status === 'completed' ? 'success' : taskStatus.status === 'failed' ? 'error' : 'wait'"
              :description="taskStatus.status === 'failed' ? taskStatus.error_msg : ''"
            />
          </el-steps>
        </el-card>

        <!-- 历史诊断记录 -->
        <el-card class="common-card">
          <template #header>
            <span class="card-title">最近诊断记录</span>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="item in recentTasks"
              :key="item.id"
              :type="item.status === 'completed' ? 'primary' : item.status === 'failed' ? 'danger' : 'warning'"
              :timestamp="item.created_at"
            >
              <p>{{ item.model_name }} - {{ item.patient_name || '匿名患者' }}</p>
              <el-button type="primary" link size="small" @click="viewTaskDetail(item)">查看详情</el-button>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>

    <!-- 诊断结果展示 -->
    <el-dialog v-model="resultDialogVisible" title="诊断结果" width="900px" fullscreen>
      <ResultVisual :result="taskResult" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getActiveModels } from '@/api/model'
import { createTask, getTaskStatus, getMyTasks } from '@/api/task'
import PageHeader from '@/components/PageHeader.vue'
import DynamicForm from '@/components/DynamicForm.vue'
import ResultVisual from '@/components/ResultVisual.vue'

const router = useRouter()

const models = ref([])
const selectedModel = ref(null)
const fileList = ref([])
const submitting = ref(false)
const currentTaskId = ref('')
const taskStatus = ref({})
const taskResult = ref(null)
const resultDialogVisible = ref(false)
const recentTasks = ref([])

// 表单数据
const taskForm = reactive({
  modelId: null,
  patientName: '',
  patientId: '',
  gender: '',
  age: null,
  phone: '',
  checkDate: '',
  inputData: {}
})

// 模型分组
const modelGroup = computed(() => {
  const group = {}
  models.value.forEach(model => {
    if (!group[model.model_type]) {
      group[model.model_type] = {
        type: model.model_type,
        label: model.model_type === '单模态' ? '单模态影像模型' : '多模态综合模型',
        models: []
      }
    }
    group[model.model_type].models.push(model)
  })
  return Object.values(group)
})

// 收藏的模型
const favoriteModels = computed(() => {
  const favorites = JSON.parse(localStorage.getItem('favorite_models') || '[]')
  return models.value.filter(model => favorites.includes(model.id))
})

// 是否收藏当前模型
const isFavorite = computed(() => {
  if (!selectedModel.value) return false
  const favorites = JSON.parse(localStorage.getItem('favorite_models') || '[]')
  return favorites.includes(selectedModel.value.id)
})

// 任务步骤
const taskStep = computed(() => {
  const statusMap = {
    pending: 1,
    processing: 2,
    completed: 3,
    failed: 3
  }
  return statusMap[taskStatus.value.status] || 0
})

// 加载模型列表
const loadModels = async () => {
  try {
    models.value = await getActiveModels()
  } catch (error) {
    console.error('加载模型列表失败', error)
  }
}

// 加载最近任务
const loadRecentTasks = async () => {
  try {
    const res = await getMyTasks({ limit: 5 })
    recentTasks.value = res
  } catch (error) {
    console.error('加载最近任务失败', error)
  }
}

// 模型切换
const onModelChange = (modelId) => {
  selectedModel.value = models.value.find(m => m.id === modelId)
  taskResult.value = null
  currentTaskId.value = ''
  taskStatus.value = {}
}

// 文件处理
const handleFileChange = (file) => {
  if (!fileList.value.find(f => f.uid === file.uid)) {
    fileList.value.push(file)
  }
}

const handleFileRemove = (file) => {
  const index = fileList.value.findIndex(f => f.uid === file.uid)
  if (index > -1) fileList.value.splice(index, 1)
}

// 收藏切换
const toggleFavorite = () => {
  if (!selectedModel.value) return
  const favorites = JSON.parse(localStorage.getItem('favorite_models') || '[]')
  const index = favorites.indexOf(selectedModel.value.id)
  if (index > -1) {
    favorites.splice(index, 1)
    ElMessage.success('已取消收藏')
  } else {
    favorites.push(selectedModel.value.id)
    ElMessage.success('收藏成功')
  }
  localStorage.setItem('favorite_models', JSON.stringify(favorites))
}

const removeFavorite = (id) => {
  const favorites = JSON.parse(localStorage.getItem('favorite_models') || '[]')
  const index = favorites.indexOf(id)
  if (index > -1) {
    favorites.splice(index, 1)
    localStorage.setItem('favorite_models', JSON.stringify(favorites))
    ElMessage.success('已取消收藏')
  }
}

// 保存草稿
const handleSaveDraft = () => {
  localStorage.setItem('diagnosis_draft', JSON.stringify(taskForm))
  ElMessage.success('草稿保存成功')
}

// 重置表单
const resetForm = () => {
  Object.keys(taskForm).forEach(key => {
    if (typeof taskForm[key] === 'object' && !Array.isArray(taskForm[key])) {
      taskForm[key] = {}
    } else {
      taskForm[key] = ''
    }
  })
  fileList.value = []
  selectedModel.value = null
  taskResult.value = null
  currentTaskId.value = ''
  taskStatus.value = {}
  ElMessage.success('表单已重置')
}

// 提交诊断
const handleSubmit = async () => {
  if (!taskForm.modelId) {
    ElMessage.warning('请选择AI诊断模型')
    return
  }

  submitting.value = true
  try {
    const formData = new FormData()
    formData.append('model_id', taskForm.modelId)
    Object.keys(taskForm).forEach(key => {
      if (taskForm[key] !== null && taskForm[key] !== '' && key !== 'inputData' && key !== 'modelId') {
        formData.append(key, taskForm[key])
      }
    })
    if (Object.keys(taskForm.inputData).length) {
      formData.append('input_data', JSON.stringify(taskForm.inputData))
    }
    fileList.value.forEach(file => {
      if (file.raw) formData.append('files', file.raw)
    })

    const task = await createTask(formData)
    currentTaskId.value = task.task_id
    ElMessage.success('任务提交成功，正在处理...')

    // 轮询任务状态
    const pollTask = setInterval(async () => {
      const status = await getTaskStatus(task.task_id)
      taskStatus.value = status
      if (status.status === 'completed') {
        clearInterval(pollTask)
        taskResult.value = status.result
        resultDialogVisible.value = true
        ElMessage.success('诊断完成')
        loadRecentTasks()
      } else if (status.status === 'failed') {
        clearInterval(pollTask)
        ElMessage.error('诊断失败: ' + status.error_msg)
      }
    }, 2000)

  } finally {
    submitting.value = false
  }
}

// 查看任务详情
const viewTaskDetail = (item) => {
  if (item.status === 'completed') {
    taskResult.value = item.result
    resultDialogVisible.value = true
  } else {
    router.push('/tasks')
  }
}

// 跳转到任务列表
const goToTaskList = () => {
  router.push('/tasks')
}

onMounted(() => {
  loadModels()
  loadRecentTasks()
  // 加载草稿
  const draft = localStorage.getItem('diagnosis_draft')
  if (draft) {
    Object.assign(taskForm, JSON.parse(draft))
    if (taskForm.modelId) {
      onModelChange(taskForm.modelId)
    }
  }
})
</script>

<style scoped>
.inference-page {
  width: 100%;
}

.model-info .el-descriptions {
  margin-top: 10px;
}

.model-desc {
  line-height: 1.8;
  color: var(--text-regular);
  margin: 0;
}

.upload-tip {
  font-size: 12px;
  color: var(--text-secondary);
}

.submit-section {
  display: flex;
  gap: 20px;
  justify-content: center;
  padding: 30px 0;
}
</style>