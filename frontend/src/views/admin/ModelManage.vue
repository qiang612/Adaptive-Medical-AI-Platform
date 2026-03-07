<template>
  <div class="model-manage-page">
    <PageHeader
      title="模型管理"
      description="管理平台AI诊断模型，支持模型注册、Schema配置、版本管理、启停控制"
    >
      <template #extra>
        <el-button type="primary" @click="openModelDialog">
          <el-icon><Plus /></el-icon>
          新增模型
        </el-button>
      </template>
    </PageHeader>

    <!-- 搜索筛选区 -->
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

    <!-- 模型列表 -->
    <el-card class="common-card">
      <el-table :data="modelList" border class="common-table" v-loading="loading">
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
        <el-table-column prop="adapter_class" label="适配器类" show-overflow-tooltip />
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
        <el-table-column prop="created_at" label="创建时间" width="180" />
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

    <!-- 模型编辑对话框 -->
    <el-dialog v-model="modelDialogVisible" :title="isEdit ? '编辑模型' : '新增模型'" width="800px" :close-on-click-modal="false">
      <el-form :model="modelForm" label-width="120px" class="common-form">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="模型名称" required>
              <el-input v-model="modelForm.model_name" :disabled="isEdit" placeholder="请输入模型名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="模型编码" required>
              <el-input v-model="modelForm.model_code" :disabled="isEdit" placeholder="请输入模型唯一编码" />
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
        <el-form-item label="适配器类" required>
          <el-input v-model="modelForm.adapter_class" placeholder="如：app.ai_adapters.cervical_adapter.CervicalAdapter" />
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

        <el-divider content-position="left">输入Schema配置</el-divider>
        <el-alert
          title="JSON Schema用于定义模型的输入参数，系统将根据此配置自动生成前端交互表单"
          type="info"
          show-icon
          class="mb-20"
        />
        <SchemaEditor
          v-model="modelForm.input_schema"
          height="300px"
          @error="schemaError = $event"
        />

        <el-divider content-position="left">输出Schema配置</el-divider>
        <SchemaEditor
          v-model="modelForm.output_schema"
          height="300px"
          @error="schemaError = $event"
        />
      </el-form>
      <template #footer>
        <el-button @click="modelDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="modelSaving" :disabled="schemaError" @click="saveModel">保存</el-button>
      </template>
    </el-dialog>

    <!-- 版本管理对话框 -->
    <el-dialog v-model="versionDialogVisible" title="模型版本管理" width="800px">
      <div class="version-header">
        <span class="model-name">当前模型：{{ currentModel?.model_name }}</span>
        <el-button type="primary" size="small">
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

    <!-- 模型详情抽屉 -->
    <el-drawer v-model="detailDrawerVisible" title="模型详情" size="60%">
      <div v-if="currentModel" class="model-detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="模型名称">{{ currentModel.model_name }}</el-descriptions-item>
          <el-descriptions-item label="模型编码">{{ currentModel.model_code }}</el-descriptions-item>
          <el-descriptions-item label="模型类型">{{ currentModel.model_type }}</el-descriptions-item>
          <el-descriptions-item label="当前版本">{{ currentModel.model_version }}</el-descriptions-item>
          <el-descriptions-item label="适配器类" :span="2">{{ currentModel.adapter_class }}</el-descriptions-item>
          <el-descriptions-item label="准确率">{{ currentModel.accuracy ? (currentModel.accuracy * 100).toFixed(2) + '%' : '-' }}</el-descriptions-item>
          <el-descriptions-item label="AUC值">{{ currentModel.auc ? (currentModel.auc * 100).toFixed(2) + '%' : '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ currentModel.created_at }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ currentModel.updated_at }}</el-descriptions-item>
          <el-descriptions-item label="模型描述" :span="2">{{ currentModel.description || '暂无' }}</el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">输入Schema</el-divider>
        <SchemaEditor :model-value="currentModel.input_schema" :readonly="true" height="300px" />

        <el-divider content-position="left">输出Schema</el-divider>
        <SchemaEditor :model-value="currentModel.output_schema" :readonly="true" height="300px" />

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
import PageHeader from '@/components/PageHeader.vue'
import SearchBar from '@/components/SearchBar.vue'
import Pagination from '@/components/Pagination.vue'
import SchemaEditor from '@/components/SchemaEditor.vue'
import { getModels, createModel, updateModel, deleteModel, toggleModelStatus, getModelVersions, rollbackModelVersion } from '@/api/model'

const loading = ref(false)
const modelList = ref([])
const schemaError = ref(null)

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

// 模型表单
const modelForm = reactive({
  id: null,
  model_name: '',
  model_code: '',
  model_type: '',
  adapter_class: '',
  description: '',
  input_schema: {},
  output_schema: {},
  model_version: '1.0.0',
  accuracy: null,
  auc: null,
  is_active: true
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
  if (row) {
    currentModel.value = row
    Object.assign(modelForm, row)
  } else {
    Object.assign(modelForm, {
      id: null,
      model_name: '',
      model_code: '',
      model_type: '',
      adapter_class: '',
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
  if (!modelForm.model_name || !modelForm.model_code || !modelForm.model_type || !modelForm.adapter_class) {
    ElMessage.warning('请填写必填项')
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

// 切换模型状态
const handleToggleModelStatus = async (row) => {
  try {
    // 这里的 toggleModelStatus 是从 api 导入的接口函数
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

// 打开版本对话框
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
  currentModel.value = row
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

.mb-20 {
  margin-bottom: 20px;
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