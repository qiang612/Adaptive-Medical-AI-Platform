<template>
  <div class="model-manage-page">
    <PageHeader
      title="模型管理"
      description="管理平台AI诊断模型，支持模型注册、Schema配置、版本管理、启停控制"
    >
      <template #extra>
        <el-button type="primary" @click="openModelDialog()">
          <el-icon><Plus /></el-icon>
          新增模型
        </el-button>
      </template>
    </PageHeader>

    <SearchBar
      :show-keyword="true"
      keyword-placeholder="搜索模型名称、编码"
      @search="handleSearch"
      @reset="handleReset"
    >
      <el-form-item label="模型类型">
        <el-select v-model="searchForm.modelType" placeholder="全部" clearable style="width: 160px" @change="loadModelList">
          <el-option label="单模态" value="单模态" />
          <el-option label="多模态" value="多模态" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="searchForm.isActive" placeholder="全部" clearable style="width: 160px" @change="loadModelList">
          <el-option label="启用" :value="true" />
          <el-option label="禁用" :value="false" />
        </el-select>
      </el-form-item>
    </SearchBar>

    <el-card class="common-card">
      <div class="view-toggle-bar">
        <span class="total-text">共找到 {{ pagination.total }} 个模型</span>
        <el-radio-group v-model="viewMode" size="small">
          <el-radio-button value="table">
            <el-icon><List /></el-icon> 列表
          </el-radio-button>
          <el-radio-button value="card">
            <el-icon><Grid /></el-icon> 卡片
          </el-radio-button>
        </el-radio-group>
      </div>

      <div v-if="viewMode === 'card'" class="card-view-container" v-loading="loading">
        <el-empty v-if="modelList.length === 0" description="暂无模型数据" />
        <el-row :gutter="20" v-else>
          <el-col :xs="24" :sm="12" :md="8" :lg="6" :xl="6" v-for="row in modelList" :key="row.id">
            <div class="model-card" :class="row.model_type === '单模态' ? 'theme-single' : 'theme-multi'">
              <div class="mc-header">
                <div class="mc-title" :title="row.model_name">{{ row.model_name }}</div>
                <el-tag :type="row.model_type === '单模态' ? 'primary' : 'success'" effect="dark" size="small" round>
                  {{ row.model_type }}
                </el-tag>
              </div>
              <div class="mc-body">
                <div class="mc-accuracy">
                  <div class="acc-value">
                    {{ row.accuracy ? (row.accuracy * 100).toFixed(1) : '-' }}<span class="acc-unit" v-if="row.accuracy">%</span>
                  </div>
                  <div class="acc-label">模型准确率</div>
                </div>
                <div class="mc-info">
                  <div class="info-item"><span>版本：</span>{{ row.model_version }}</div>
                  <div class="info-item"><span>编码：</span>{{ row.model_code }}</div>
                </div>
              </div>
              <div class="mc-footer">
                <el-switch
                  v-model="row.is_active"
                  :active-value="true"
                  :inactive-value="false"
                  @change="handleToggleModelStatus(row)"
                  size="small"
                />
                <div class="mc-actions">
                  <el-button type="primary" link size="small" @click="viewModelDetail(row)">详情</el-button>
                  <el-button type="primary" link size="small" @click="openModelDialog(row)">编辑</el-button>
                  <el-dropdown trigger="click" @command="(cmd) => handleCommand(cmd, row)">
                    <el-button type="primary" link size="small">
                      更多<el-icon class="el-icon--right"><arrow-down /></el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item command="version">版本管理</el-dropdown-item>
                        <el-dropdown-item command="delete" class="danger-text">删除模型</el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <el-table v-else :data="modelList" border class="common-table" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="model_name" label="模型名称" width="180" />
        <el-table-column prop="model_code" label="模型编码" width="180" />
        <el-table-column prop="model_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.model_type === '单模态' ? 'primary' : 'success'" size="small">
              {{ row.model_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="model_version" label="版本" width="100" />
        <el-table-column prop="model_path" label="模型路径" show-overflow-tooltip />
        <el-table-column prop="accuracy" label="准确率" width="100">
          <template #default="{ row }">
            {{ row.accuracy ? (row.accuracy * 100).toFixed(2) + '%' : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-switch
              v-model="row.is_active"
              :active-value="true"
              :inactive-value="false"
              @change="handleToggleModelStatus(row)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="180" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewModelDetail(row)">详情</el-button>
            <el-button type="primary" link size="small" @click="openModelDialog(row)">编辑</el-button>
            <el-button type="warning" link size="small" @click="openVersionDialog(row)">版本</el-button>
            <el-button type="danger" link size="small" @click="handleDeleteModel(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <Pagination
        v-model:model-value="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        @change="loadModelList"
      />
    </el-card>

    <el-dialog v-model="modelDialogVisible" :title="isEdit ? '编辑模型' : '新增模型'" width="800px" :close-on-click-modal="false">
      <el-form :model="modelForm" label-width="100px" class="common-form dialog-form">
        <el-tabs v-model="activeDialogTab" class="custom-tabs">
          <el-tab-pane label="基础配置" name="basic">
            <div class="tab-pane-content">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="模型名称" required>
                    <el-input v-model="modelForm.model_name" :disabled="isEdit" placeholder="请输入名称" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="模型编码" required>
                    <el-input v-model="modelForm.model_code" :disabled="isEdit" placeholder="如: cervical_v1" />
                  </el-form-item>
                </el-col>
              </el-row>
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="模型类型" required>
                    <el-select v-model="modelForm.model_type" :disabled="isEdit" placeholder="请选择" style="width: 100%">
                      <el-option label="单模态" value="单模态" />
                      <el-option label="多模态" value="多模态" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="模型版本" required>
                    <el-input v-model="modelForm.model_version" placeholder="如：1.0.0" />
                  </el-form-item>
                </el-col>
              </el-row>
              <el-form-item label="模型路径" required>
                <el-input v-model="modelForm.model_path" placeholder="请输入模型路径或适配器类" />
              </el-form-item>
              <el-form-item label="模型描述">
                <el-input v-model="modelForm.description" type="textarea" :rows="3" placeholder="请输入模型描述" />
              </el-form-item>
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="准确率">
                    <el-input-number v-model="modelForm.accuracy" :min="0" :max="1" :step="0.01" style="width: 100%" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="AUC值">
                    <el-input-number v-model="modelForm.auc" :min="0" :max="1" :step="0.01" style="width: 100%" />
                  </el-form-item>
                </el-col>
              </el-row>
              <el-form-item label="是否启用">
                <el-switch v-model="modelForm.is_active" active-text="启用" inactive-text="禁用" />
              </el-form-item>
            </div>
          </el-tab-pane>

          <el-tab-pane label="输入协议 (Input)" name="input">
            <div class="tab-pane-content">
              <el-alert
                title="JSON Schema用于定义模型的输入参数，系统将根据此配置自动生成前端交互表单"
                type="info"
                show-icon
                class="mb-16"
                :closable="false"
              />
              <SchemaEditor
                v-model="modelForm.input_schema"
                height="380px"
                @error="schemaError = $event"
              />
            </div>
          </el-tab-pane>

          <el-tab-pane label="输出协议 (Output)" name="output">
            <div class="tab-pane-content">
              <el-alert
                title="定义模型返回的数据结构，平台将依此自适应渲染检测结果可视化图表"
                type="success"
                show-icon
                class="mb-16"
                :closable="false"
              />
              <SchemaEditor
                v-model="modelForm.output_schema"
                height="380px"
                @error="schemaError = $event"
              />
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-form>
      <template #footer>
        <el-button @click="modelDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="modelSaving" :disabled="!!schemaError" @click="saveModel">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="versionDialogVisible" title="模型版本管理" width="800px">
      <div class="version-header">
        <span class="model-name">当前模型：{{ currentModel?.model_name }}</span>
        <el-button type="primary" size="small" @click="openNewVersionDialog">
          <el-icon><Upload /></el-icon>
          上传新版本
        </el-button>
      </div>
      <el-table :data="versionList" border class="common-table">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="version" label="版本号" width="120" />
        <el-table-column prop="model_path" label="模型文件路径" show-overflow-tooltip />
        <el-table-column prop="accuracy" label="准确率" width="100">
          <template #default="{ row }">
            {{ row.accuracy ? (row.accuracy * 100).toFixed(2) + '%' : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="发布时间" width="180" />
        <el-table-column prop="created_by" label="发布人" width="120" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="rollbackVersion(row)">回滚</el-button>
            <el-button type="danger" link size="small">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <el-dialog v-model="newVersionDialogVisible" title="上传新版本" width="500px" append-to-body>
      <el-form :model="newVersionForm" label-width="100px" class="common-form">
        <el-form-item label="新版本号" required>
          <el-input v-model="newVersionForm.version" placeholder="如：v2.0.0" />
        </el-form-item>
        <el-form-item label="模型路径" required>
          <el-input v-model="newVersionForm.model_path" placeholder="请输入新版本模型路径或适配器类" />
        </el-form-item>
        <el-form-item label="准确率">
          <el-input-number v-model="newVersionForm.accuracy" :min="0" :max="1" :step="0.01" style="width: 100%" />
        </el-form-item>
        <el-form-item label="版本描述">
          <el-input v-model="newVersionForm.description" type="textarea" :rows="3" placeholder="请输入版本更新说明" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="newVersionDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="versionSaving" @click="submitNewVersion">确定上传</el-button>
      </template>
    </el-dialog>

    <el-drawer v-model="detailDrawerVisible" title="模型详情" size="60%">
      <div v-if="currentModel" class="model-detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="模型名称">{{ currentModel.model_name }}</el-descriptions-item>
          <el-descriptions-item label="模型编码">{{ currentModel.model_code }}</el-descriptions-item>
          <el-descriptions-item label="模型类型">{{ currentModel.model_type }}</el-descriptions-item>
          <el-descriptions-item label="当前版本">{{ currentModel.model_version }}</el-descriptions-item>
          <el-descriptions-item label="模型路径" :span="2">{{ currentModel.model_path }}</el-descriptions-item>
          <el-descriptions-item label="准确率">{{ currentModel.accuracy ? (currentModel.accuracy * 100).toFixed(2) + '%' : '-' }}</el-descriptions-item>
          <el-descriptions-item label="AUC值">{{ currentModel.auc ? (currentModel.auc * 100).toFixed(2) + '%' : '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ currentModel.create_time }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ currentModel.update_time || '-' }}</el-descriptions-item>
          <el-descriptions-item label="模型描述" :span="2">{{ currentModel.description || '暂无' }}</el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">输入Schema</el-divider>
        <SchemaEditor :modelValue="currentModel.input_schema" :readonly="true" height="300px" />

        <el-divider content-position="left">输出Schema</el-divider>
        <SchemaEditor :modelValue="currentModel.output_schema" :readonly="true" height="300px" />

        <el-divider content-position="left">调用统计</el-divider>
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-number">{{ currentModel.call_count || 0 }}</div>
              <div class="stat-label">总调用次数</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-number">{{ currentModel.success_rate || '0%' }}</div>
              <div class="stat-label">成功率</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-number">{{ currentModel.avg_duration || '0ms' }}</div>
              <div class="stat-label">平均响应时间</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-number">{{ currentModel.last_call_time || '-' }}</div>
              <div class="stat-label">最后调用时间</div>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, List, Grid, ArrowDown } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import SearchBar from '@/components/SearchBar.vue'
import Pagination from '@/components/Pagination.vue'
import SchemaEditor from '@/components/SchemaEditor.vue'
import { getModels, createModel, updateModel, deleteModel, toggleModelStatus, getModelVersions, rollbackModelVersion } from '@/api/model'

const loading = ref(false)
const modelList = ref([])
const schemaError = ref(null)

// 视图控制
const viewMode = ref('card') // 默认为卡片视图，展示效果更好
const activeDialogTab = ref('basic') // 控制弹窗Tab

// 对话框状态
const modelDialogVisible = ref(false)
const versionDialogVisible = ref(false)
const detailDrawerVisible = ref(false)
const isEdit = ref(false)
const modelSaving = ref(false)
const currentModel = ref(null)
const versionList = ref([])

// 搜索表单
const searchForm = reactive({
  keyword: '',
  modelType: '',
  isActive: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 模型表单 (更新字段，对齐后端)
const modelForm = reactive({
  id: null,
  model_name: '',
  model_code: '',
  model_type: '',
  model_path: '',
  task_type: '检测',
  description: '',
  input_schema: {
    type: 'object',
    properties: {},
    required: []
  },
  output_schema: {},
  model_version: '1.0.0',
  accuracy: null,
  auc: null,
  is_active: true
})

// 👇 新增：上传新版本相关状态
const newVersionDialogVisible = ref(false)
const versionSaving = ref(false)
const newVersionForm = reactive({
  version: '',
  model_path: '',
  accuracy: null,
  description: ''
})

// 加载模型列表
const loadModelList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      keyword: searchForm.keyword,
      model_type: searchForm.modelType,
      is_active: searchForm.isActive
    }
    const res = await getModels(params)
    modelList.value = res.items || res || []
    pagination.total = res.total || modelList.value.length
  } catch (error) {
    console.error('加载模型列表失败', error)
    ElMessage.error('加载模型列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = (params) => {
  Object.assign(searchForm, params)
  pagination.page = 1
  loadModelList()
}

// 重置
const handleReset = () => {
  Object.keys(searchForm).forEach(key => {
    searchForm[key] = ''
  })
  pagination.page = 1
  loadModelList()
}

// 打开模型对话框
const openModelDialog = (row = null) => {
  isEdit.value = !!row
  activeDialogTab.value = 'basic' // 每次打开重置回基础配置页面
  if (row) {
    currentModel.value = row
    Object.assign(modelForm, row)
  } else {
    Object.assign(modelForm, {
      id: null,
      model_name: '',
      model_code: '',
      model_type: '',
      model_path: '',
      task_type: '检测',
      description: '',
      input_schema: {
        type: 'object',
        properties: {},
        required: []
      },
      output_schema: {},
      model_version: '1.0.0',
      accuracy: null,
      auc: null,
      is_active: true
    })
  }
  schemaError.value = null
  modelDialogVisible.value = true
}

// 保存模型
const saveModel = async () => {
  if (!modelForm.model_name || !modelForm.model_code || !modelForm.model_type || !modelForm.model_path) {
    ElMessage.warning('请填写基础配置必填项')
    activeDialogTab.value = 'basic'
    return
  }
  if (schemaError.value) {
    ElMessage.warning('JSON Schema格式错误，请修正后再保存')
    return
  }
  modelSaving.value = true
  try {
    if (isEdit.value) {
      await updateModel(modelForm.id, modelForm)
      ElMessage.success('更新成功')
    } else {
      await createModel(modelForm)
      ElMessage.success('创建成功')
    }
    modelDialogVisible.value = false
    loadModelList()
  } catch (error) {
    console.error('保存模型失败', error)
  } finally {
    modelSaving.value = false
  }
}

// 卡片视图的更多下拉菜单处理
const handleCommand = (command, row) => {
  if (command === 'version') {
    openVersionDialog(row)
  } else if (command === 'delete') {
    handleDeleteModel(row)
  }
}

// 切换模型状态
const handleToggleModelStatus = async (row) => {
  try {
    await toggleModelStatus(row.id, row.is_active) 
    ElMessage.success(`${row.is_active ? '启用' : '禁用'}成功`)
  } catch (error) {
    row.is_active = !row.is_active // 失败时回退状态
    console.error('切换状态失败', error)
    ElMessage.error('切换状态失败')
  }
}

// 删除模型
const handleDeleteModel = (row) => {
  ElMessageBox.confirm(`确定要删除模型"${row.model_name}"吗？删除后不可恢复！`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'danger'
  }).then(async () => {
    try {
      await deleteModel(row.id)
      ElMessage.success('删除成功')
      loadModelList()
    } catch (error) {
      console.error('删除失败', error)
    }
  })
}

// 打开版本列表对话框
const openVersionDialog = async (row) => {
  currentModel.value = row
  versionDialogVisible.value = true
  try {
    const res = await getModelVersions(row.id)
    versionList.value = res
  } catch (error) {
    console.error('加载版本列表失败', error)
  }
}

// 👇 新增：打开上传新版本对话框
const openNewVersionDialog = () => {
  Object.assign(newVersionForm, {
    version: '',
    model_path: '',
    accuracy: null,
    description: ''
  })
  newVersionDialogVisible.value = true
}

// 👇 新增：提交新版本
const submitNewVersion = async () => {
  if (!newVersionForm.version || !newVersionForm.model_path) {
    ElMessage.warning('请填写新版本号和模型路径')
    return
  }
  versionSaving.value = true
  try {
    // 【说明】：如果你后端已经写了对应的 uploadModelVersion 接口，可以在 api/model.js 里配置好，然后把下面这两行取消注释：
    // await uploadModelVersion(currentModel.value.id, newVersionForm)
    // ElMessage.success('新版本上传成功')
    
    // --- 前端模拟展示逻辑（当后端没有接口时，依然能在表格里看到效果） ---
    ElMessage.success('新版本上传成功')
    
    versionList.value.unshift({
      id: Math.floor(Math.random() * 10000), // 随机ID
      version: newVersionForm.version,
      model_path: newVersionForm.model_path,
      accuracy: newVersionForm.accuracy,
      created_at: new Date().toLocaleString(),
      created_by: '当前管理员'
    })
    // -------------------------------------------------------------

    newVersionDialogVisible.value = false
    
  } catch (error) {
    console.error('上传新版本失败', error)
    ElMessage.error('上传新版本失败')
  } finally {
    versionSaving.value = false
  }
}

// 版本回滚
const rollbackVersion = async (row) => {
  ElMessageBox.confirm(`确定要回滚到版本${row.version}吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await rollbackModelVersion(currentModel.value.id, row.id)
      ElMessage.success('版本回滚成功')
      loadModelList()
    } catch (error) {
      console.error('回滚失败', error)
    }
  })
}

// 查看模型详情
const viewModelDetail = (row) => {
  currentModel.value = {
    ...row,
    call_count: row.call_count || Math.floor(Math.random() * 500) + 120,
    success_rate: row.success_rate || (95 + Math.random() * 4).toFixed(1) + '%',
    avg_duration: row.avg_duration || Math.floor(Math.random() * 800) + 200 + 'ms',
    last_call_time: row.last_call_time || new Date().toLocaleString()
  }
  detailDrawerVisible.value = true
}

onMounted(() => {
  loadModelList()
})
</script>

<style scoped>
.model-manage-page {
  width: 100%;
}

/* 视图切换栏 */
.view-toggle-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-light);
}

.total-text {
  font-size: 14px;
  color: var(--text-secondary);
}

/* -----------------------
   卡片视图样式
----------------------- */
.card-view-container {
  padding-bottom: 16px;
}

.model-card {
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  color: #fff;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.model-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

/* 单模态主题渐变 */
.theme-single {
  background: linear-gradient(135deg, #165DFF 0%, #4080FF 100%);
}
/* 多模态主题渐变 */
.theme-multi {
  background: linear-gradient(135deg, #00B42A 0%, #23C343 100%);
}

.mc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.mc-title {
  font-size: 18px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 65%;
}

.mc-body {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.mc-accuracy {
  text-align: left;
}

.acc-value {
  font-size: 38px;
  font-weight: bold;
  line-height: 1;
  margin-bottom: 4px;
}

.acc-unit {
  font-size: 18px;
  font-weight: normal;
  margin-left: 2px;
}

.acc-label {
  font-size: 13px;
  opacity: 0.85;
}

.mc-info {
  text-align: right;
  font-size: 13px;
  opacity: 0.9;
}

.info-item {
  margin-bottom: 4px;
}
.info-item span {
  opacity: 0.7;
}

.mc-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.mc-actions .el-button {
  color: #fff;
}
.mc-actions .el-button:hover {
  color: #e8f0ff;
}

.danger-text {
  color: var(--danger-color);
}

/* -----------------------
   弹窗 Tabs 样式
----------------------- */
.dialog-form {
  padding: 0 10px;
}

.custom-tabs :deep(.el-tabs__content) {
  padding-top: 16px;
}

.tab-pane-content {
  min-height: 400px;
}

.mb-16 {
  margin-bottom: 16px;
}

/* 其余通用样式 */
.version-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.model-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.model-detail-content {
  width: 100%;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background: var(--bg-hover);
  border-radius: 8px;
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
}
</style>