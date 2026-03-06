<template>
  <div class="page-header">
    <div class="page-header-left">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item v-for="item in breadcrumbList" :key="item.path">
          <span v-if="item.last">{{ item.title }}</span>
          <router-link v-else :to="item.path">{{ item.title }}</router-link>
        </el-breadcrumb-item>
      </el-breadcrumb>
      <h2 class="page-title">{{ title }}</h2>
      <p v-if="description" class="page-description">{{ description }}</p>
    </div>
    <div class="page-header-right">
      <slot name="extra"></slot>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  description: {
    type: String,
    default: ''
  }
})

const route = useRoute()

// 面包屑列表
const breadcrumbList = computed(() => {
  const matched = route.matched.filter(item => item.meta?.title && item.path !== '/')
  return matched.map((item, index) => ({
    title: item.meta.title,
    path: item.path,
    last: index === matched.length - 1
  }))
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-light);
}

.page-header-left {
  flex: 1;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 12px 0 8px;
  line-height: 1.3;
}

.page-description {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

.page-header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

:deep(.el-breadcrumb__inner) {
  font-weight: 500;
}

:deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) {
  color: var(--primary-color);
  font-weight: 600;
}
</style>