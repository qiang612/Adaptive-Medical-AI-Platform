import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/modules/user'
import { ElMessage } from 'element-plus' // 新增：用于权限提示

// 路由配置
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layout/Layout.vue'),
    redirect: '/inference',
    meta: { requiresAuth: true },
    children: [
      // 医生端路由
      {
        path: 'inference',
        name: 'Inference',
        component: () => import('@/views/doctor/Inference.vue'),
        meta: { title: 'AI辅助诊断', role: 'doctor' }
      },
      {
        path: 'tasks',
        name: 'TaskList',
        component: () => import('@/views/doctor/TaskList.vue'),
        meta: { title: '我的诊断任务', role: 'doctor' }
      },
      {
        path: 'patient',
        name: 'PatientManage',
        component: () => import('@/views/doctor/PatientManage.vue'),
        meta: { title: '病例管理', role: 'doctor' }
      },
      {
        path: 'patient/:id',
        name: 'PatientDetail',
        component: () => import('@/views/doctor/PatientDetail.vue'),
        meta: { title: '患者详情', role: 'doctor', hidden: true }
      },
      {
        path: 'statistics',
        name: 'Statistics',
        component: () => import('@/views/doctor/Statistics.vue'),
        meta: { title: '统计分析', role: 'doctor' }
      },
      {
        path: 'model-compare',
        name: 'ModelCompare',
        component: () => import('@/views/doctor/ModelCompare.vue'),
        meta: { title: '模型对比诊断', role: 'doctor' }
      },
      {
        path: 'teaching',
        name: 'TeachingCase',
        component: () => import('@/views/doctor/TeachingCase.vue'),
        meta: { title: '教学案例库', role: 'doctor' }
      },
      {
        path: 'teaching/:id',
        name: 'CaseDetail',
        component: () => import('@/views/doctor/CaseDetail.vue'),
        meta: { title: '案例详情', role: 'doctor', hidden: true }
      },

      // 管理员端路由
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/admin/Dashboard.vue'),
        meta: { title: '数据看板', role: 'admin' }
      },
      {
        path: 'admin/models',
        name: 'ModelManage',
        component: () => import('@/views/admin/ModelManage.vue'),
        meta: { title: '模型管理', role: 'admin' }
      },
      {
        path: 'admin/users',
        name: 'UserManage',
        component: () => import('@/views/admin/UserManage.vue'),
        meta: { title: '用户管理', role: 'admin' }
      },
      {
        path: 'admin/tasks',
        name: 'TaskMonitor',
        component: () => import('@/views/admin/TaskMonitor.vue'),
        meta: { title: '任务监控', role: 'admin' }
      },
      {
        path: 'admin/system',
        name: 'SystemSetting',
        component: () => import('@/views/admin/SystemSetting.vue'),
        meta: { title: '系统设置', role: 'admin' }
      },
      {
        path: 'admin/logs',
        name: 'LogAudit',
        component: () => import('@/views/admin/LogAudit.vue'),
        meta: { title: '日志审计', role: 'admin' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL), // 修复：添加 BASE_URL 适配不同环境
  routes
})

// 路由守卫（修复无限重定向 + 完善权限校验）
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const token = userStore.token
  const userRole = userStore.userInfo?.role // 获取用户角色

  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 自适应AI辅助医疗推理平台` : '自适应AI辅助医疗推理平台'

  // 1. 不需要登录的页面（登录页）
  if (!to.meta.requiresAuth) {
    // 已登录用户访问登录页 → 跳转到对应角色的首页
    if (token) {
      const targetPath = userRole === 'admin' ? '/dashboard' : '/inference'
      // 关键修复：判断是否已经是目标路径，避免无限循环
      if (to.path !== targetPath) {
        next(targetPath)
      } else {
        next() // 已经是目标路径，直接放行
      }
    } else {
      next() // 未登录用户正常访问登录页
    }
    return // 终止后续逻辑，避免重复调用 next
  }

  // 2. 需要登录但未登录 → 跳转到登录页
  if (!token) {
    ElMessage.warning('请先登录系统')
    // 关键修复：记录跳转前的路径，登录后可返回
    next({ path: '/login', query: { redirect: to.fullPath } })
    return
  }

  // 3. 已登录但用户信息未加载完成 → 先加载用户信息
  if (token && !userRole) {
    // 异步加载用户信息
    userStore.getUserInfo().then(() => {
      // 重新执行权限校验
      checkRolePermission(to, next)
    }).catch(() => {
      // 加载用户信息失败 → 退出登录
      userStore.logout()
      next('/login')
    })
    return
  }

  // 4. 角色权限校验
  checkRolePermission(to, next)
})

/**
 * 角色权限校验函数（抽离逻辑，避免重复代码）
 * @param {RouteLocationNormalized} to 目标路由
 * @param {Function} next 路由跳转函数
 */
function checkRolePermission(to, next) {
  const userStore = useUserStore()
  const userRole = userStore.userInfo?.role
  const requiredRole = to.meta.role

  // 无角色限制的页面（理论上不会出现，兜底处理）
  if (!requiredRole) {
    next()
    return
  }

  // 角色匹配 → 正常放行
  if (requiredRole === userRole) {
    next()
  } else {
    // 角色不匹配 → 跳转到对应角色的首页并提示
    ElMessage.error(`无${requiredRole === 'admin' ? '管理员' : '医生'}权限，无法访问该页面`)
    const targetPath = userRole === 'admin' ? '/dashboard' : '/inference'
    
    // 关键修复：判断是否已经是目标路径，避免无限循环
    if (to.path !== targetPath) {
      next(targetPath)
    } else {
      next()
    }
  }
}

export default router