<template>
  <slot v-if="hasPermission"></slot>
</template>

<script setup>
import { computed } from 'vue'
import { useUserStore } from '@/store/modules/user'

const props = defineProps({
  role: {
    type: [String, Array],
    default: ''
  }
})

const userStore = useUserStore()

const hasPermission = computed(() => {
  const userRole = userStore.userInfo?.role
  if (!userRole) return false

  if (Array.isArray(props.role)) {
    return props.role.includes(userRole)
  }
  return props.role === userRole
})
</script>