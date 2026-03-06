import { useUserStore } from '@/store/modules/user'

// 检查角色权限
export function hasRole(role) {
  const userStore = useUserStore()
  const userRole = userStore.userInfo?.role
  if (!userRole) return false

  if (Array.isArray(role)) {
    return role.includes(userRole)
  }
  return role === userRole
}