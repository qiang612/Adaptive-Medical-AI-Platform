<template>
  <el-tag :type="tagType" :size="size" :effect="effect">
    {{ tagText }}
  </el-tag>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: [String, Number, Boolean],
    required: true
  },
  typeMap: {
    type: Object,
    default: () => ({
      active: 'success',
      inactive: 'info',
      pending: 'warning',
      processing: 'primary',
      completed: 'success',
      failed: 'danger',
      true: 'success',
      false: 'info'
    })
  },
  textMap: {
    type: Object,
    default: () => ({
      active: '启用',
      inactive: '禁用',
      pending: '等待中',
      processing: '处理中',
      completed: '已完成',
      failed: '失败',
      true: '是',
      false: '否'
    })
  },
  size: {
    type: String,
    default: 'default'
  },
  effect: {
    type: String,
    default: 'light'
  }
})

const tagType = computed(() => {
  return props.typeMap[props.status] || 'info'
})

const tagText = computed(() => {
  return props.textMap[props.status] || props.status
})
</script>