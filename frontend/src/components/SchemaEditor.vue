<template>
  <div class="schema-editor-container" :class="{ 'is-readonly': readonly }">
    <div class="editor-toolbar" v-if="!readonly">
      <el-radio-group v-model="editMode" size="small">
        <el-radio-button value="visual">
          <el-icon><Operation /></el-icon> 可视化配置
        </el-radio-button>
        <el-radio-button value="code">
          <el-icon><Document /></el-icon> 源码编辑
        </el-radio-button>
      </el-radio-group>
      <el-button v-if="editMode === 'visual'" type="primary" size="small" plain @click="addField">
        <el-icon><Plus /></el-icon> 添加字段
      </el-button>
    </div>

    <div v-show="editMode === 'visual'" class="visual-mode" :style="{ height }">
      <el-table :data="visualData" border stripe size="small" height="100%" class="schema-table">
        <el-table-column label="字段标识 (Key)" min-width="120">
          <template #default="{ row }">
            <el-input v-model="row.key" placeholder="如: age, image" @change="syncToCode" :disabled="readonly" />
          </template>
        </el-table-column>
        <el-table-column label="显示名称 (Title)" min-width="120">
          <template #default="{ row }">
            <el-input v-model="row.title" placeholder="如: 患者年龄" @change="syncToCode" :disabled="readonly" />
          </template>
        </el-table-column>
        <el-table-column label="数据类型" width="140">
          <template #default="{ row }">
            <el-select v-model="row.type" @change="syncToCode" :disabled="readonly">
              <el-option label="文本 (String)" value="string" />
              <el-option label="数字 (Number)" value="number" />
              <el-option label="文件 (File/Image)" value="file" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="必填" width="70" align="center">
          <template #default="{ row }">
            <el-checkbox v-model="row.required" @change="syncToCode" :disabled="readonly" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="70" align="center" v-if="!readonly">
          <template #default="{ $index }">
            <el-button type="danger" link size="small" @click="removeField($index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-empty v-if="visualData.length === 0 && readonly" description="暂无字段配置" :image-size="60" />
    </div>

    <div v-show="editMode === 'code'" class="code-mode">
      <div ref="editorRef" class="editor-container" :style="{ height }"></div>
      <div v-if="error" class="error-tip">{{ error }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount, nextTick } from 'vue'
import { Plus, Operation, Document } from '@element-plus/icons-vue'
import { EditorView, basicSetup } from 'codemirror'
import { json } from '@codemirror/lang-json'
import { oneDark } from '@codemirror/theme-one-dark'
import { EditorState } from '@codemirror/state'

const props = defineProps({
  modelValue: {
    type: [String, Object],
    default: () => ({ type: 'object', properties: {}, required: [] })
  },
  readonly: {
    type: Boolean,
    default: false
  },
  height: {
    type: String,
    default: '400px'
  }
})

const emit = defineEmits(['update:modelValue', 'change', 'error'])

const editMode = ref(props.readonly ? 'code' : 'visual')
const visualData = ref([])
const editorRef = ref(null)
const editorView = ref(null)
const error = ref('')

// 1. 将 JSON Schema 解析为可视化表格数据
const parseToVisual = (schemaObj) => {
  const data = []
  if (schemaObj && schemaObj.properties) {
    for (const [key, val] of Object.entries(schemaObj.properties)) {
      const isRequired = (schemaObj.required || []).includes(key)
      data.push({
        key,
        title: val.description || val.title || '',
        type: val.format === 'binary' ? 'file' : (val.type || 'string'),
        required: isRequired
      })
    }
  }
  visualData.value = data
}

// 2. 将可视化表格数据同步回 JSON Schema
const syncToCode = () => {
  const schema = { type: 'object', properties: {}, required: [] }
  visualData.value.forEach(item => {
    if (!item.key) return
    const prop = { type: item.type === 'file' ? 'string' : item.type }
    if (item.title) prop.description = item.title
    if (item.type === 'file') prop.format = 'binary'
    
    schema.properties[item.key] = prop
    if (item.required) schema.required.push(item.key)
  })
  
  emit('update:modelValue', schema)
  emit('change', schema)
  updateEditorContent(schema)
}

// 添加与删除字段
const addField = () => {
  visualData.value.push({ key: '', title: '', type: 'string', required: false })
}

const removeField = (index) => {
  visualData.value.splice(index, 1)
  syncToCode()
}

// 3. 更新 CodeMirror 编辑器内容
const updateEditorContent = (obj) => {
  if (!editorView.value) return
  const newContent = JSON.stringify(obj, null, 2)
  if (editorView.value.state.doc.toString() !== newContent) {
    editorView.value.dispatch({
      changes: {
        from: 0,
        to: editorView.value.state.doc.length,
        insert: newContent
      }
    })
  }
}

// 4. 格式化 JSON (兼容对象和字符串)
const formatJSON = (value) => {
  if (!value) return '{}'
  if (typeof value === 'object') return JSON.stringify(value, null, 2)
  try {
    const obj = JSON.parse(value)
    return JSON.stringify(obj, null, 2)
  } catch (e) {
    return value
  }
}

// 5. 初始化 CodeMirror
const initEditor = () => {
  if (!editorRef.value) return

  const startDoc = formatJSON(props.modelValue)

  const state = EditorState.create({
    doc: startDoc,
    extensions: [
      basicSetup,
      json(),
      oneDark,
      EditorView.editable.of(!props.readonly),
      EditorView.lineWrapping,
      EditorView.updateListener.of(update => {
        if (update.docChanged && editMode.value === 'code') {
          const content = update.state.doc.toString()
          try {
            const obj = JSON.parse(content)
            error.value = ''
            emit('update:modelValue', obj)
            emit('change', obj)
            emit('error', null)
            parseToVisual(obj) // 源码改变时，同步更新可视化表单
          } catch (e) {
            error.value = `JSON格式错误: ${e.message}`
            emit('error', e)
          }
        }
      })
    ]
  })

  editorView.value = new EditorView({
    state,
    parent: editorRef.value
  })
}

// 监听外部值变化 (例如在父组件选中不同的模型时)
watch(
  () => props.modelValue,
  (newVal) => {
    if (typeof newVal === 'object') {
      parseToVisual(newVal)
    } else {
      try {
        parseToVisual(JSON.parse(newVal))
      } catch (e) {
        // 解析失败则忽略
      }
    }
    
    if (!editorView.value) return
    const currentContent = editorView.value.state.doc.toString()
    const newContent = formatJSON(newVal)
    if (currentContent !== newContent && editMode.value !== 'code') {
      editorView.value.dispatch({
        changes: {
          from: 0,
          to: currentContent.length,
          insert: newContent
        }
      })
    }
  },
  { deep: true }
)

// 监听只读状态变化
watch(
  () => props.readonly,
  (newVal) => {
    if (newVal) {
      editMode.value = 'code' // 只读模式下默认展示代码视图更清晰
    }
    if (!editorView.value) return
    editorView.value.dispatch({
      effects: EditorView.editable.of(!newVal)
    })
  }
)

onMounted(() => {
  const initialData = typeof props.modelValue === 'string' ? JSON.parse(props.modelValue || '{}') : props.modelValue
  parseToVisual(initialData)
  
  nextTick(() => {
    initEditor()
  })
})

onBeforeUnmount(() => {
  editorView.value?.destroy()
})
</script>

<style scoped>
.schema-editor-container {
  width: 100%;
  border: 1px solid var(--border-base);
  border-radius: 6px;
  overflow: hidden;
  background: var(--bg-page);
}

.is-readonly {
  border-color: transparent;
}

.editor-toolbar {
  padding: 8px 16px;
  background: #f5f7fa;
  border-bottom: 1px solid var(--border-base);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.visual-mode {
  background: #fff;
  position: relative;
}

.code-mode {
  position: relative;
  background: #282c34;
}

.editor-container {
  width: 100%;
  overflow: hidden;
}

.schema-table :deep(.el-input__wrapper),
.schema-table :deep(.el-select .el-input__wrapper) {
  box-shadow: none;
  background: transparent;
  padding: 0 8px;
}

.schema-table :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--primary-color) inset;
  background: #fff;
}

.error-tip {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  background: rgba(245, 63, 63, 0.9);
  color: #fff;
  padding: 6px 12px;
  font-size: 13px;
  z-index: 10;
}

:deep(.cm-editor) {
  height: 100%;
}

:deep(.cm-scroller) {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', Consolas, monospace;
  font-size: 14px;
  line-height: 1.6;
}

:deep(.cm-gutters) {
  background-color: #282c34;
  color: #5c6370;
  border-right: 1px solid #3e4451;
}
</style>