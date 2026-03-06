<template>
  <div class="schema-editor">
    <div ref="editorRef" class="editor-container"></div>
    <div v-if="error" class="error-tip">{{ error }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import { EditorView, basicSetup } from 'codemirror'
import { json } from '@codemirror/lang-json'
import { oneDark } from '@codemirror/theme-one-dark'
import { EditorState } from '@codemirror/state'

const props = defineProps({
  modelValue: {
    type: [String, Object],
    default: ''
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

const editorRef = ref(null)
const editorView = ref(null)
const error = ref('')

// 格式化JSON
const formatJSON = (value) => {
  if (!value) return '{}'
  if (typeof value === 'object') {
    return JSON.stringify(value, null, 2)
  }
  try {
    const obj = JSON.parse(value)
    return JSON.stringify(obj, null, 2)
  } catch (e) {
    return value
  }
}

// 初始化编辑器
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
        if (update.docChanged) {
          const content = update.state.doc.toString()
          validateJSON(content)
        }
      })
    ]
  })

  editorView.value = new EditorView({
    state,
    parent: editorRef.value
  })
}

// 校验JSON
const validateJSON = (content) => {
  try {
    const obj = JSON.parse(content)
    error.value = ''
    emit('update:modelValue', obj)
    emit('change', obj)
    emit('error', null)
  } catch (e) {
    error.value = `JSON格式错误: ${e.message}`
    emit('error', e)
  }
}

// 监听外部值变化
watch(
  () => props.modelValue,
  (newVal) => {
    if (!editorView.value) return
    const currentContent = editorView.value.state.doc.toString()
    const newContent = formatJSON(newVal)
    if (currentContent !== newContent) {
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
    if (!editorView.value) return
    editorView.value.dispatch({
      effects: EditorView.editable.of(!newVal)
    })
  }
)

onMounted(() => {
  initEditor()
  editorRef.value.style.height = props.height
})

onBeforeUnmount(() => {
  editorView.value?.destroy()
})
</script>

<style scoped>
.schema-editor {
  width: 100%;
}

.editor-container {
  width: 100%;
  min-height: 300px;
  border-radius: 6px;
  overflow: hidden;
}

.error-tip {
  margin-top: 8px;
  color: var(--danger-color);
  font-size: 12px;
}

:deep(.cm-editor) {
  height: 100%;
  min-height: inherit;
}

:deep(.cm-scroller) {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.6;
}
</style>