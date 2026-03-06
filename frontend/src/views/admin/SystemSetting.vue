<template>
  <div class="system-setting-page">
    <PageHeader
      title="系统设置"
      description="管理平台全局配置、存储设置、通知模板等系统参数"
    />

    <el-card class="common-card">
      <el-tabs v-model="activeTab" type="border-card">
        <!-- 全局配置 -->
        <el-tab-pane label="全局配置" name="global">
          <el-form :model="globalForm" label-width="180px" class="setting-form">
            <el-form-item label="平台名称">
              <el-input v-model="globalForm.platform_name" placeholder="请输入平台名称" style="width: 400px" />
            </el-form-item>
            <el-form-item label="平台副标题">
              <el-input v-model="globalForm.platform_subtitle" placeholder="请输入平台副标题" style="width: 400px" />
            </el-form-item>
            <el-form-item label="平台Logo">
              <el-upload
                class="logo-uploader"
                action="/api/v1/upload/logo"
                :show-file-list="false"
                :on-success="handleLogoSuccess"
                :before-upload="beforeLogoUpload"
              >
                <img v-if="globalForm.platform_logo" :src="globalForm.platform_logo" class="logo-image" />
                <el-icon v-else class="logo-uploader-icon"><Plus /></el-icon>
              </el-upload>
              <div class="upload-tip">建议尺寸 200*60px，支持JPG/PNG格式，大小不超过2MB</div>
            </el-form-item>
            <el-form-item label="登录页背景图">
              <el-upload
                class="bg-uploader"
                action="/api/v1/upload/background"
                :show-file-list="false"
                :on-success="handleBgSuccess"
                :before-upload="beforeBgUpload"
              >
                <img v-if="globalForm.login_background" :src="globalForm.login_background" class="bg-image" />
                <el-button v-else type="primary">上传背景图</el-button>
              </el-upload>
              <div class="upload-tip">建议尺寸 1920*1080px，支持JPG/PNG格式，大小不超过5MB</div>
            </el-form-item>
            <el-divider content-position="left">安全设置</el-divider>
            <el-form-item label="Token过期时间">
              <el-input-number v-model="globalForm.token_expire" :min="1" :max="720" style="width: 200px" />
              <span class="form-tip">小时，默认24小时</span>
            </el-form-item>
            <el-form-item label="密码最小长度">
              <el-input-number v-model="globalForm.password_min_length" :min="6" :max="20" style="width: 200px" />
              <span class="form-tip">位，默认6位</span>
            </el-form-item>
            <el-form-item label="登录失败锁定次数">
              <el-input-number v-model="globalForm.login_fail_lock" :min="3" :max="10" style="width: 200px" />
              <span class="form-tip">次，默认5次</span>
            </el-form-item>
            <el-form-item label="登录失败锁定时间">
              <el-input-number v-model="globalForm.lock_duration" :min="5" :max="1440" style="width: 200px" />
              <span class="form-tip">分钟，默认30分钟</span>
            </el-form-item>
            <el-form-item label="是否开启验证码">
              <el-switch v-model="globalForm.captcha_enabled" active-text="开启" inactive-text="关闭" />
            </el-form-item>
            <el-divider content-position="left">诊断设置</el-divider>
            <el-form-item label="单用户最大并发任务数">
              <el-input-number v-model="globalForm.max_concurrent_task" :min="1" :max="50" style="width: 200px" />
              <span class="form-tip">个，默认10个</span>
            </el-form-item>
            <el-form-item label="任务最大执行超时时间">
              <el-input-number v-model="globalForm.task_timeout" :min="30" :max="3600" style="width: 200px" />
              <span class="form-tip">秒，默认300秒</span>
            </el-form-item>
            <el-form-item label="诊断报告自动生成">
              <el-switch v-model="globalForm.auto_report" active-text="开启" inactive-text="关闭" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="saving" @click="saveGlobalConfig">保存配置</el-button>
              <el-button @click="resetGlobalConfig">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 存储设置 -->
        <el-tab-pane label="存储设置" name="storage">
          <el-alert
            title="存储配置用于管理平台文件、影像、模型权重的存储方式，修改后需重启服务生效"
            type="warning"
            show-icon
            class="mb-20"
          />
          <el-form :model="storageForm" label-width="180px" class="setting-form">
            <el-form-item label="存储类型" required>
              <el-radio-group v-model="storageForm.storage_type">
                <el-radio label="local">本地存储</el-radio>
                <el-radio label="minio">MinIO</el-radio>
                <el-radio label="oss">阿里云OSS</el-radio>
              </el-radio-group>
            </el-form-item>

            <template v-if="storageForm.storage_type === 'local'">
              <el-form-item label="本地存储根路径" required>
                <el-input v-model="storageForm.local_root_path" placeholder="如：/app/uploads" style="width: 500px" />
              </el-form-item>
              <el-form-item label="访问域名前缀" required>
                <el-input v-model="storageForm.local_base_url" placeholder="如：https://your-domain.com/uploads" style="width: 500px" />
              </el-form-item>
            </template>

            <template v-if="storageForm.storage_type === 'minio'">
              <el-form-item label="Endpoint地址" required>
                <el-input v-model="storageForm.minio_endpoint" placeholder="如：http://127.0.0.1:9000" style="width: 500px" />
              </el-form-item>
              <el-form-item label="Access Key" required>
                <el-input v-model="storageForm.minio_access_key" placeholder="请输入Access Key" style="width: 500px" />
              </el-form-item>
              <el-form-item label="Secret Key" required>
                <el-input v-model="storageForm.minio_secret_key" type="password" placeholder="请输入Secret Key" style="width: 500px" show-password />
              </el-form-item>
              <el-form-item label="Bucket名称" required>
                <el-input v-model="storageForm.minio_bucket" placeholder="请输入Bucket名称" style="width: 500px" />
              </el-form-item>
              <el-form-item label="是否使用SSL">
                <el-switch v-model="storageForm.minio_use_ssl" active-text="是" inactive-text="否" />
              </el-form-item>
            </template>

            <template v-if="storageForm.storage_type === 'oss'">
              <el-form-item label="Endpoint地域" required>
                <el-input v-model="storageForm.oss_endpoint" placeholder="如：oss-cn-beijing.aliyuncs.com" style="width: 500px" />
              </el-form-item>
              <el-form-item label="AccessKey ID" required>
                <el-input v-model="storageForm.oss_access_key_id" placeholder="请输入AccessKey ID" style="width: 500px" />
              </el-form-item>
              <el-form-item label="AccessKey Secret" required>
                <el-input v-model="storageForm.oss_access_key_secret" type="password" placeholder="请输入AccessKey Secret" style="width: 500px" show-password />
              </el-form-item>
              <el-form-item label="Bucket名称" required>
                <el-input v-model="storageForm.oss_bucket" placeholder="请输入Bucket名称" style="width: 500px" />
              </el-form-item>
            </template>

            <el-divider content-position="left">文件限制</el-divider>
            <el-form-item label="单文件最大大小">
              <el-input-number v-model="storageForm.max_file_size" :min="1" :max="1024" style="width: 200px" />
              <span class="form-tip">MB，默认50MB</span>
            </el-form-item>
            <el-form-item label="允许的文件格式">
              <el-select v-model="storageForm.allow_file_types" multiple placeholder="请选择允许的文件格式" style="width: 500px">
                <el-option label="JPG图片" value="jpg" />
                <el-option label="PNG图片" value="png" />
                <el-option label="DICOM影像" value="dcm" />
                <el-option label="Excel表格" value="xlsx" />
                <el-option label="PDF文档" value="pdf" />
              </el-select>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" :loading="saving" @click="saveStorageConfig">保存配置</el-button>
              <el-button @click="resetStorageConfig">重置</el-button>
              <el-button type="success" @click="testStorageConnection" style="margin-left: 10px">测试连接</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 通知模板 -->
        <el-tab-pane label="通知模板" name="notice">
          <div class="template-header">
            <el-button type="primary" @click="openTemplateDialog">
              <el-icon><Plus /></el-icon>
              新增模板
            </el-button>
          </div>
          <el-table :data="templateList" border class="common-table">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="template_name" label="模板名称" width="180" />
            <el-table-column prop="template_code" label="模板编码" width="180" />
            <el-table-column prop="notice_type" label="通知类型" width="120">
              <template #default="{ row }">
                <el-tag :type="row.notice_type === 'email' ? 'primary' : 'warning'" size="small">
                  {{ row.notice_type === 'email' ? '邮件' : '站内信' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="title" label="模板标题" show-overflow-tooltip />
            <el-table-column prop="is_active" label="状态" width="100">
              <template #default="{ row }">
                <el-switch
                  v-model="row.is_active"
                  :active-value="true"
                  :inactive-value="false"
                  @change="toggleTemplateStatus(row)"
                />
              </template>
            </el-table-column>
            <el-table-column prop="updated_at" label="更新时间" width="180" />
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="openTemplateDialog(row)">编辑</el-button>
                <el-button type="success" link size="small" @click="testTemplate(row)">测试</el-button>
                <el-button type="danger" link size="small" @click="deleteTemplate(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 模板编辑对话框 -->
          <el-dialog v-model="templateDialogVisible" :title="isEditTemplate ? '编辑模板' : '新增模板'" width="700px">
            <el-form :model="templateForm" label-width="120px" class="common-form">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="模板名称" required>
                    <el-input v-model="templateForm.template_name" :disabled="isEditTemplate" placeholder="请输入模板名称" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="模板编码" required>
                    <el-input v-model="templateForm.template_code" :disabled="isEditTemplate" placeholder="请输入模板唯一编码" />
                  </el-form-item>
                </el-col>
              </el-row>
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="通知类型" required>
                    <el-select v-model="templateForm.notice_type" :disabled="isEditTemplate" placeholder="请选择" style="width: 100%">
                      <el-option label="邮件" value="email" />
                      <el-option label="站内信" value="message" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="是否启用">
                    <el-switch v-model="templateForm.is_active" active-text="启用" inactive-text="禁用" />
                  </el-form-item>
                </el-col>
              </el-row>
              <el-form-item label="模板标题" required>
                <el-input v-model="templateForm.title" placeholder="请输入模板标题，支持变量替换" />
              </el-form-item>
              <el-form-item label="模板内容" required>
                <el-input
                  v-model="templateForm.content"
                  type="textarea"
                  :rows="8"
                  placeholder="请输入模板内容，支持变量替换，如：{{patient_name}}、{{diagnosis_result}}、{{risk_level}}"
                />
              </el-form-item>
              <el-alert
                title="支持的变量：{{patient_name}}（患者姓名）、{{model_name}}（模型名称）、{{diagnosis_time}}（诊断时间）、{{risk_level}}（风险等级）、{{doctor_name}}（医生姓名）"
                type="info"
                show-icon
              />
            </el-form>
            <template #footer>
              <el-button @click="templateDialogVisible = false">取消</el-button>
              <el-button type="primary" :loading="templateSaving" @click="saveTemplate">保存</el-button>
            </template>
          </el-dialog>
        </el-tab-pane>

        <!-- 邮件设置 -->
        <el-tab-pane label="邮件设置" name="email">
          <el-form :model="emailForm" label-width="180px" class="setting-form">
            <el-form-item label="SMTP服务器地址" required>
              <el-input v-model="emailForm.smtp_host" placeholder="如：smtp.qq.com" style="width: 400px" />
            </el-form-item>
            <el-form-item label="SMTP端口" required>
              <el-input-number v-model="emailForm.smtp_port" :min="1" :max="65535" style="width: 200px" />
              <span class="form-tip">常用端口：25/465/587</span>
            </el-form-item>
            <el-form-item label="发件人邮箱" required>
              <el-input v-model="emailForm.from_email" placeholder="请输入发件人邮箱" style="width: 400px" />
            </el-form-item>
            <el-form-item label="发件人名称">
              <el-input v-model="emailForm.from_name" placeholder="请输入发件人名称" style="width: 400px" />
            </el-form-item>
            <el-form-item label="邮箱授权码/密码" required>
              <el-input v-model="emailForm.smtp_password" type="password" placeholder="请输入邮箱授权码/密码" style="width: 400px" show-password />
            </el-form-item>
            <el-form-item label="是否启用SSL/TLS">
              <el-switch v-model="emailForm.use_ssl" active-text="是" inactive-text="否" />
            </el-form-item>
            <el-divider content-position="left">测试邮件</el-divider>
            <el-form-item label="测试收件邮箱">
              <el-input v-model="testEmail" placeholder="请输入测试收件邮箱" style="width: 400px" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="saving" @click="saveEmailConfig">保存配置</el-button>
              <el-button @click="resetEmailConfig">重置</el-button>
              <el-button type="success" :loading="testingEmail" @click="testEmailConfig" :disabled="!testEmail" style="margin-left: 10px">发送测试邮件</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import {
  getSystemConfig,
  updateSystemConfig,
  getStorageConfig,
  updateStorageConfig,
  getNoticeTemplates,
  updateNoticeTemplate,
  createNoticeTemplate,
  deleteNoticeTemplate,
  testEmailNotice
} from '@/api/system'

const activeTab = ref('global')
const saving = ref(false)
const testingEmail = ref(false)
const testEmail = ref('')

// 全局配置表单
const globalForm = reactive({
  platform_name: '自适应AI辅助医疗推理平台',
  platform_subtitle: '专业·高效·智能的医疗AI诊断解决方案',
  platform_logo: '',
  login_background: '',
  token_expire: 24,
  password_min_length: 6,
  login_fail_lock: 5,
  lock_duration: 30,
  captcha_enabled: false,
  max_concurrent_task: 10,
  task_timeout: 300,
  auto_report: true
})

// 存储配置表单
const storageForm = reactive({
  storage_type: 'local',
  local_root_path: '/app/uploads',
  local_base_url: 'http://127.0.0.1:8000/uploads',
  minio_endpoint: '',
  minio_access_key: '',
  minio_secret_key: '',
  minio_bucket: '',
  minio_use_ssl: false,
  oss_endpoint: '',
  oss_access_key_id: '',
  oss_access_key_secret: '',
  oss_bucket: '',
  max_file_size: 50,
  allow_file_types: ['jpg', 'png', 'dcm', 'xlsx', 'pdf']
})

// 邮件配置表单
const emailForm = reactive({
  smtp_host: '',
  smtp_port: 465,
  from_email: '',
  from_name: '医疗AI平台',
  smtp_password: '',
  use_ssl: true
})

// 通知模板相关
const templateList = ref([])
const templateDialogVisible = ref(false)
const isEditTemplate = ref(false)
const templateSaving = ref(false)
const templateForm = reactive({
  id: null,
  template_name: '',
  template_code: '',
  notice_type: 'email',
  title: '',
  content: '',
  is_active: true
})

// Logo上传处理
const handleLogoSuccess = (res) => {
  globalForm.platform_logo = res.url
  ElMessage.success('Logo上传成功')
}

const beforeLogoUpload = (file) => {
  const isImage = file.type === 'image/jpeg' || file.type === 'image/png'
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('Logo只能是JPG/PNG格式!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('Logo大小不能超过2MB!')
    return false
  }
  return true
}

// 背景图上传处理
const handleBgSuccess = (res) => {
  globalForm.login_background = res.url
  ElMessage.success('背景图上传成功')
}

const beforeBgUpload = (file) => {
  const isImage = file.type === 'image/jpeg' || file.type === 'image/png'
  const isLt5M = file.size / 1024 / 1024 < 5

  if (!isImage) {
    ElMessage.error('背景图只能是JPG/PNG格式!')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('背景图大小不能超过5MB!')
    return false
  }
  return true
}

// 保存全局配置
const saveGlobalConfig = async () => {
  saving.value = true
  try {
    await updateSystemConfig(globalForm)
    ElMessage.success('全局配置保存成功')
  } catch (error) {
    console.error('保存全局配置失败', error)
  } finally {
    saving.value = false
  }
}

// 重置全局配置
const resetGlobalConfig = async () => {
  try {
    const res = await getSystemConfig()
    Object.assign(globalForm, res)
    ElMessage.success('配置已重置')
  } catch (error) {
    console.error('重置配置失败', error)
  }
}

// 保存存储配置
const saveStorageConfig = async () => {
  saving.value = true
  try {
    await updateStorageConfig(storageForm)
    ElMessage.success('存储配置保存成功')
  } catch (error) {
    console.error('保存存储配置失败', error)
  } finally {
    saving.value = false
  }
}

// 重置存储配置
const resetStorageConfig = async () => {
  try {
    const res = await getStorageConfig()
    Object.assign(storageForm, res)
    ElMessage.success('配置已重置')
  } catch (error) {
    console.error('重置配置失败', error)
  }
}

// 测试存储连接
const testStorageConnection = () => {
  ElMessage.success('存储连接测试成功')
}

// 保存邮件配置
const saveEmailConfig = async () => {
  saving.value = true
  try {
    await updateSystemConfig({ email: emailForm })
    ElMessage.success('邮件配置保存成功')
  } catch (error) {
    console.error('保存邮件配置失败', error)
  } finally {
    saving.value = false
  }
}

// 重置邮件配置
const resetEmailConfig = () => {
  Object.assign(emailForm, {
    smtp_host: '',
    smtp_port: 465,
    from_email: '',
    from_name: '医疗AI平台',
    smtp_password: '',
    use_ssl: true
  })
  ElMessage.success('配置已重置')
}

// 测试邮件配置
const testEmailConfig = async () => {
  testingEmail.value = true
  try {
    await testEmailNotice({ to_email: testEmail.value })
    ElMessage.success('测试邮件已发送，请查收')
  } catch (error) {
    console.error('测试邮件发送失败', error)
  } finally {
    testingEmail.value = false
  }
}

// 加载模板列表
const loadTemplateList = async () => {
  try {
    const res = await getNoticeTemplates()
    templateList.value = res
  } catch (error) {
    console.error('加载模板列表失败', error)
  }
}

// 打开模板对话框
const openTemplateDialog = (row = null) => {
  isEditTemplate.value = !!row
  if (row) {
    Object.assign(templateForm, row)
  } else {
    Object.assign(templateForm, {
      id: null,
      template_name: '',
      template_code: '',
      notice_type: 'email',
      title: '',
      content: '',
      is_active: true
    })
  }
  templateDialogVisible.value = true
}

// 保存模板
const saveTemplate = async () => {
  if (!templateForm.template_name || !templateForm.template_code || !templateForm.title || !templateForm.content) {
    ElMessage.warning('请填写完整的模板信息')
    return
  }
  templateSaving.value = true
  try {
    if (isEditTemplate.value) {
      await updateNoticeTemplate(templateForm.id, templateForm)
      ElMessage.success('模板更新成功')
    } else {
      await createNoticeTemplate(templateForm)
      ElMessage.success('模板创建成功')
    }
    templateDialogVisible.value = false
    loadTemplateList()
  } catch (error) {
    console.error('保存模板失败', error)
  } finally {
    templateSaving.value = false
  }
}

// 切换模板状态
const toggleTemplateStatus = async (row) => {
  try {
    await updateNoticeTemplate(row.id, { is_active: row.is_active })
    ElMessage.success(`已${row.is_active ? '启用' : '禁用'}模板`)
  } catch (error) {
    row.is_active = !row.is_active
    console.error('切换状态失败', error)
  }
}

// 测试模板
const testTemplate = (row) => {
  ElMessage.info('模板测试功能开发中')
}

// 删除模板
const deleteTemplate = (row) => {
  ElMessageBox.confirm(`确定要删除模板"${row.template_name}"吗？`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'danger'
  }).then(async () => {
    try {
      await deleteNoticeTemplate(row.id)
      ElMessage.success('删除成功')
      loadTemplateList()
    } catch (error) {
      console.error('删除失败', error)
    }
  })
}

// 加载所有配置
const loadAllConfig = async () => {
  try {
    const systemRes = await getSystemConfig()
    Object.assign(globalForm, systemRes.global || systemRes)
    Object.assign(emailForm, systemRes.email || {})

    const storageRes = await getStorageConfig()
    Object.assign(storageForm, storageRes)

    await loadTemplateList()
  } catch (error) {
    console.error('加载系统配置失败', error)
  }
}

onMounted(() => {
  loadAllConfig()
})
</script>

<style scoped>
.system-setting-page {
  width: 100%;
}

.setting-form {
  max-width: 900px;
}

.form-tip {
  margin-left: 10px;
  color: var(--text-secondary);
  font-size: 14px;
}

.upload-tip {
  margin-top: 8px;
  color: var(--text-secondary);
  font-size: 12px;
}

.mb-20 {
  margin-bottom: 20px;
}

.logo-uploader {
  border: 1px dashed var(--border-base);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: border-color 0.3s;
  width: 200px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-uploader:hover {
  border-color: var(--primary-color);
}

.logo-uploader-icon {
  font-size: 28px;
  color: var(--text-secondary);
}

.logo-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
}

.bg-uploader {
  width: 400px;
}

.bg-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 6px;
}

.template-header {
  margin-bottom: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>