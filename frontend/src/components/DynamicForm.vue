<template>
  <el-form :model="formData" label-width="120px" class="dynamic-form">
    <el-form-item
      v-for="(schema, key) in schema.properties"
      :key="key"
      :label="schema.title || key"
      :required="schema.required?.includes(key)"
      :prop="key"
      :rules="getFormRules(schema, key)"
    >
      <!-- 数字输入框 -->
      <el-input-number
        v-if="schema.type === 'number' || schema.type === 'integer'"
        v-model="formData[key]"
        :min="schema.minimum ?? -Infinity"
        :max="schema.maximum ?? Infinity"
        :step="schema.step ?? (schema.type === 'integer' ? 1 : 0.1)"
        :precision="schema.precision ?? (schema.type === 'integer' ? 0 : 2)"
        style="width: 100%"
        :placeholder="`请输入${schema.title || key}`"
        :disabled="schema.disabled"
      />

      <!-- 单选下拉框 -->
      <el-select
        v-else-if="schema.type === 'string' && schema.enum"
        v-model="formData[key]"
        style="width: 100%"
        :placeholder="`请选择${schema.title || key}`"
        :disabled="schema.disabled"
        clearable
      >
        <el-option
          v-for="item in schema.enum"
          :key="item"
          :label="item"
          :value="item"
        />
      </el-select>

      <!-- 日期选择器 -->
      <el-date-picker
        v-else-if="schema.type === 'string' && schema.format === 'date'"
        v-model="formData[key]"
        type="date"
        style="width: 100%"
        :placeholder="`请选择${schema.title || key}`"
        :disabled="schema.disabled"
        value-format="YYYY-MM-DD"
      />

      <!-- 日期时间选择器 -->
      <el-date-picker
        v-else-if="schema.type === 'string' && schema.format === 'datetime'"
        v-model="formData[key]"
        type="datetime"
        style="width: 100%"
        :placeholder="`请选择${schema.title || key}`"
        :disabled="schema.disabled"
        value-format="YYYY-MM-DD HH:mm:ss"
      />

      <!-- 文本域 -->
      <el-input
        v-else-if="schema.type === 'string' && schema.format === 'textarea'"
        v-model="formData[key]"
        type="textarea"
        :rows="schema.rows ?? 4"
        :placeholder="`请输入${schema.title || key}`"
        :maxlength="schema.maxLength ?? undefined"
        :disabled="schema.disabled"
        clearable
        show-word-limit
      />

      <!-- 密码输入框 -->
      <el-input
        v-else-if="schema.type === 'string' && schema.format === 'password'"
        v-model="formData[key]"
        type="password"
        :placeholder="`请输入${schema.title || key}`"
        :maxlength="schema.maxLength ?? undefined"
        :disabled="schema.disabled"
        clearable
        show-password
      />

      <!-- 复选框组 -->
      <el-checkbox-group
        v-else-if="schema.type === 'array' && schema.items?.enum"
        v-model="formData[key]"
      >
        <el-checkbox
          v-for="item in schema.items.enum"
          :key="item"
          :label="item"
          :disabled="schema.disabled"
        />
      </el-checkbox-group>

      <!-- 开关 -->
      <el-switch
        v-else-if="schema.type === 'boolean'"
        v-model="formData[key]"
        :disabled="schema.disabled"
        :active-text="schema.activeText || '是'"
        :inactive-text="schema.inactiveText || '否'"
      />

      <!-- 普通文本输入框 -->
      <el-input
        v-else-if="schema.type === 'string'"
        v-model="formData[key]"
        :placeholder="`请输入${schema.title || key}`"
        :maxlength="schema.maxLength ?? undefined"
        :disabled="schema.disabled"
        clearable
      />

      <!-- 兜底：未知类型提示 -->
      <div v-else class="unknown-type-tip">
        暂不支持 {{ schema.type }} 类型的输入控件
      </div>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  schema: {
    type: Object,
    required: true,
    default: () => ({ properties: {}, required: [] })
  },
  modelValue: {
    type: Object,
    default: () => ({})
  },
  readonly: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const formData = ref({ ...props.modelValue })

// 生成表单校验规则
const getFormRules = (schema, key) => {
  const rules = []
  if (schema.required?.includes(key)) {
    rules.push({ required: true, message: `${schema.title || key}为必填项`, trigger: 'blur' })
  }
  if (schema.pattern) {
    rules.push({ pattern: new RegExp(schema.pattern), message: schema.patternMessage || '格式不正确', trigger: 'blur' })
  }
  if (schema.minLength) {
    rules.push({ min: schema.minLength, message: `最少输入${schema.minLength}个字符`, trigger: 'blur' })
  }
  if (schema.maxLength) {
    rules.push({ max: schema.maxLength, message: `最多输入${schema.maxLength}个字符`, trigger: 'blur' })
  }
  return rules
}

// 监听schema变化，重置表单数据
watch(
  () => props.schema,
  (newSchema) => {
    if (newSchema?.properties) {
      const newFormData = {}
      Object.keys(newSchema.properties).forEach(key => {
        newFormData[key] = props.modelValue[key] ?? newSchema.properties[key].default ?? undefined
      })
      formData.value = newFormData
      emit('change', newFormData)
    }
  },
  { immediate: true, deep: true }
)

// 监听外部modelValue变化，同步到内部
watch(
  () => props.modelValue,
  (newVal) => {
    if (newVal && Object.keys(newVal).length) {
      formData.value = { ...newVal }
    }
  },
  { deep: true }
)

// 监听内部表单变化，同步到外部
watch(
  formData,
  (val) => {
    emit('update:modelValue', { ...val })
    emit('change', { ...val })
  },
  { deep: true }
)
</script>

<style scoped>
.dynamic-form {
  width: 100%;
}

.unknown-type-tip {
  color: var(--text-placeholder);
  line-height: 32px;
  text-align: center;
  padding: 10px;
  border: 1px dashed var(--border-base);
  border-radius: 4px;
}
</style>