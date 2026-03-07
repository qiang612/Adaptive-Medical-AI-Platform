<template>
  <div class="user-manage-page">
    <PageHeader
      title="用户管理"
      description="管理平台所有用户账户，支持用户增删改查、角色分配、密码重置、状态管理"
    >
      <template #extra>
        <el-button type="primary" @click="openUserDialog">
          <el-icon><Plus /></el-icon>
          新增用户
        </el-button>
      </template>
    </PageHeader>

    <!-- 搜索筛选区 -->
    <SearchBar
      :show-keyword="true"
      keyword-placeholder="搜索用户名、姓名、手机号、邮箱"
      @search="handleSearch"
      @reset="handleReset"
    >
      <el-form-item label="角色">
        <el-select v-model="searchForm.role" placeholder="全部" clearable style="width: 160px" @change="loadUserList">
          <el-option label="管理员" value="admin" />
          <el-option label="医生" value="doctor" />
          <el-option label="实习生" value="intern" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="searchForm.isActive" placeholder="全部" clearable style="width: 160px" @change="loadUserList">
          <el-option label="启用" :label="true" />
          <el-option label="禁用" :label="false" />
        </el-select>
      </el-form-item>
      <el-form-item label="部门">
        <el-select v-model="searchForm.department" placeholder="全部" clearable style="width: 160px" @change="loadUserList">
          <el-option label="妇产科" value="妇产科" />
          <el-option label="放射科" value="放射科" />
          <el-option label="心内科" value="心内科" />
          <el-option label="内分泌科" value="内分泌科" />
          <el-option label="眼科" value="眼科" />
        </el-select>
      </el-form-item>
    </SearchBar>

    <!-- 用户列表 -->
    <el-card class="common-card">
      <el-table :data="userList" border class="common-table" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="用户信息" width="200">
          <template #default="{ row }">
            <div class="user-info-cell">
              <el-avatar :size="40" :src="row.avatar">
                {{ row.full_name?.charAt(0) || row.username?.charAt(0) }}
              </el-avatar>
              <div class="user-info">
                <div class="user-name">{{ row.full_name || row.username }}</div>
                <div class="user-meta">
                  @{{ row.username }}
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : row.role === 'doctor' ? 'primary' : 'info'" size="small">
              {{ row.role === 'admin' ? '管理员' : row.role === 'doctor' ? '医生' : '实习生' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="department" label="部门" width="120" />
        <el-table-column prop="phone" label="手机号" width="130">
          <template #default="{ row }">
            {{ row.phone ? row.phone.replace(/^(.{3})(.+)(.{4})$/, '$1****$3') : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" show-overflow-tooltip />
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-switch
              v-model="row.is_active"
              :active-value="true"
              :inactive-value="false"
              @change="handleToggleUserStatus(row)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="last_login_at" label="最后登录" width="180">
          <template #default="{ row }">
            {{ row.last_login_at || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewUserDetail(row)">
              详情
            </el-button>
            <el-button type="primary" link size="small" @click="openUserDialog(row)">
              编辑
            </el-button>
            <el-button type="warning" link size="small" @click="resetPassword(row)">
              重置密码
            </el-button>
            <el-popconfirm
              title="确定要删除这个用户吗？"
              @confirm="handleDeleteUser(row)"
            >
              <template #reference>
                <el-button type="danger" link size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <Pagination
        v-model:model-value="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        @change="loadUserList"
      />
    </el-card>

    <!-- 用户编辑对话框 -->
    <el-dialog v-model="userDialogVisible" :title="isEdit ? '编辑用户' : '新增用户'" width="700px" :close-on-click-modal="false">
      <el-form :model="userForm" :rules="userRules" ref="userFormRef" label-width="120px" class="common-form">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用户名" prop="username">
              <el-input v-model="userForm.username" :disabled="isEdit" placeholder="请输入登录用户名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="姓名" prop="fullName">
              <el-input v-model="userForm.full_name" placeholder="请输入真实姓名" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20" v-if="!isEdit">
          <el-col :span="12">
            <el-form-item label="密码" prop="password">
              <el-input v-model="userForm.password" type="password" placeholder="请输入登录密码" show-password />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input v-model="userForm.confirm_password" type="password" placeholder="请再次输入密码" show-password />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="角色" prop="role">
              <el-select v-model="userForm.role" placeholder="请选择角色" style="width: 100%">
                <el-option label="管理员" value="admin" />
                <el-option label="医生" value="doctor" />
                <el-option label="实习生" value="intern" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="部门">
              <el-select v-model="userForm.department" placeholder="请选择部门" clearable style="width: 100%">
                <el-option label="妇产科" value="妇产科" />
                <el-option label="放射科" value="放射科" />
                <el-option label="心内科" value="心内科" />
                <el-option label="内分泌科" value="内分泌科" />
                <el-option label="眼科" value="眼科" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="手机号">
              <el-input v-model="userForm.phone" placeholder="请输入手机号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱">
              <el-input v-model="userForm.email" placeholder="请输入邮箱" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="职称">
          <el-select v-model="userForm.title" placeholder="请选择职称" clearable style="width: 300px">
            <el-option label="住院医师" value="住院医师" />
            <el-option label="主治医师" value="主治医师" />
            <el-option label="副主任医师" value="副主任医师" />
            <el-option label="主任医师" value="主任医师" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="userForm.remark" type="textarea" :rows="3" placeholder="请输入备注信息" />
        </el-form-item>
        <el-form-item label="是否启用">
          <el-switch v-model="userForm.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="userDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="userSaving" @click="saveUser">保存</el-button>
      </template>
    </el-dialog>

    <!-- 密码重置对话框 -->
    <el-dialog v-model="passwordDialogVisible" title="重置密码" width="500px">
      <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="120px" class="common-form">
        <el-form-item label="用户名">
          <el-input v-model="passwordForm.username" disabled />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="passwordForm.new_password" type="password" placeholder="请输入新密码" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="passwordForm.confirm_password" type="password" placeholder="请再次输入新密码" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="passwordSaving" @click="confirmResetPassword">确认重置</el-button>
      </template>
    </el-dialog>

    <!-- 用户详情抽屉 -->
    <el-drawer v-model="detailDrawerVisible" title="用户详情" size="40%">
      <div v-if="currentUser" class="user-detail-content">
        <div class="profile-section">
          <el-avatar :size="80" :src="currentUser.avatar">
            {{ currentUser.full_name?.charAt(0) || currentUser.username?.charAt(0) }}
          </el-avatar>
          <div class="profile-info">
            <h3>{{ currentUser.full_name || currentUser.username }}</h3>
            <el-tag :type="currentUser.role === 'admin' ? 'danger' : 'primary'" size="large">
              {{ currentUser.role === 'admin' ? '管理员' : currentUser.role === 'doctor' ? '医生' : '实习生' }}
            </el-tag>
          </div>
        </div>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="用户名">{{ currentUser.username }}</el-descriptions-item>
          <el-descriptions-item label="姓名">{{ currentUser.full_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="部门">{{ currentUser.department || '-' }}</el-descriptions-item>
          <el-descriptions-item label="职称">{{ currentUser.title || '-' }}</el-descriptions-item>
          <el-descriptions-item label="手机号">{{ currentUser.phone || '-' }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ currentUser.email || '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="currentUser.is_active ? 'success' : 'danger'" size="small">
              {{ currentUser.is_active ? '启用' : '禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ currentUser.created_at }}</el-descriptions-item>
          <el-descriptions-item label="最后登录">{{ currentUser.last_login_at || '-' }}</el-descriptions-item>
          <el-descriptions-item label="诊断次数">{{ currentUser.diagnosis_count || 0 }}</el-descriptions-item>
          <el-descriptions-item label="备注">{{ currentUser.remark || '-' }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import SearchBar from '@/components/SearchBar.vue'
import Pagination from '@/components/Pagination.vue'
import { getUsers, createUser, updateUser, deleteUser, resetUserPassword, toggleUserStatus } from '@/api/user'

const loading = ref(false)
const userList = ref([])
const userDialogVisible = ref(false)
const passwordDialogVisible = ref(false)
const detailDrawerVisible = ref(false)
const isEdit = ref(false)
const userSaving = ref(false)
const passwordSaving = ref(false)
const userFormRef = ref(null)
const passwordFormRef = ref(null)
const currentUser = ref(null)

// 搜索表单
const searchForm = reactive({
  keyword: '',
  role: '',
  isActive: '',
  department: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 用户表单
const userForm = reactive({
  id: null,
  username: '',
  full_name: '',
  password: '',
  confirm_password: '',
  role: 'doctor',
  department: '',
  phone: '',
  email: '',
  title: '',
  remark: '',
  is_active: true
})

// 密码重置表单
const passwordForm = reactive({
  user_id: null,
  username: '',
  new_password: '',
  confirm_password: ''
})

// 表单校验规则
const validateConfirmPassword = (rule, value, callback) => {
  if (value !== userForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const validateResetConfirmPassword = (rule, value, callback) => {
  if (value !== passwordForm.new_password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const userRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]{4,20}$/, message: '用户名只能包含字母、数字、下划线，长度4-20位', trigger: 'blur' }
  ],
  fullName: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

const passwordRules = {
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: validateResetConfirmPassword, trigger: 'blur' }
  ]
}

// 加载用户列表
const loadUserList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      keyword: searchForm.keyword,
      role: searchForm.role,
      is_active: searchForm.isActive,
      department: searchForm.department
    }
    const res = await getUsers(params)
    userList.value = res.items || res || []
    pagination.total = res.total || userList.value.length
  } catch (error) {
    console.error('加载用户列表失败', error)
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = (params) => {
  Object.assign(searchForm, params)
  pagination.page = 1
  loadUserList()
}

// 重置
const handleReset = () => {
  Object.keys(searchForm).forEach(key => {
    searchForm[key] = ''
  })
  pagination.page = 1
  loadUserList()
}

// 打开用户对话框
const openUserDialog = (row = null) => {
  isEdit.value = !!row
  if (row) {
    Object.assign(userForm, {
      id: row.id,
      username: row.username,
      full_name: row.full_name,
      password: '',
      confirm_password: '',
      role: row.role,
      department: row.department,
      phone: row.phone,
      email: row.email,
      title: row.title,
      remark: row.remark,
      is_active: row.is_active
    })
  } else {
    Object.assign(userForm, {
      id: null,
      username: '',
      full_name: '',
      password: '',
      confirm_password: '',
      role: 'doctor',
      department: '',
      phone: '',
      email: '',
      title: '',
      remark: '',
      is_active: true
    })
  }
  userDialogVisible.value = true
}

// 保存用户
const saveUser = async () => {
  await userFormRef.value.validate()
  userSaving.value = true
  try {
    if (isEdit.value) {
      await updateUser(userForm.id, userForm)
      ElMessage.success('更新成功')
    } else {
      await createUser(userForm)
      ElMessage.success('创建成功')
    }
    userDialogVisible.value = false
    loadUserList()
  } catch (error) {
    console.error('保存用户失败', error)
  } finally {
    userSaving.value = false
  }
}

// 切换用户状态
const handleToggleUserStatus = async (row) => {
  try {
    await toggleUserStatus(row.id, row.is_active)
    ElMessage.success(`已${row.is_active ? '启用' : '禁用'}用户`)
  } catch (error) {
    row.is_active = !row.is_active
    console.error('切换状态失败', error)
  }
}

// 重置密码
const resetPassword = (row) => {
  passwordForm.user_id = row.id
  passwordForm.username = row.username
  passwordForm.new_password = ''
  passwordForm.confirm_password = ''
  passwordDialogVisible.value = true
}

// 确认重置密码
const confirmResetPassword = async () => {
  await passwordFormRef.value.validate()
  passwordSaving.value = true
  try {
    await resetUserPassword(passwordForm.user_id, { new_password: passwordForm.new_password })
    ElMessage.success('密码重置成功')
    passwordDialogVisible.value = false
  } catch (error) {
    console.error('重置密码失败', error)
  } finally {
    passwordSaving.value = false
  }
}

// 删除用户
const handleDeleteUser = async (row) => {
  try {
    await deleteUser(row.id)
    ElMessage.success('删除成功')
    loadUserList()
  } catch (error) {
    console.error('删除用户失败', error)
    ElMessage.error('删除用户失败')
  }
}

// 查看用户详情
const viewUserDetail = (row) => {
  currentUser.value = row
  detailDrawerVisible.value = true
}

onMounted(() => {
  loadUserList()
})
</script>

<style scoped>
.user-manage-page {
  width: 100%;
}

.user-info-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.user-meta {
  font-size: 12px;
  color: var(--text-secondary);
}

.user-detail-content {
  width: 100%;
}

.profile-section {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border-light);
}

.profile-info h3 {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 12px;
}
</style>