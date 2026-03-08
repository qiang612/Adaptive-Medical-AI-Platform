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
          class="date-picker-item"
          @change="handleSearch"
        />
      </el-form-item>
      
      <el-form-item v-if="showKeyword" label="关键词">
        <el-input
          v-model="searchForm.keyword"
          :placeholder="keywordPlaceholder"
          clearable
          class="keyword-item"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </el-form-item>
    </el-form>

    <div class="search-buttons">
      <el-button type="primary" @click="handleSearch">
        <el-icon style="margin-right: 4px"><Search /></el-icon>搜索
      </el-button>
      <el-button @click="handleReset">
        <el-icon style="margin-right: 4px"><Refresh /></el-icon>重置
      </el-button>
      <slot name="buttons"></slot> 
    </div>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue'
import { Search, Refresh } from '@element-plus/icons-vue'

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
  padding: 20px 20px 4px 20px; 
  background: var(--bg-card, #ffffff);
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.search-form {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
}

/* 统一控制所有表单项的间距 */
:deep(.el-form-item) {
  margin-right: 24px;
  margin-bottom: 16px;
}

/* 美化标签字体 */
:deep(.el-form-item__label) {
  font-weight: 500;
  color: var(--text-regular, #606266);
}

/* 尺寸微调 */
.date-picker-item {
  width: 340px !important;
}

.keyword-item {
  width: 260px;
}

/* 独立出来的按钮组：强制靠右下角对齐 */
.search-buttons {
  display: flex;
  justify-content: flex-end; /* 靠右对齐 */
  align-items: center;
  gap: 12px;
  margin-top: -4px; /* 消除多余的垂直间距 */
  padding-bottom: 16px; /* 与上面的 form-item 的 margin-bottom 保持视觉平衡 */
  border-top: 1px dashed transparent; /* 预留给未来加分割线的空间 */
}
</style>