<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '220px'" class="aside-container">
      <div class="logo">
        <!-- <img v-if="isCollapse" src="/favicon.ico" alt="logo" class="logo-mini" /> -->
        <span  class="logo-text">自适应AI辅助医疗平台</span>
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
        <!-- 医生菜单 -->
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
            <el-icon><Scale /></el-icon>
            <template #title>模型对比</template>
          </el-menu-item>
          <el-menu-item index="/teaching">
            <el-icon><Reading /></el-icon>
            <template #title>教学案例库</template>
          </el-menu-item>
        </template>

        <!-- 管理员菜单 -->
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

    <!-- 主内容区 -->
    <el-container class="main-container">
      <el-header class="header-container">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="toggleCollapse">
            <Fold v-if="!isCollapse" />
            <Expand v-else />
          </el-icon>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <div class="user-info">
              <el-avatar :size="32" :src="userStore.userInfo?.avatar" />
              <span class="username">{{ userStore.userInfo?.full_name || userStore.userInfo?.username }}</span>
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

    <!-- 修改密码对话框 -->
    <el-dialog v-model="passwordDialogVisible" title="修改密码" width="500px">
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
import { ref, computed, onMounted, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store/modules/user'
import { useAppStore } from '@/store/modules/app'
import { ElMessageBox, ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const appStore = useAppStore()

const isCollapse = computed(() => appStore.isCollapse)
const activeMenu = computed(() => route.path)
const passwordDialogVisible = ref(false)
const passwordFormRef = ref(null)
const passwordLoading = ref(false)

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 密码校验规则
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

// 切换侧边栏折叠
const toggleCollapse = () => {
  appStore.toggleCollapse()
}

// 下拉菜单操作
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

// 退出登录
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

// 提交修改密码
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

.logo-mini {
  width: 32px;
  height: 32px;
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

.collapse-btn {
  font-size: 18px;
  color: var(--text-regular);
  cursor: pointer;
  transition: color 0.3s;
}

.collapse-btn:hover {
  color: var(--primary-color);
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

/* 页面过渡动画 */
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