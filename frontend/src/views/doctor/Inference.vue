<template>
  <div class="inference-page">
    <PageHeader
      title="AI辅助诊断"
      description="基于异步架构的多模态医疗智能推理平台"
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
                  <el-input-number v-model="taskForm.age" :min="0" :max="150" style="width: 100%" controls-position="right" />
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

        <el-card class="common-card visual-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="card-title">医学影像与数据上传</span>
              <span class="upload-tip">支持 JPG / PNG / DICOM 影像及 Excel 数据表</span>
            </div>
          </template>
          
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
              accept=".jpg,.jpeg,.png,.dcm,.xlsx,.xls"
            >
              <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
              <div class="el-upload__text">将文件拖到此处，或 <em>点击上传</em></div>
              <template #tip>
                <div class="el-upload__tip text-center">单个文件大小不超过 50MB</div>
              </template>
            </el-upload>

            <div v-show="currentImage" class="preview-area">
              <img :src="currentImage" class="preview-image" alt="医学影像" />
              <canvas ref="resultCanvas" class="result-canvas"></canvas>
              
              <div class="preview-actions">
                <el-tooltip content="清除并重新上传" placement="left">
                  <el-button type="danger" circle icon="Delete" @click="clearImage" />
                </el-tooltip>
              </div>
            </div>
          </div>
          
          <div v-if="currentImage && fileList.length > 1" class="extra-files">
            <el-tag v-for="file in nonImageFiles" :key="file.uid" size="small" type="info" closable @close="handleFileRemove(file, fileList)">
              {{ file.name }}
            </el-tag>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8" class="right-column">
        <el-card class="common-card" shadow="never">
          <template #header>
            <span class="card-title">AI诊断模型选择</span>
          </template>
          
          <el-select
            v-model="taskForm.modelId"
            placeholder="请选择AI诊断模型"
            style="width: 100%; margin-bottom: 16px;"
            @change="onModelChange"
            clearable
            size="large"
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
              >
                <span style="float: left">{{ model.model_name }}</span>
                <span style="float: right; color: var(--el-text-color-secondary); font-size: 12px">
                  v{{ model.model_version }}
                </span>
              </el-option>
            </el-option-group>
          </el-select>

          <div class="favorite-models" v-if="favoriteModels.length > 0">
            <span class="label">常用:</span>
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

        <el-card v-if="selectedModel" class="common-card model-config-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="card-title">配置与特征输入</span>
              <div class="header-actions">
                <el-tag :type="selectedModel.model_type === '单模态' ? 'primary' : 'success'" size="small">
                  {{ selectedModel.model_type }}
                </el-tag>
                <el-button
                  :type="isFavorite ? 'warning' : 'primary'"
                  :icon="isFavorite ? 'StarFilled' : 'Star'"
                  size="small"
                  link
                  @click="toggleFavorite"
                >
                  {{ isFavorite ? '取消' : '收藏' }}
                </el-button>
              </div>
            </div>
          </template>
          
          <div class="model-desc-mini">
            {{ selectedModel.description || '暂无描述' }}
            <div class="metrics">
              <span v-if="selectedModel.accuracy">准确率: {{ selectedModel.accuracy }}</span>
              <span v-if="selectedModel.auc">AUC: {{ selectedModel.auc }}</span>
            </div>
          </div>

          <el-divider border-style="dashed" />
          
          <div class="dynamic-schema">
            <div class="section-title">临床特征录入</div>
            <DynamicForm v-if="selectedModel.input_schema && selectedModel.input_schema.length > 0" v-model="taskForm.inputData" :schema="selectedModel.input_schema" />
            <el-empty v-else description="当前为单模态模型，仅需影像数据" :image-size="60" />
          </div>
        </el-card>

        <div class="submit-section">
          <el-button 
            type="primary" 
            size="large" 
            class="w-full submit-btn" 
            :loading="submitting" 
            :disabled="!taskForm.modelId || fileList.length === 0"
            @click="handleSubmit"
          >
            <el-icon><VideoPlay /></el-icon>
            提交异步推理任务
          </el-button>
          <div class="submit-tip">
            <el-icon><InfoFilled /></el-icon> 任务将排队执行，可稍后在右上角通知或任务列表中查看。
          </div>
        </div>

        <el-card class="common-card history-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="card-title">最近任务追踪</span>
              <el-button type="primary" link size="small" @click="goToTaskList">查看全部</el-button>
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
                <span class="task-model">{{ item.model_name }}</span>
                <span class="task-patient">{{ item.patient_name || '匿名患者' }}</span>
              </div>
              <div class="timeline-status">
                <span v-if="item.status === 'pending'" class="text-warning"><el-icon class="is-loading"><Loading /></el-icon> 排队中</span>
                <span v-else-if="item.status === 'processing'" class="text-primary"><el-icon class="is-loading"><Loading /></el-icon> 推理中</span>
                <span v-else-if="item.status === 'completed'" class="text-success cursor-pointer" @click="viewTaskDetail(item)">查看结果 -></span>
                <span v-else class="text-danger">推理失败</span>
              </div>
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="暂无近期任务" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getActiveModels } from '@/api/model'
import { createTask, getMyTasks } from '@/api/task'
import PageHeader from '@/components/PageHeader.vue'
import DynamicForm from '@/components/DynamicForm.vue'

const router = useRouter()

// 状态变量
const models = ref([])
const selectedModel = ref(null)
const fileList = ref([])
const submitting = ref(false)
const recentTasks = ref([])

// 影像预览专用状态
const imageLoading = ref(false)
const currentImage = ref(null)

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

// 计算非图片的附加文件（如Excel）
const nonImageFiles = computed(() => {
  return fileList.value.filter(f => !f.raw.type.startsWith('image/') && !f.name.endsWith('.dcm'))
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
}

// 文件处理与本地预览
const handleFileChange = (uploadFile, uploadFiles) => {
  fileList.value = uploadFiles
  // 查找第一个图片文件进行大屏预览
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
  // 如果移除的是当前预览的图片，清空预览
  if (uploadFiles.filter(f => f.raw.type.startsWith('image/') || f.name.endsWith('.dcm')).length === 0) {
    currentImage.value = null
  }
}

const clearImage = () => {
  currentImage.value = null
  fileList.value = nonImageFiles.value // 保留非图片文件
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
  currentImage.value = null
  selectedModel.value = null
  ElMessage.success('表单已重置')
}

// 提交异步诊断（核心修改：提交即走，不阻塞等待）
const handleSubmit = async () => {
  if (!taskForm.modelId) {
    ElMessage.warning('请选择AI诊断模型')
    return
  }

  submitting.value = true
  try {
    const formData = new FormData()
    formData.append('model_id', taskForm.modelId)
    
    // 附加基础信息
    Object.keys(taskForm).forEach(key => {
      if (taskForm[key] !== null && taskForm[key] !== '' && key !== 'inputData' && key !== 'modelId') {
        formData.append(key, taskForm[key])
      }
    })
    
    // 附加动态 Schema 数据
    if (Object.keys(taskForm.inputData).length) {
      formData.append('input_data', JSON.stringify(taskForm.inputData))
    }
    
    // 附加文件
    fileList.value.forEach(file => {
      if (file.raw) formData.append('files', file.raw)
    })

    // 提交任务到后端 Celery 队列
    await createTask(formData)
    
    // 提交成功，刷新历史记录，无需等待结果返回
    ElMessage.success('任务已成功提交至推理队列，请留意页面通知。')
    loadRecentTasks()

  } catch (error) {
    ElMessage.error('任务提交失败')
  } finally {
    submitting.value = false
  }
}

// 跳转到任务列表查看结果
const viewTaskDetail = (item) => {
  router.push(`/tasks?taskId=${item.id}`)
}

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
.inference-page { width: 100%; }

.inference-container {
  display: flex;
  align-items: stretch;
}

.left-column, .right-column {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.upload-tip { font-size: 12px; color: var(--text-secondary); }

/* 影像预览区深度定制 */
.visual-card { flex: 1; display: flex; flex-direction: column; }
:deep(.visual-card .el-card__body) { flex: 1; display: flex; flex-direction: column; }

.canvas-container {
  flex: 1; 
  min-height: 450px;
  background: #1e1e1e; /* 医疗影像深色背景 */
  border-radius: 8px;
  display: flex; 
  align-items: center; 
  justify-content: center;
  position: relative; 
  overflow: hidden;
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
.extra-files { margin-top: 12px; display: flex; gap: 8px; flex-wrap: wrap; }

/* 右侧组件样式 */
.favorite-models {
  font-size: 13px;
  color: var(--text-secondary);
  display: flex;
  align-items: flex-start;
  gap: 8px;
}
.favorite-models .label { padding-top: 4px; }
.cursor-pointer { cursor: pointer; }

.model-config-card { flex-shrink: 0; }
.model-desc-mini {
  font-size: 13px;
  color: var(--text-regular);
  line-height: 1.6;
}
.model-desc-mini .metrics { margin-top: 8px; display: flex; gap: 16px; color: var(--text-secondary); }

.section-title { 
  font-size: 14px; font-weight: bold; color: var(--text-primary); 
  margin-bottom: 16px; padding-left: 8px; border-left: 4px solid var(--primary-color);
}

/* 提交按钮区域 */
.w-full { width: 100%; }
.submit-section { text-align: center; }
.submit-btn { border-radius: 8px; font-size: 16px; font-weight: bold; }
.submit-tip { 
  margin-top: 10px; font-size: 12px; color: var(--text-secondary); 
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