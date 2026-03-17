<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="aside-container">
      <div class="logo">
        <span v-if="!isCollapse" class="logo-text">自适应AI辅助医疗平台</span>
        <span v-else class="logo-text">AI</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        :collapse="isCollapse"
        :collapse-transition="false"
        background-color="transparent"
        text-color="#d1e8f5"
        active-text-color="#ffffff"
        unique-opened
      >
        <template v-if="userStore.userInfo?.role === 'doctor'">
          <el-menu-item index="/inference">
            <el-icon><DataAnalysis /></el-icon>
            <template #title>AI诊断</template>
          </el-menu-item>
          <el-menu-item index="/tasks">
            <el-icon><List /></el-icon>
            <template #title>我的任务</template>
          </el-menu-item>
          <el-menu-item index="/patient">
            <el-icon><UserFilled /></el-icon>
            <template #title>病例管理</template>
          </el-menu-item>
          <el-menu-item index="/statistics">
            <el-icon><TrendCharts /></el-icon>
            <template #title>统计分析</template>
          </el-menu-item>
          <el-menu-item index="/model-compare">
            <el-icon><Operation /></el-icon>
            <template #title>模型对比</template>
          </el-menu-item>
          <el-menu-item index="/teaching">
            <el-icon><Reading /></el-icon>
            <template #title>教学案例库</template>
          </el-menu-item>
        </template>

        <template v-if="userStore.userInfo?.role === 'admin'">
          <el-menu-item index="/dashboard">
            <el-icon><Odometer /></el-icon>
            <template #title>数据看板</template>
          </el-menu-item>
          <el-menu-item index="/admin/models">
            <el-icon><Box /></el-icon>
            <template #title>模型管理</template>
          </el-menu-item>
          <el-menu-item index="/admin/users">
            <el-icon><User /></el-icon>
            <template #title>用户管理</template>
          </el-menu-item>
          <el-menu-item index="/admin/tasks">
            <el-icon><Monitor /></el-icon>
            <template #title>任务监控</template>
          </el-menu-item>
          <el-menu-item index="/admin/system">
            <el-icon><Setting /></el-icon>
            <template #title>系统设置</template>
          </el-menu-item>
          <el-menu-item index="/admin/logs">
            <el-icon><Document /></el-icon>
            <template #title>日志审计</template>
          </el-menu-item>
        </template>
      </el-menu>
    </el-aside>

    <el-container class="main-container">
      <el-header class="header-container">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="toggleCollapse">
            <Fold v-if="!isCollapse" />
            <Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/" class="header-breadcrumb">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-for="item in breadcrumbList" :key="item.path">
              <span v-if="item.last">{{ item.title }}</span>
              <router-link v-else :to="item.path">{{ item.title }}</router-link>
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-right">
          <el-badge :value="unreadTasks" :hidden="unreadTasks === 0" class="task-badge" type="danger">
            <el-icon class="header-icon" @click="handleBellClick">
              <Bell />
            </el-icon>
          </el-badge>

          <el-dropdown @command="handleCommand">
            <div class="user-info">
              <el-avatar :size="32" :src="userStore.userInfo?.avatar || 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'" />
              <span class="username">{{ userStore.userInfo?.full_name || userStore.userInfo?.username || '翟旭强' }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="password">修改密码</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>

    <el-dialog v-model="passwordDialogVisible" title="修改密码" width="500px" append-to-body>
      <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="100px">
        <el-form-item label="原密码" prop="oldPassword">
          <el-input v-model="passwordForm.oldPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="passwordForm.newPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirmPassword">
          <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="passwordLoading" @click="handlePasswordSubmit">确认修改</el-button>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, reactive, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store/modules/user'
import { useAppStore } from '@/store/modules/app'
import { ElMessageBox, ElMessage, ElNotification } from 'element-plus'
import request from '@/api/index' // 假设你项目里有统一的 request 请求工具，没有的话可以使用 axios 或 fetch

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const appStore = useAppStore()

const isCollapse = computed(() => appStore.isCollapse)
const activeMenu = computed(() => route.path)
const passwordDialogVisible = ref(false)
const passwordFormRef = ref(null)
const passwordLoading = ref(false)

// 任务通知状态
const unreadTasks = ref(0)
let pollingTimer = null

// 🔥 新增：向后端获取真实未读通知数量 🔥
const fetchUnreadCount = async () => {
  try {
    // 这里的接口路径对应你后端的 @router.get("/unread-count")
    // 如果你没有封装统一的 request，这里可以用 fetch:
    // const res = await fetch('/api/v1/notifications/unread-count', { headers: { Authorization: 'Bearer ' + userStore.token }})
    // const data = await res.json()
    // unreadTasks.value = data.count
    
    const res = await request.get('/notifications/unread-count')
    
    // 如果发现数量增加了，弹出提示框 (可选，为了增加交互体验)
    if (res.data?.count > unreadTasks.value) {
      ElNotification({
        title: '新通知',
        message: '您的AI推理任务有了新进展，请点击铃铛查看。',
        type: 'success',
        duration: 3000
      })
    }
    
    unreadTasks.value = res.data?.count || 0
  } catch (error) {
    console.error('获取未读通知失败:', error)
  }
}

// 🔥 新增：点击小铃铛的逻辑 (清空数量并跳转) 🔥
const handleBellClick = async () => {
  // 1. 根据角色跳转到对应的任务页面
  router.push(userStore.userInfo?.role === 'admin' ? '/admin/tasks' : '/tasks')
  
  // 2. 如果当前有未读消息，调用后端一键已读接口
  if (unreadTasks.value > 0) {
    try {
      // 对应后端的 @router.post("/read-all")
      await request.post('/notifications/read-all')
      // 接口调用成功后，本地小红点清零
      unreadTasks.value = 0
    } catch (error) {
      console.error('标记已读失败:', error)
    }
  }
}

// 初始化真实的后台轮询
const initTaskNotification = () => {
  // 刚进页面时，先查一次
  fetchUnreadCount()
  
  // 每隔 30 秒向后端轮询一次真实未读数据 (可根据需要调整时间)
  pollingTimer = setInterval(() => {
    fetchUnreadCount()
  }, 30000)
}

// 面包屑计算逻辑
const breadcrumbList = computed(() => {
  const matched = route.matched.filter(item => item.meta?.title && item.path !== '/')
  return matched.map((item, index) => ({
    title: item.meta.title,
    path: item.path,
    last: index === matched.length - 1
  }))
})

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  oldPassword: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const toggleCollapse = () => {
  appStore.toggleCollapse()
}

const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人中心功能开发中')
      break
    case 'password':
      passwordDialogVisible.value = true
      break
    case 'logout':
      handleLogout()
      break
  }
}

const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    userStore.logout()
    router.push('/login')
    ElMessage.success('退出成功')
  })
}

const handlePasswordSubmit = async () => {
  await passwordFormRef.value.validate()
  passwordLoading.value = true
  try {
    // 后续对接后端修改密码接口
    ElMessage.success('密码修改成功')
    passwordDialogVisible.value = false
    passwordFormRef.value.resetFields()
  } finally {
    passwordLoading.value = false
  }
}

onMounted(async () => {
  if (!userStore.userInfo) {
    await userStore.getUserInfo()
  }
  // 初始化全局任务真实数据轮询
  initTaskNotification()
})

// 组件销毁前清除定时器避免内存泄漏
onBeforeUnmount(() => {
  if (pollingTimer) clearInterval(pollingTimer)
})
</script>

<style scoped>
.layout-container {
  width: 100%;
  height: 100%;
}

.aside-container {
  background: linear-gradient(180deg, #0f4c81 0%, #1a5f7a 100%);
  box-shadow: 2px 0 8px rgba(0,0,0,0.1);
  transition: width 0.3s ease;
  overflow: hidden;
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  background: rgba(0,0,0,0.1);
}

.logo-text {
  font-size: 18px;
  font-weight: bold;
  color: #fff;
  letter-spacing: 1px;
}

.main-container {
  height: 100vh;
  overflow: hidden;
}

.header-container {
  background: #fff;
  border-bottom: 1px solid var(--border-light);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 64px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px; 
}

.header-breadcrumb {
  margin-top: 2px;
}

.collapse-btn {
  font-size: 18px;
  color: var(--text-regular);
  cursor: pointer;
  transition: color 0.3s;
}

.collapse-btn:hover {
  color: var(--primary-color);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 24px;
}

.header-icon {
  font-size: 20px;
  color: var(--text-regular);
  cursor: pointer;
  transition: color 0.3s;
  display: flex;
  align-items: center;
}

.header-icon:hover {
  color: var(--primary-color);
}

.task-badge {
  line-height: 1;
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.username {
  font-size: 14px;
  color: var(--text-regular);
  font-weight: 500;
}

.main-content {
  background: var(--bg-page);
  padding: 20px;
  overflow-y: auto;
  height: calc(100vh - 64px);
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(10px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}

:deep(.el-menu) {
  border-right: none;
  background: transparent;
}

:deep(.el-menu-item) {
  color: #d1e8f5;
  margin: 4px 8px;
  border-radius: 4px;
  width: calc(100% - 16px);
}

:deep(.el-menu-item:hover),
:deep(.el-menu-item.is-active) {
  background: rgba(255,255,255,0.2);
  color: #fff;
}

:deep(.el-menu-item.is-active) {
  background: var(--primary-color);
}
</style>