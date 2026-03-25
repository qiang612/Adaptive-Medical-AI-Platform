<template>
  <div class="inference-page">
    <PageHeader
      title=" AI 辅助诊断"
      description="基于智能模型的多模态病情分析与辅助筛查"
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

    <el-row :gutter="20" class="inference-container">
      <el-col :span="16" class="left-column">
        <el-card class="common-card patient-card" shadow="never">
          <template #header>
            <span class="card-title">患者基础信息</span>
          </template>
          <el-form :model="taskForm" label-position="top" class="common-form" size="default">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="患者姓名">
                  <el-input v-model="taskForm.patientName" placeholder="请输入患者姓名" clearable />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="患者ID (门诊/住院号)">
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
                  <el-input-number v-model="taskForm.age" :min="0" :max="150" style="width: 100%" controls-position="right" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="联系方式">
                  <el-input v-model="taskForm.phone" placeholder="请输入手机号" clearable />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="就诊日期">
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

        <el-card class="common-card data-input-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="card-title">诊断数据录入</span>
              <el-tag v-if="selectedModel" :type="selectedModel.model_type === '单模态' ? 'primary' : 'success'" effect="light">
                当前适配：{{ selectedModel.model_type }} AI 模型
              </el-tag>
            </div>
          </template>

          <div v-if="!selectedModel" class="empty-model-state">
            <el-empty description="👉 请先在右侧选择 AI 诊断模型，系统将自动生成所需的数据输入项" :image-size="120" />
          </div>

          <div v-else class="adaptive-input-area">
            
            <div class="input-section">
              <div class="section-title">
                <span class="step-num">1</span> 上传医学影像资料
                <span class="upload-tip">(支持 JPG / PNG / DICOM 格式)</span>
              </div>
              
              <div class="canvas-container" v-loading="imageLoading">
                <el-upload
                  v-show="!currentImage"
                  class="upload-area"
                  drag
                  multiple
                  action="#"
                  :auto-upload="false"
                  :on-change="handleFileChange"
                  :on-remove="handleFileRemove"
                  :file-list="fileList"
                  accept=".jpg,.jpeg,.png,.dcm"
                >
                  <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
                  <div class="el-upload__text">将影像文件拖到此处，或 <em>点击上传</em></div>
                  <template #tip>
                    <div class="el-upload__tip text-center">系统将自动进行影像脱敏与预处理，单文件不超过 50MB</div>
                  </template>
                </el-upload>

                <div v-show="currentImage" class="preview-area">
                  <img :src="currentImage" class="preview-image" alt="医学影像预览" />
                  <div class="preview-actions">
                    <el-tooltip content="清除并重新上传" placement="left">
                      <el-button type="danger" circle icon="Delete" @click="clearImage" />
                    </el-tooltip>
                  </div>
                </div>
              </div>
            </div>

            <el-divider v-if="selectedModel && selectedModel.input_schema && Object.keys(selectedModel.input_schema || {}).length > 0" border-style="dashed" />

            <div v-if="selectedModel && selectedModel.input_schema && Object.keys(selectedModel.input_schema || {}).length > 0" class="input-section">
              <div class="section-title">
                <span class="step-num">2</span> 补充临床与检验特征 <el-tag size="small" type="warning" class="ml-2">多模态所需</el-tag>
              </div>
              <div class="dynamic-form-wrapper">
                <el-alert title="请尽量完整填写以下指标，以提升 AI 联合诊断的准确率。" type="info" show-icon :closable="false" style="margin-bottom: 16px;" />
                <DynamicForm v-model="taskForm.inputData" :schema="selectedModel.input_schema" />
              </div>
            </div>
            
            <div v-if="selectedModel.model_type === '多模态混合'" class="input-section" style="margin-top: 20px;">
               <div class="section-title">
                <span class="step-num">3</span> 批量检验数据上传 (可选)
              </div>
              <el-upload
                action="#"
                :auto-upload="false"
                :on-change="handleExtraFileChange"
                :on-remove="handleExtraFileRemove"
                :file-list="extraFileList"
                accept=".xlsx,.xls,.csv"
              >
                <el-button type="primary" plain size="small"><el-icon><Paperclip /></el-icon> 附加 Excel/CSV 数据表</el-button>
              </el-upload>
            </div>

          </div>
        </el-card>
      </el-col>

      <el-col :span="8" class="right-column">
        
        <el-card class="common-card model-select-card" shadow="never">
          <template #header>
            <span class="card-title"><el-icon><Cpu /></el-icon> 选择 AI 诊断模型</span>
          </template>
          
          <el-select
            v-model="taskForm.modelId"
            placeholder="请选择适用的 AI 诊断模型"
            style="width: 100%; margin-bottom: 16px;"
            @change="onModelChange"
            clearable
            size="large"
          >
            <el-option-group v-for="group in modelGroup" :key="group.type" :label="group.label">
              <el-option
                v-for="model in group.models"
                :key="model.id"
                :label="model.model_name"
                :value="model.id"
              >
                <span style="float: left">{{ model.model_name }}</span>
                <span style="float: right; color: var(--el-text-color-secondary); font-size: 12px">
                  {{ model.model_version }}
                </span>
              </el-option>
            </el-option-group>
          </el-select>

          <div v-if="selectedModel" class="model-brief">
            <div class="brief-title">
              模型简介
              <el-button :type="isFavorite ? 'warning' : 'primary'" :icon="isFavorite ? 'StarFilled' : 'Star'" size="small" link @click="toggleFavorite">
                {{ isFavorite ? '已收藏' : '收藏' }}
              </el-button>
            </div>
            <p>{{ selectedModel.description || '该模型暂无详细描述。' }}</p>
            <div class="metrics" v-if="selectedModel.accuracy || selectedModel.auc">
              <el-tag size="small" type="info" v-if="selectedModel.accuracy">准确率: {{ selectedModel.accuracy }}</el-tag>
              <el-tag size="small" type="info" v-if="selectedModel.auc">AUC: {{ selectedModel.auc }}</el-tag>
            </div>
          </div>

          <div class="favorite-models" v-if="favoriteModels.length > 0 && !selectedModel">
            <span class="label">常用模型:</span>
            <el-space wrap>
              <el-tag
                v-for="model in favoriteModels"
                :key="model.id"
                type="info"
                effect="plain"
                closable
                class="cursor-pointer"
                @click="taskForm.modelId = model.id; onModelChange(model.id)"
                @close="removeFavorite(model.id)"
              >
                {{ model.model_name }}
              </el-tag>
            </el-space>
          </div>
        </el-card>

        <div class="submit-section">
          <el-button 
            type="primary" 
            size="large" 
            class="w-full submit-btn" 
            :loading="submitting" 
            :disabled="!taskForm.modelId || (fileList.length === 0 && !Object.keys(taskForm.inputData).length)"
            @click="handleSubmit"
          >
            <el-icon><Monitor /></el-icon>
            开始 AI 智能分析
          </el-button>
          <div class="submit-tip">
            <el-icon><InfoFilled /></el-icon> 诊断请求将在后台安全进行，报告生成后将提醒您。
          </div>
        </div>

        <el-card class="common-card history-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="card-title">今日诊断记录</span>
              <el-button type="primary" link size="small" @click="goToTaskList">进入工作台</el-button>
            </div>
          </template>
          <el-timeline v-if="recentTasks.length > 0">
            <el-timeline-item
              v-for="item in recentTasks"
              :key="item.id"
              :type="item.status === 'completed' ? 'success' : item.status === 'failed' ? 'danger' : 'warning'"
              :timestamp="item.created_at"
              size="large"
            >
              <div class="timeline-content">
                <span class="task-model">{{ models.find(m => m.id == item.model_id)?.model_name || item.model_name }}</span>
                <span class="task-patient">患者: {{ item.patient_name || '匿名' }}</span>
              </div>
              <div class="timeline-status">
                <span v-if="item.status === 'pending'" class="text-warning"><el-icon class="is-loading"><Loading /></el-icon> 等待分析</span>
                <span v-else-if="item.status === 'processing'" class="text-primary"><el-icon class="is-loading"><Loading /></el-icon> AI 分析中...</span>
                <span v-else-if="item.status === 'completed'" class="text-success cursor-pointer" @click="viewTaskDetail(item)">报告已生成，点击查看 <el-icon><ArrowRight /></el-icon></span>
                <span v-else class="text-danger d-flex-center">
                  分析失败
                  <el-tooltip v-if="item.error_msg" :content="item.error_msg" placement="top">
                    <el-icon class="ml-1 cursor-pointer"><InfoFilled /></el-icon>
                  </el-tooltip>
                </span>
              </div>
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="暂无进行中的诊断" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getActiveModels } from '@/api/model'
import { createTask, getMyTasks } from '@/api/task'
import PageHeader from '@/components/PageHeader.vue'
import DynamicForm from '@/components/DynamicForm.vue'

const router = useRouter()
const route = useRoute()

// 状态变量
const models = ref([])
const selectedModel = ref(null)
const fileList = ref([])      // 影像文件
const extraFileList = ref([]) // Excel等附加文件
const submitting = ref(false)
const recentTasks = ref([])
let pollTimer = null // 用于保存轮询定时器
let polling = false // 轮询控制标志，防止请求堆积

// 影像预览专用状态
const imageLoading = ref(false)
const currentImage = ref(null)

const getToday = () => {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

// 表单数据
const taskForm = reactive({
  modelId: null,
  patientName: '',
  patientId: '',
  gender: '',
  age: null,
  phone: '',
  checkDate: getToday(),
  inputData: {}
})

// 模型分组逻辑
const modelGroup = computed(() => {
  const group = {}
  models.value.forEach(model => {
    if (!group[model.model_type]) {
      group[model.model_type] = {
        type: model.model_type,
        label: model.model_type.includes('单模态') ? '单模态专病模型 (仅需影像)' : '多模态联合诊断模型 (影像+临床指标)',
        models: []
      }
    }
    group[model.model_type].models.push(model)
  })
  return Object.values(group)
})

const favoriteModels = computed(() => {
  const favorites = JSON.parse(localStorage.getItem('favorite_models') || '[]')
  return models.value.filter(model => favorites.includes(model.id))
})

const isFavorite = computed(() => {
  if (!selectedModel.value) return false
  const favorites = JSON.parse(localStorage.getItem('favorite_models') || '[]')
  return favorites.includes(selectedModel.value.id)
})

const loadModels = async () => {
  try {
    const res = await getActiveModels()
    // 解析 JSON
    models.value = res.map(model => {
      model.id = Number(model.id)
      if (typeof model.input_schema === 'string') {
        try {
          model.input_schema = JSON.parse(model.input_schema)
        } catch (e) {
          model.input_schema = {}
        }
      }
      return model
    })
  } catch (error) {
    console.error('加载模型列表失败', error)
  }
}

const loadRecentTasks = async () => {
  try {
    const res = await getMyTasks({ limit: 4 })
    recentTasks.value = res.items || res || []
  } catch (error) {
    console.error('加载最近任务失败', error)
  }
}

// 轮询刷新机制：使用递归setTimeout确保上一次请求完成后再发起下一次，避免请求堆积
const startPolling = async () => {
  if (polling) return
  polling = true
  
  const poll = async () => {
    if (!polling) return
    const hasProcessing = recentTasks.value.some(t => t.status === 'pending' || t.status === 'processing')
    if (hasProcessing) {
      await loadRecentTasks()
      pollTimer = setTimeout(poll, 3000)
    } else {
      polling = false
    }
  }
  poll()
}

// 核心自适应逻辑：模型切换时清空旧数据
const onModelChange = (modelId) => {
  selectedModel.value = null
  taskForm.inputData = {}
  currentImage.value = null
  fileList.value = []
  extraFileList.value = []

  if (!modelId) return

  setTimeout(() => {
    const targetModel = models.value.find(m => String(m.id) === String(modelId))
    if (targetModel) {
      selectedModel.value = targetModel
    }
  }, 50)
}

// 影像文件处理
const handleFileChange = (uploadFile, uploadFiles) => {
  fileList.value = uploadFiles
  const imageFile = uploadFiles.find(f => f.raw.type.startsWith('image/') || f.name.endsWith('.dcm'))
  
  if (imageFile && !currentImage.value) {
    imageLoading.value = true
    const reader = new FileReader()
    reader.onload = (e) => {
      currentImage.value = e.target.result
      imageLoading.value = false
    }
    reader.readAsDataURL(imageFile.raw)
  }
}

const handleFileRemove = (file, uploadFiles) => {
  fileList.value = uploadFiles
  if (uploadFiles.filter(f => f.raw.type.startsWith('image/') || f.name.endsWith('.dcm')).length === 0) {
    currentImage.value = null
  }
}

const clearImage = () => {
  currentImage.value = null
  fileList.value = [] 
}

const handleExtraFileChange = (uploadFile, uploadFiles) => { extraFileList.value = uploadFiles }
const handleExtraFileRemove = (file, uploadFiles) => { extraFileList.value = uploadFiles }

const toggleFavorite = () => {
  if (!selectedModel.value) return
  const favorites = JSON.parse(localStorage.getItem('favorite_models') || '[]')
  const index = favorites.indexOf(selectedModel.value.id)
  if (index > -1) {
    favorites.splice(index, 1)
    ElMessage.success('已取消收藏')
  } else {
    favorites.push(selectedModel.value.id)
    ElMessage.success('已添加到常用模型')
  }
  localStorage.setItem('favorite_models', JSON.stringify(favorites))
}

const removeFavorite = (id) => {
  const favorites = JSON.parse(localStorage.getItem('favorite_models') || '[]')
  const index = favorites.indexOf(id)
  if (index > -1) {
    favorites.splice(index, 1)
    localStorage.setItem('favorite_models', JSON.stringify(favorites))
  }
}

const handleSaveDraft = () => {
  localStorage.setItem('diagnosis_draft', JSON.stringify(taskForm))
  ElMessage.success('患者信息草稿保存成功')
}

const resetForm = () => {
  Object.keys(taskForm).forEach(key => {
    if (typeof taskForm[key] === 'object' && !Array.isArray(taskForm[key])) {
      taskForm[key] = {}
    } else {
      taskForm[key] = ''
    }
  })
  taskForm.checkDate = getToday()
  fileList.value = []
  extraFileList.value = []
  currentImage.value = null
  selectedModel.value = null
  ElMessage.success('表单已重置')
}

// 提交 AI 诊断
const handleSubmit = async () => {
  if (!taskForm.modelId) {
    ElMessage.warning('请选择诊断模型')
    return
  }

  submitting.value = true
  try {
    const formData = new FormData()
    formData.append('model_id', taskForm.modelId)
    
    // 映射表
    const fieldMap = {
      patientName: 'patient_name',
      patientId: 'patient_id',
      checkDate: 'check_date',
      phone: 'phone',
      gender: 'gender',
      age: 'age'
    }

    // 附加患者基础信息
    Object.keys(taskForm).forEach(key => {
      if (taskForm[key] !== null && taskForm[key] !== '' && key !== 'inputData' && key !== 'modelId') {
        const backendKey = fieldMap[key] || key
        formData.append(backendKey, taskForm[key])
      }
    })
    
    if (Object.keys(taskForm.inputData).length) {
      formData.append('input_data', JSON.stringify(taskForm.inputData))
    }
    
    const allFiles = [...fileList.value, ...extraFileList.value]
    allFiles.forEach(file => {
      if (file.raw) formData.append('files', file.raw)
    })

    await createTask(formData)
    
    ElMessage.success({
      message: '诊断请求已提交，AI 正在后台为您分析，请稍后查看结果。',
      duration: 4000
    })
    
    await loadRecentTasks() 
    startPolling() 

  } catch (error) {
    ElMessage.error('请求提交失败，请检查网络或联系管理员')
  } finally {
    submitting.value = false
  }
}

const viewTaskDetail = (item) => {
  router.push(`/tasks?taskId=${item.id}`)
}

const goToTaskList = () => {
  router.push('/tasks')
}

onMounted(async () => {
  await loadModels()
  await loadRecentTasks()
  startPolling() // 初始化挂载时如果存在任务，也开启轮询
  
  // ✅ 修复：接收通过 URL 传递的所有患者参数并进行表单自动填充
  if (route.query.patient_name || route.query.patient_id) {
    taskForm.patientId = route.query.patient_id || ''
    taskForm.patientName = route.query.patient_name || ''
    taskForm.gender = route.query.gender || ''
    taskForm.age = route.query.age ? Number(route.query.age) : null
    taskForm.phone = route.query.phone || ''
  } else {
    const draft = localStorage.getItem('diagnosis_draft')
    if (draft) {
      const parsedDraft = JSON.parse(draft)
      Object.assign(taskForm, parsedDraft)
      
      if (!taskForm.checkDate) {
        taskForm.checkDate = getToday()
      }
      
      if (taskForm.modelId) {
        onModelChange(taskForm.modelId)
      }
    }
  }
})

// 组件销毁时清除定时器，避免内存泄漏
onUnmounted(() => {
  polling = false
  if (pollTimer) clearTimeout(pollTimer)
})
</script>

<style scoped>
.inference-page { width: 100%; }

.inference-container { display: flex; align-items: stretch; }
.left-column, .right-column { display: flex; flex-direction: column; gap: 20px; }

.card-header { display: flex; justify-content: space-between; align-items: center; }
.card-title { font-size: 16px; font-weight: 600; color: var(--text-primary); display: flex; align-items: center; gap: 8px;}

/* 自适应数据录入区特有样式 */
.empty-model-state {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--el-fill-color-light);
  border-radius: 8px;
  border: 1px dashed var(--el-border-color);
}

.adaptive-input-area {
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.input-section { margin-bottom: 24px; }
.section-title { 
  font-size: 15px; font-weight: bold; color: var(--text-primary); 
  margin-bottom: 16px; display: flex; align-items: center; gap: 8px;
}
.step-num {
  display: inline-flex; justify-content: center; align-items: center;
  width: 20px; height: 20px; background-color: var(--el-color-primary);
  color: #fff; border-radius: 50%; font-size: 12px;
}
.upload-tip { font-size: 12px; color: var(--text-secondary); font-weight: normal;}
.ml-1 { margin-left: 4px; }
.ml-2 { margin-left: 8px; }
.d-flex-center { display: inline-flex; align-items: center; }

/* 影像预览区深度定制 */
.canvas-container {
  min-height: 280px;
  background: #1e1e1e; /* 医疗影像深色背景 */
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  position: relative; overflow: hidden;
  border: 1px dashed var(--border-color);
}
.upload-area { width: 100%; padding: 0 40px; }
:deep(.el-upload-dragger) { background: transparent; border: none; }
:deep(.el-upload__text) { color: #888; }
.text-center { text-align: center; }

.preview-area { 
  position: relative; width: 100%; height: 100%; 
  display: flex; align-items: center; justify-content: center; 
}
.preview-image { max-width: 100%; max-height: 100%; object-fit: contain; }
.result-canvas { position: absolute; top: 0; left: 0; pointer-events: none; }
.preview-actions { position: absolute; top: 16px; right: 16px; z-index: 10; }

/* 右侧模型选择面板样式 */
.model-brief {
  margin-top: 16px; padding: 16px;
  background-color: var(--el-fill-color-light); border-radius: 8px;
}
.brief-title { font-size: 13px; font-weight: bold; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;}
.model-brief p { font-size: 13px; color: var(--text-regular); line-height: 1.5; margin: 0 0 12px 0;}
.metrics { display: flex; gap: 8px; }

.favorite-models { font-size: 13px; color: var(--text-secondary); display: flex; align-items: flex-start; gap: 8px; margin-top: 12px;}
.favorite-models .label { padding-top: 4px; flex-shrink: 0;}
.cursor-pointer { cursor: pointer; }

/* 提交按钮区域 */
.w-full { width: 100%; }
.submit-section { text-align: center; margin: 10px 0;}
.submit-btn { 
  border-radius: 12px; font-size: 16px; font-weight: bold; 
  padding: 24px 0; box-shadow: 0 4px 12px rgba(22, 93, 255, 0.2);
}
.submit-tip { 
  margin-top: 12px; font-size: 12px; color: var(--text-secondary); 
  display: flex; align-items: center; justify-content: center; gap: 4px;
}

/* 历史记录 */
.history-card { flex: 1; overflow-y: auto; }
.timeline-content { display: flex; flex-direction: column; gap: 4px; }
.task-model { font-weight: bold; color: var(--text-primary); font-size: 14px; }
.task-patient { font-size: 13px; color: var(--text-secondary); }
.timeline-status { margin-top: 8px; font-size: 13px; }

.text-warning { color: var(--el-color-warning); }
.text-primary { color: var(--el-color-primary); }
.text-success { color: var(--el-color-success); font-weight: bold; }
.text-danger { color: var(--el-color-danger); }
</style>