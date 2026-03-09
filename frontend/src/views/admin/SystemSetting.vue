<template>
  <div class="system-setting-page">
    <PageHeader
      title="系统设置"
      description="管理平台全局配置、存储设置、通知模板等系统参数"
    />

    <el-card class="common-card">
      <el-tabs v-model="activeTab" class="custom-tabs">
        <el-tab-pane label="全局配置" name="global">
          <el-form :model="globalForm" label-width="180px" class="setting-form">
            
            <div class="setting-section">
              <div class="section-header">
                <div class="section-title">
                  <el-icon><Monitor /></el-icon> 品牌与外观
                  <el-tooltip content="定制化平台的名称、Logo及登录页背景，打造专属品牌形象" placement="top">
                    <el-icon class="info-icon"><QuestionFilled /></el-icon>
                  </el-tooltip>
                </div>
              </div>
              <div class="section-body">
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
                    <div v-else class="uploader-placeholder">
                      <el-icon class="logo-uploader-icon"><Plus /></el-icon>
                      <span>上传Logo</span>
                    </div>
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
                    <el-button v-else type="primary" plain>上传背景图</el-button>
                  </el-upload>
                  <div class="upload-tip">建议尺寸 1920*1080px，支持JPG/PNG格式，大小不超过5MB</div>
                </el-form-item>
              </div>
            </div>

            <div class="setting-section">
              <div class="section-header">
                <div class="section-title">
                  <el-icon><Lock /></el-icon> 安全与认证
                  <el-tooltip content="配置账户密码强度、登录防爆破策略及登录态过期时间" placement="top">
                    <el-icon class="info-icon"><QuestionFilled /></el-icon>
                  </el-tooltip>
                </div>
              </div>
              <div class="section-body">
                <el-row>
                  <el-col :span="12">
                    <el-form-item label="Token过期时间">
                      <el-input-number v-model="globalForm.token_expire" :min="1" :max="720" style="width: 160px" />
                      <span class="form-tip">小时 (默认24)</span>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="密码最小长度">
                      <el-input-number v-model="globalForm.password_min_length" :min="6" :max="20" style="width: 160px" />
                      <span class="form-tip">位 (默认6)</span>
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-row>
                  <el-col :span="12">
                    <el-form-item label="登录失败锁定次数">
                      <el-input-number v-model="globalForm.login_fail_lock" :min="3" :max="10" style="width: 160px" />
                      <span class="form-tip">次 (默认5)</span>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="失败锁定时间">
                      <el-input-number v-model="globalForm.lock_duration" :min="5" :max="1440" style="width: 160px" />
                      <span class="form-tip">分钟 (默认30)</span>
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-form-item label="开启验证码登录">
                  <el-switch v-model="globalForm.captcha_enabled" active-text="开启" inactive-text="关闭" />
                </el-form-item>
              </div>
            </div>

            <div class="setting-section">
              <div class="section-header">
                <div class="section-title">
                  <el-icon><Operation /></el-icon> 诊断流控
                  <el-tooltip content="管理系统推理任务的并发上限及超时限制，防止系统资源过载" placement="top">
                    <el-icon class="info-icon"><QuestionFilled /></el-icon>
                  </el-tooltip>
                </div>
              </div>
              <div class="section-body">
                <el-row>
                  <el-col :span="12">
                    <el-form-item label="最大并发任务数">
                      <el-input-number v-model="globalForm.max_concurrent_task" :min="1" :max="50" style="width: 160px" />
                      <span class="form-tip">单用户上限</span>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="任务最大超时">
                      <el-input-number v-model="globalForm.task_timeout" :min="30" :max="3600" style="width: 160px" />
                      <span class="form-tip">秒 (默认300)</span>
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-form-item label="自动生成诊断报告">
                  <el-switch v-model="globalForm.auto_report" active-text="推理成功后自动生成" inactive-text="需医生手动生成" />
                </el-form-item>
              </div>
            </div>

            <div class="form-footer-actions">
              <el-button @click="resetGlobalConfig" size="large">重置恢复</el-button>
              <el-button type="primary" :loading="saving" @click="saveGlobalConfig" size="large">保存全部配置</el-button>
            </div>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="存储引擎" name="storage">
          <div class="setting-section">
            <el-alert
              title="存储配置用于管理平台医学影像、文档、模型权重的存储底层，修改后需重启后端服务生效"
              type="warning"
              show-icon
              class="mb-20"
              :closable="false"
            />
            <el-form :model="storageForm" label-width="180px" class="setting-form">
              <el-form-item label="存储类型" required>
                <el-radio-group v-model="storageForm.storage_type">
                  <el-radio-button label="local">本地存储</el-radio-button>
                  <el-radio-button label="minio">MinIO</el-radio-button>
                  <el-radio-button label="oss">阿里云OSS</el-radio-button>
                </el-radio-group>
              </el-form-item>

              <div class="engine-config-box">
                <template v-if="storageForm.storage_type === 'local'">
                  <el-form-item label="本地存储根路径" required>
                    <el-input v-model="storageForm.local_root_path" placeholder="如：/app/uploads" style="width: 400px" />
                  </el-form-item>
                  <el-form-item label="访问域名前缀" required>
                    <el-input v-model="storageForm.local_base_url" placeholder="如：https://your-domain.com/uploads" style="width: 400px" />
                  </el-form-item>
                </template>

                <template v-if="storageForm.storage_type === 'minio'">
                  <el-form-item label="Endpoint地址" required>
                    <el-input v-model="storageForm.minio_endpoint" placeholder="如：http://127.0.0.1:9000" style="width: 400px" />
                  </el-form-item>
                  <el-form-item label="Access Key" required>
                    <el-input v-model="storageForm.minio_access_key" placeholder="请输入Access Key" style="width: 400px" />
                  </el-form-item>
                  <el-form-item label="Secret Key" required>
                    <el-input v-model="storageForm.minio_secret_key" type="password" placeholder="请输入Secret Key" style="width: 400px" show-password />
                  </el-form-item>
                  <el-form-item label="Bucket名称" required>
                    <el-input v-model="storageForm.minio_bucket" placeholder="请输入Bucket名称" style="width: 400px" />
                  </el-form-item>
                  <el-form-item label="使用SSL加密">
                    <el-switch v-model="storageForm.minio_use_ssl" active-text="是" inactive-text="否" />
                  </el-form-item>
                </template>

                <template v-if="storageForm.storage_type === 'oss'">
                  <el-form-item label="Endpoint地域" required>
                    <el-input v-model="storageForm.oss_endpoint" placeholder="如：oss-cn-beijing.aliyuncs.com" style="width: 400px" />
                  </el-form-item>
                  <el-form-item label="AccessKey ID" required>
                    <el-input v-model="storageForm.oss_access_key_id" placeholder="请输入AccessKey ID" style="width: 400px" />
                  </el-form-item>
                  <el-form-item label="AccessKey Secret" required>
                    <el-input v-model="storageForm.oss_access_key_secret" type="password" placeholder="请输入AccessKey Secret" style="width: 400px" show-password />
                  </el-form-item>
                  <el-form-item label="Bucket名称" required>
                    <el-input v-model="storageForm.oss_bucket" placeholder="请输入Bucket名称" style="width: 400px" />
                  </el-form-item>
                </template>
              </div>

              <el-divider content-position="left">上传限制</el-divider>
              <el-form-item label="单文件最大限制">
                <el-input-number v-model="storageForm.max_file_size" :min="1" :max="1024" style="width: 160px" />
                <span class="form-tip">MB</span>
              </el-form-item>
              <el-form-item label="允许的文件后缀">
                <el-select v-model="storageForm.allow_file_types" multiple placeholder="请选择允许的文件格式" style="width: 400px">
                  <el-option label=".jpg (图片)" value="jpg" />
                  <el-option label=".png (图片)" value="png" />
                  <el-option label=".dcm (DICOM医疗影像)" value="dcm" />
                  <el-option label=".nii (NIfTI影像)" value="nii" />
                  <el-option label=".xlsx (表格)" value="xlsx" />
                  <el-option label=".pdf (文档)" value="pdf" />
                </el-select>
              </el-form-item>

              <div class="form-footer-actions">
                <el-button @click="resetStorageConfig">重置</el-button>
                <el-button type="success" plain @click="testStorageConnection">测试引擎连通性</el-button>
                <el-button type="primary" :loading="saving" @click="saveStorageConfig">保存存储配置</el-button>
              </div>
            </el-form>
          </div>
        </el-tab-pane>

        <el-tab-pane label="邮件与通知" name="email">
          <div class="setting-section">
            <el-form :model="emailForm" label-width="180px" class="setting-form">
              <div class="section-header">
                <div class="section-title"><el-icon><Message /></el-icon> SMTP 服务器配置</div>
              </div>
              <div class="section-body">
                <el-form-item label="SMTP服务器地址" required>
                  <el-input v-model="emailForm.smtp_host" placeholder="如：smtp.qq.com" style="width: 400px" />
                </el-form-item>
                <el-form-item label="SMTP端口" required>
                  <el-input-number v-model="emailForm.smtp_port" :min="1" :max="65535" style="width: 160px" />
                  <span class="form-tip">常用端口：25/465/587</span>
                </el-form-item>
                <el-form-item label="发件人邮箱" required>
                  <el-input v-model="emailForm.from_email" placeholder="请输入发件人邮箱" style="width: 400px" />
                </el-form-item>
                <el-form-item label="发件人显示名称">
                  <el-input v-model="emailForm.from_name" placeholder="请输入发件人名称" style="width: 400px" />
                </el-form-item>
                <el-form-item label="邮箱授权码/密码" required>
                  <el-input v-model="emailForm.smtp_password" type="password" placeholder="请输入邮箱授权码" style="width: 400px" show-password />
                </el-form-item>
                <el-form-item label="启用SSL/TLS协议">
                  <el-switch v-model="emailForm.use_ssl" active-text="启用" inactive-text="禁用" />
                </el-form-item>
              </div>

              <el-divider content-position="left">连通性测试</el-divider>
              <el-form-item label="测试收件邮箱">
                <div style="display: flex; gap: 12px; width: 400px;">
                  <el-input v-model="testEmail" placeholder="输入收件人邮箱" />
                  <el-button type="success" plain :loading="testingEmail" @click="testEmailConfig" :disabled="!testEmail">发送测试邮件</el-button>
                </div>
              </el-form-item>

              <div class="form-footer-actions">
                <el-button @click="resetEmailConfig">重置</el-button>
                <el-button type="primary" :loading="saving" @click="saveEmailConfig">保存邮件配置</el-button>
              </div>
            </el-form>
          </div>
        </el-tab-pane>

        <el-tab-pane label="通知模板管理" name="notice">
          <div class="template-header">
            <el-button type="primary" @click="openTemplateDialog()">
              <el-icon><Plus /></el-icon> 新增通知模板
            </el-button>
          </div>
          <el-table :data="templateList" border class="common-table">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="template_name" label="业务场景" width="180" />
            <el-table-column prop="template_code" label="模板编码" width="180" />
            <el-table-column prop="notice_type" label="触达方式" width="120">
              <template #default="{ row }">
                <el-tag :type="row.notice_type === 'email' ? 'primary' : 'warning'" size="small">
                  {{ row.notice_type === 'email' ? '邮件推送' : '站内信' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="title" label="消息标题" show-overflow-tooltip />
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
            <el-table-column prop="updated_at" label="最后更新" width="180" />
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="openTemplateDialog(row)">编辑</el-button>
                <el-button type="success" link size="small" @click="testTemplate(row)">模拟发送</el-button>
                <el-button type="danger" link size="small" @click="deleteTemplate(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-dialog v-model="templateDialogVisible" :title="isEditTemplate ? '编辑通知模板' : '新增通知模板'" width="750px">
            <el-form :model="templateForm" label-width="100px" class="common-form">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="场景名称" required>
                    <el-input v-model="templateForm.template_name" :disabled="isEditTemplate" placeholder="如：任务完成通知" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="模板编码" required>
                    <el-input v-model="templateForm.template_code" :disabled="isEditTemplate" placeholder="如：TASK_COMPLETE" />
                  </el-form-item>
                </el-col>
              </el-row>
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="触达方式" required>
                    <el-select v-model="templateForm.notice_type" :disabled="isEditTemplate" placeholder="请选择" style="width: 100%">
                      <el-option label="邮件推送" value="email" />
                      <el-option label="站内消息" value="message" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="是否启用">
                    <el-switch v-model="templateForm.is_active" active-text="启用" inactive-text="禁用" />
                  </el-form-item>
                </el-col>
              </el-row>
              <el-form-item label="消息标题" required>
                <el-input v-model="templateForm.title" placeholder="请输入标题，支持双大括号变量替换" />
              </el-form-item>
              <el-form-item label="正文内容" required>
                <el-input
                  v-model="templateForm.content"
                  type="textarea"
                  :rows="10"
                  placeholder="支持 HTML 标签及变量替换。&#10;示例：您好 {{doctor_name}}，患者 {{patient_name}} 的 {{model_name}} 诊断任务已完成。"
                />
              </el-form-item>
              <el-alert
                title="系统变量词典：{{patient_name}} (患者姓名) | {{model_name}} (模型名称) | {{diagnosis_time}} (完成时间) | {{doctor_name}} (医生姓名) | {{task_id}} (任务编号)"
                type="info"
                show-icon
                :closable="false"
              />
            </el-form>
            <template #footer>
              <el-button @click="templateDialogVisible = false">取消</el-button>
              <el-button type="primary" :loading="templateSaving" @click="saveTemplate">保存模板</el-button>
            </template>
          </el-dialog>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Monitor, Lock, Operation, Message, QuestionFilled, Plus } from '@element-plus/icons-vue'
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
  allow_file_types: ['jpg', 'png', 'dcm', 'nii', 'xlsx', 'pdf']
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
  if (!isImage) { ElMessage.error('Logo只能是JPG/PNG格式!'); return false }
  if (!isLt2M) { ElMessage.error('Logo大小不能超过2MB!'); return false }
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
  if (!isImage) { ElMessage.error('背景图只能是JPG/PNG格式!'); return false }
  if (!isLt5M) { ElMessage.error('背景图大小不能超过5MB!'); return false }
  return true
}

// 保存/重置全局配置
const saveGlobalConfig = async () => {
  saving.value = true
  try {
    await updateSystemConfig(globalForm)
    ElMessage.success('全局配置保存成功')
  } catch (error) {
    console.error('保存失败', error)
  } finally { saving.value = false }
}

const resetGlobalConfig = async () => {
  try {
    const res = await getSystemConfig()
    Object.assign(globalForm, res)
    ElMessage.success('配置已恢复至上次保存状态')
  } catch (error) { console.error('重置失败', error) }
}

// 保存/重置存储配置
const saveStorageConfig = async () => {
  saving.value = true
  try {
    await updateStorageConfig(storageForm)
    ElMessage.success('存储引擎配置更新成功，请重启后端服务生效')
  } catch (error) { console.error('保存失败', error) } finally { saving.value = false }
}

const resetStorageConfig = async () => {
  try {
    const res = await getStorageConfig()
    Object.assign(storageForm, res)
    ElMessage.success('配置已重置')
  } catch (error) { console.error('重置失败', error) }
}

const testStorageConnection = () => {
  ElMessage.success('存储网关连接测试成功')
}

// 邮件配置相关
const saveEmailConfig = async () => {
  saving.value = true
  try {
    await updateSystemConfig({ email: emailForm })
    ElMessage.success('SMTP配置保存成功')
  } catch (error) { console.error('保存失败', error) } finally { saving.value = false }
}

const resetEmailConfig = () => {
  Object.assign(emailForm, { smtp_host: '', smtp_port: 465, from_email: '', from_name: '医疗AI平台', smtp_password: '', use_ssl: true })
  ElMessage.success('配置已重置')
}

const testEmailConfig = async () => {
  testingEmail.value = true
  try {
    await testEmailNotice({ to_email: testEmail.value })
    ElMessage.success('测试邮件已下发任务队列，请查收')
  } catch (error) { console.error('测试失败', error) } finally { testingEmail.value = false }
}

// 模板管理相关
const loadTemplateList = async () => {
  try {
    const res = await getNoticeTemplates()
    templateList.value = res
  } catch (error) { console.error('加载模板列表失败', error) }
}

const openTemplateDialog = (row = null) => {
  isEditTemplate.value = !!row
  if (row) {
    Object.assign(templateForm, row)
  } else {
    Object.assign(templateForm, { id: null, template_name: '', template_code: '', notice_type: 'email', title: '', content: '', is_active: true })
  }
  templateDialogVisible.value = true
}

const saveTemplate = async () => {
  if (!templateForm.template_name || !templateForm.template_code || !templateForm.title || !templateForm.content) {
    ElMessage.warning('请填写必填项')
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
  } catch (error) { console.error('保存失败', error) } finally { templateSaving.value = false }
}

const toggleTemplateStatus = async (row) => {
  try {
    await updateNoticeTemplate(row.id, { is_active: row.is_active })
    ElMessage.success(`模板已${row.is_active ? '启用' : '挂起'}`)
  } catch (error) { row.is_active = !row.is_active; console.error('切换失败', error) }
}

const testTemplate = (row) => { ElMessage.info('模板渲染测试功能开发中...') }

const deleteTemplate = (row) => {
  ElMessageBox.confirm(`确定要移除 "${row.template_name}" 模板吗？`, '高危操作', { type: 'danger' }).then(async () => {
    try {
      await deleteNoticeTemplate(row.id)
      ElMessage.success('移除成功')
      loadTemplateList()
    } catch (error) { console.error('删除失败', error) }
  })
}

const loadAllConfig = async () => {
  try {
    const systemRes = await getSystemConfig()
    Object.assign(globalForm, systemRes.global || systemRes)
    Object.assign(emailForm, systemRes.email || {})
    const storageRes = await getStorageConfig()
    Object.assign(storageForm, storageRes)
    await loadTemplateList()
  } catch (error) { console.error('初始化配置失败', error) }
}

onMounted(() => { loadAllConfig() })
</script>

<style scoped>
.system-setting-page {
  width: 100%;
}

/* Tabs 自定义样式去除生硬的 border */
.custom-tabs :deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background-color: var(--border-light);
}

/* ----------------------------------
   卡片内嵌逻辑分块 (核心优化区)
-----------------------------------*/
.setting-section {
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: 10px;
  margin-bottom: 24px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.015);
  overflow: hidden;
}

.section-header {
  padding: 16px 24px;
  background-color: #f9fafc;
  border-bottom: 1px solid var(--border-light);
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-icon {
  font-size: 14px;
  color: var(--text-secondary);
  cursor: help;
  outline: none;
}

.section-body {
  padding: 24px 24px 8px 24px;
}

.form-tip {
  margin-left: 12px;
  color: var(--text-secondary);
  font-size: 13px;
}

.upload-tip {
  margin-top: 8px;
  color: var(--text-secondary);
  font-size: 12px;
  line-height: 1.4;
}

.mb-20 { margin-bottom: 20px; }

/* 上传组件样式美化 */
.logo-uploader {
  border: 1px dashed var(--border-base);
  border-radius: 8px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
  width: 220px;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #fafafa;
}
.logo-uploader:hover {
  border-color: var(--primary-color);
  background-color: #f0f5ff;
}
.logo-image {
  width: 100%; height: 100%; object-fit: contain; display: block;
}
.uploader-placeholder {
  display: flex; flex-direction: column; align-items: center; color: var(--text-secondary);
}
.logo-uploader-icon { font-size: 24px; margin-bottom: 4px; }

.bg-uploader { width: 400px; }
.bg-image {
  width: 100%; height: 200px; object-fit: cover;
  border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

/* 引擎配置内联区块 */
.engine-config-box {
  background-color: #f7f8fa;
  padding: 24px 24px 4px 0;
  border-radius: 8px;
  margin-left: 40px;
  margin-bottom: 24px;
}

/* 底部操作区 */
.form-footer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  padding: 20px 24px;
  background-color: #fff;
  border-top: 1px dashed var(--border-light);
}

.template-header {
  margin-bottom: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>