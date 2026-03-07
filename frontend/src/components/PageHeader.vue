<template>
  <div class="page-header-compact">
    <div class="title-wrapper">
      <div class="title-indicator"></div>
      <span class="compact-title">{{ title }}</span>
      <el-tooltip v-if="description" :content="description" placement="right" effect="light">
        <el-icon class="info-icon"><InfoFilled /></el-icon>
      </el-tooltip>
    </div>
    <div class="extra-actions">
      <slot name="extra"></slot>
    </div>
  </div>
</template>

<script setup>
// 定义组件接收的属性
defineProps({
  title: {
    type: String,
    required: true, // 标题是必填项
    default: ''
  },
  description: {
    type: String,
    default: '' // 描述是选填项，没有时不显示提示图标
  }
})
</script>

<style scoped>
.page-header-compact {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 12px 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,21,41,0.04);
}
.title-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}
.title-indicator {
  width: 4px;
  height: 16px;
  background-color: var(--el-color-primary);
  border-radius: 2px;
}
.compact-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}
.info-icon {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  cursor: help;
}
</style>