<template>
  <el-upload
    class="upload-demo"
    drag
    action="/api/upload"
    multiple
    :on-success="handleSuccess"
    :on-error="handleError"
  >
    <el-icon class="el-icon--upload"><upload-filled /></el-icon>
    <div class="el-upload__text">
      将文件拖到此处，或 <em>点击上传</em>
    </div>
  </el-upload>
</template>

<script setup>
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const emit = defineEmits(['success'])

const handleSuccess = (response, uploadFile) => {
  ElMessage.success('上传成功')
  emit('success', response)
}

const handleError = () => {
  ElMessage.error('上传失败，请重试')
}
</script>

<style scoped>
.upload-demo {
  width: 100%;
}
</style>