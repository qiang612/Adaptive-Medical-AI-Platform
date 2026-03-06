<template>
  <div class="search-bar">
    <el-form :model="searchForm" inline class="search-form">
      <slot></slot>
      <el-form-item v-if="showTimeRange" label="时间范围">
        <el-date-picker
          v-model="searchForm.timeRange"
          type="datetimerange"
          range-separator="至"
          start-placeholder="开始时间"
          end-placeholder="结束时间"
          value-format="YYYY-MM-DD HH:mm:ss"
          style="width: 360px"
          @change="handleSearch"
        />
      </el-form-item>
      <el-form-item v-if="showKeyword" label="关键词">
        <el-input
          v-model="searchForm.keyword"
          :placeholder="keywordPlaceholder"
          clearable
          style="width: 240px"
          @keyup.enter="handleSearch"
        />
      </el-form-item>
    </el-form>
    <div class="search-buttons">
      <el-button type="primary" @click="handleSearch">
        <el-icon><Search /></el-icon>
        搜索
      </el-button>
      <el-button @click="handleReset">
        <el-icon><Refresh /></el-icon>
        重置
      </el-button>
      <slot name="buttons"></slot>
    </div>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue'

const props = defineProps({
  showKeyword: {
    type: Boolean,
    default: true
  },
  showTimeRange: {
    type: Boolean,
    default: false
  },
  keywordPlaceholder: {
    type: String,
    default: '请输入关键词搜索'
  },
  defaultSearchForm: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['search', 'reset'])

const searchForm = reactive({
  keyword: '',
  timeRange: [],
  ...props.defaultSearchForm
})

// 搜索
const handleSearch = () => {
  emit('search', { ...searchForm })
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
  emit('reset', { ...searchForm })
}

// 监听外部默认值变化
watch(
  () => props.defaultSearchForm,
  (newVal) => {
    Object.assign(searchForm, newVal)
  },
  { deep: true }
)
</script>

<style scoped>
.search-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  padding: 16px 20px;
  background: var(--bg-card);
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
}

.search-form {
  flex: 1;
}

.search-buttons {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
}

:deep(.el-form-item) {
  margin-bottom: 0;
}
</style>