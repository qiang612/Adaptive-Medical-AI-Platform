<template>
  <el-form :model="formData" label-width="120px" class="dynamic-form">
    <el-form-item
      v-for="(propDef, key) in schema.properties"
      :key="key"
      :label="propDef.title || key"
      :required="schema.required?.includes(key)"
      :prop="key"
      :rules="getFormRules(propDef, key, schema.required?.includes(key))"
    >
      <!-- 数字输入框 -->
      <el-input-number
        v-if="propDef.type === 'number' || propDef.type === 'integer'"
        v-model="formData[key]"
        :min="propDef.minimum ?? -Infinity"
        :max="propDef.maximum ?? Infinity"
        :step="propDef.step ?? (propDef.type === 'integer' ? 1 : 0.1)"
        :precision="propDef.precision ?? (propDef.type === 'integer' ? 0 : 2)"
        style="width: 100%"
        :placeholder="`请输入${propDef.title || key}`"
        :disabled="propDef.disabled"
      />

      <!-- 单选下拉框 -->
      <el-select
        v-else-if="propDef.type === 'string' && propDef.enum"
        v-model="formData[key]"
        style="width: 100%"
        :placeholder="`请选择${propDef.title || key}`"
        :disabled="propDef.disabled"
        clearable
      >
        <el-option
          v-for="item in propDef.enum"
          :key="item"
          :label="item"
          :value="item"
        />
      </el-select>

      <!-- 日期选择器 -->
      <el-date-picker
        v-else-if="propDef.type === 'string' && propDef.format === 'date'"
        v-model="formData[key]"
        type="date"
        style="width: 100%"
        :placeholder="`请选择${propDef.title || key}`"
        :disabled="propDef.disabled"
        value-format="YYYY-MM-DD"
      />

      <!-- 日期时间选择器 -->
      <el-date-picker
        v-else-if="propDef.type === 'string' && propDef.format === 'datetime'"
        v-model="formData[key]"
        type="datetime"
        style="width: 100%"
        :placeholder="`请选择${propDef.title || key}`"
        :disabled="propDef.disabled"
        value-format="YYYY-MM-DD HH:mm:ss"
      />

      <!-- 文本域 -->
      <el-input
        v-else-if="propDef.type === 'string' && propDef.format === 'textarea'"
        v-model="formData[key]"
        type="textarea"
        :rows="propDef.rows ?? 4"
        :placeholder="`请输入${propDef.title || key}`"
        :maxlength="propDef.maxLength ?? undefined"
        :disabled="propDef.disabled"
        clearable
        show-word-limit
      />

      <!-- 密码输入框 -->
      <el-input
        v-else-if="propDef.type === 'string' && propDef.format === 'password'"
        v-model="formData[key]"
        type="password"
        :placeholder="`请输入${propDef.title || key}`"
        :maxlength="propDef.maxLength ?? undefined"
        :disabled="propDef.disabled"
        clearable
        show-password
      />

      <!-- 复选框组 -->
      <el-checkbox-group
        v-else-if="propDef.type === 'array' && propDef.items?.enum"
        v-model="formData[key]"
      >
        <el-checkbox
          v-for="item in propDef.items.enum"
          :key="item"
          :label="item"
          :disabled="propDef.disabled"
        />
      </el-checkbox-group>

      <!-- 开关 -->
      <el-switch
        v-else-if="propDef.type === 'boolean'"
        v-model="formData[key]"
        :disabled="propDef.disabled"
        :active-text="propDef.activeText || '是'"
        :inactive-text="propDef.inactiveText || '否'"
      />

      <!-- 普通文本输入框 -->
      <el-input
        v-else-if="propDef.type === 'string'"
        v-model="formData[key]"
        :placeholder="`请输入${propDef.title || key}`"
        :maxlength="propDef.maxLength ?? undefined"
        :disabled="propDef.disabled"
        clearable
      />

      <!-- 兜底：未知类型提示 -->
      <div v-else class="unknown-type-tip">
        暂不支持 {{ propDef.type }} 类型的输入控件
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

const getFormRules = (propDef, key, isRequired) => {
  const rules = []
  if (isRequired) {
    rules.push({ required: true, message: `${propDef.title || key}为必填项`, trigger: 'blur' })
  }
  if (propDef.pattern) {
    rules.push({ pattern: new RegExp(propDef.pattern), message: propDef.patternMessage || '格式不正确', trigger: 'blur' })
  }
  if (propDef.minLength) {
    rules.push({ min: propDef.minLength, message: `最少输入${propDef.minLength}个字符`, trigger: 'blur' })
  }
  if (propDef.maxLength) {
    rules.push({ max: propDef.maxLength, message: `最多输入${propDef.maxLength}个字符`, trigger: 'blur' })
  }
  return rules
}

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

watch(
  () => props.modelValue,
  (newVal) => {
    if (newVal && Object.keys(newVal).length) {
      formData.value = { ...newVal }
    }
  },
  { deep: true }
)

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