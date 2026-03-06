<template>
  <div class="pagination-container">
    <el-pagination
      :current-page="currentPage"
      :page-size="innerPageSize"
      :page-sizes="[10, 20, 50, 100]"
      :layout="layout"
      :total="total"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    ></el-pagination> <!-- 关键：添加闭合标签 -->
  </div>
</template>

<script setup>
import { computed, watch, defineProps, defineEmits } from 'vue'

// 定义组件属性
const props = defineProps({
  modelValue: { // 对应当前页码的 v-model 绑定
    type: Number,
    default: 1
  },
  pageSize: { // 对应每页条数的 v-model 绑定
    type: Number,
    default: 10
  },
  total: {
    type: Number,
    required: true
  },
  layout: {
    type: String,
    default: 'total, sizes, prev, pager, next, jumper'
  }
})

// 定义事件
const emit = defineEmits(['update:modelValue', 'update:pageSize', 'change'])

// 计算属性封装当前页码（实现双向绑定）
const currentPage = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// 计算属性封装每页条数（实现双向绑定）
const innerPageSize = computed({
  get: () => props.pageSize,
  set: (val) => emit('update:pageSize', val)
})

// 处理每页条数变化
const handleSizeChange = (val) => {
  innerPageSize.value = val // 通过计算属性触发 update:pageSize 事件
  emit('change', { page: currentPage.value, pageSize: val })
}

// 处理当前页码变化
const handleCurrentChange = (val) => {
  currentPage.value = val // 通过计算属性触发 update:modelValue 事件
  emit('change', { page: val, pageSize: props.pageSize })
}

// 监听总条数变化，防止页码超出范围
watch(
  () => props.total,
  () => {
    if (currentPage.value > 1 && props.total <= (currentPage.value - 1) * props.pageSize) {
      currentPage.value = 1
    }
  }
)
</script>

<style scoped>
.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>