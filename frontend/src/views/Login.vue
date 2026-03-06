<template>
  <div class="login-container">
    <el-card class="login-card" shadow="hover">
      <template #header>
        <div class="login-header">
          <h2 class="title">自适应 AI 辅助医疗推理平台</h2>
          <p class="subtitle">专业·高效·智能的医疗AI诊断解决方案</p>
        </div>
      </template>
      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" class="login-form">
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            prefix-icon="User"
            size="large"
            clearable
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            size="large"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" style="width: 100%" :loading="loading" @click="handleLogin">
            登 录
          </el-button>
        </el-form-item>
      </el-form>
      <div class="tips">
        <el-divider content-position="center">测试账号</el-divider>
        <div class="account-list">
          <p><span>管理员账号：</span><code>admin / admin123</code></p>
          <p><span>医生账号：</span><code>doctor / doctor123</code></p>
        </div>
      </div>
    </el-card>
    <div class="footer">
      <p>© 2025 中国石油大学（北京）软件工程专业 毕业设计</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/modules/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const loginFormRef = ref(null)
const loading = ref(false)

// 表单数据（保持原有结构）
const loginForm = reactive({
  username: '',
  password: ''
})

// 表单校验规则
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

// 登录处理函数（核心修复：完整错误捕获 + 参数校验 + 防重复提交）
const handleLogin = async () => {
  // 1. 防重复点击
  if (loading.value) return

  try {
    // 2. 先校验表单（同步校验，确保有返回值）
    const validateResult = await loginFormRef.value.validate()
    if (!validateResult) {
      return // 校验失败直接返回
    }

    // 3. 手动参数校验（去空格 + 非空检查）
    const username = loginForm.username.trim()
    const password = loginForm.password.trim()
    
    if (!username) {
      ElMessage.error('用户名不能为空')
      return
    }
    if (!password) {
      ElMessage.error('密码不能为空')
      return
    }

    // 4. 开始登录流程
    loading.value = true
    
    // 5. 调用 store 中的登录方法（传递处理后的参数）
    await userStore.login(username, password)
    
    // 6. 登录成功处理
    ElMessage.success('登录成功')
    // 延迟跳转，提升用户体验
    setTimeout(() => {
      router.push(userStore.isAdmin ? '/dashboard' : '/inference')
    }, 500)

  } catch (error) {
    // 7. 捕获所有错误（表单校验/接口请求/其他异常）
    console.error('登录失败:', error)
    // 友好的错误提示
    ElMessage.error(error.message || '登录失败，请检查账号密码或网络状态')

  } finally {
    // 8. 无论成功/失败，都关闭加载状态
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: url('https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80') no-repeat center center;
  background-size: cover;
  position: relative;
}

.login-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(15,76,129,0.88) 0%, rgba(26,95,122,0.85) 100%);
}

.login-card {
  width: 440px;
  position: relative;
  z-index: 1;
  border-radius: 16px;
}

.login-header {
  text-align: center;
}

.title {
  margin: 0;
  color: var(--primary-color);
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 1px;
}

.subtitle {
  margin: 8px 0 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.login-form {
  margin-top: 20px;
}

.tips {
  margin-top: 25px;
}

.account-list {
  padding: 10px 0;
}

.account-list p {
  margin: 8px 0;
  font-size: 14px;
  color: var(--text-regular);
  display: flex;
  justify-content: space-between;
}

.account-list code {
  background: var(--bg-hover);
  padding: 2px 8px;
  border-radius: 4px;
  color: var(--primary-dark);
  font-weight: 500;
}

.footer {
  position: absolute;
  bottom: 20px;
  left: 0;
  right: 0;
  text-align: center;
  color: rgba(255,255,255,0.7);
  font-size: 14px;
  z-index: 1;
}

:deep(.el-card__header) {
  padding: 24px 20px;
  border-bottom: 1px solid var(--border-light);
}
</style>