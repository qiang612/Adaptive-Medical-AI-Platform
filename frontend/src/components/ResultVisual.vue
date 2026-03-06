<template>
  <div v-if="result" class="result-visual">
    <!-- 基础诊断信息 -->
    <el-alert
      v-if="result.diagnosis_summary"
      :title="result.diagnosis_summary"
      :type="result.risk_level === '高风险' ? 'warning' : 'info'"
      show-icon
      class="mb-20"
      closable
    />

    <!-- 医学影像标注展示 -->
    <div v-if="result.annotated_image" class="image-section common-card">
      <h4>影像检测结果</h4>
      <div class="image-comparison">
        <div class="image-box">
          <p class="image-label">原始影像</p>
          <el-image
            :src="getImageUrl(result.original_image)"
            fit="contain"
            :preview-src-list="[getImageUrl(result.original_image)]"
            :initial-index="0"
          />
        </div>
        <div class="image-box">
          <p class="image-label">AI标注影像</p>
          <el-image
            :src="getImageUrl(result.annotated_image)"
            fit="contain"
            :preview-src-list="[getImageUrl(result.annotated_image)]"
            :initial-index="0"
          />
        </div>
      </div>

      <el-divider content-position="left">病灶检测详情</el-divider>
      <el-table :data="result.detections || []" border class="common-table" max-height="300">
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="class" label="病灶类别" width="150" />
        <el-table-column prop="confidence" label="置信度" width="120">
          <template #default="{ row }">
            <el-progress
              :percentage="(row.confidence * 100).toFixed(0)"
              :color="getConfidenceColor(row.confidence)"
              :stroke-width="8"
            />
          </template>
        </el-table-column>
        <el-table-column prop="bbox" label="坐标 (x1,y1,x2,y2)" />
        <el-table-column prop="size" label="病灶大小" width="120" />
      </el-table>
    </div>

    <!-- 风险仪表盘 -->
    <div v-if="result.risk_score !== undefined" class="chart-box common-card">
      <div class="card-header">
        <h4>疾病风险评估</h4>
        <div class="risk-header">
          <el-tag :type="getRiskTagType(result.risk_level)" size="large">
            {{ result.risk_level }}
          </el-tag>
          <span class="risk-score">风险评分: {{ (result.risk_score * 100).toFixed(1) }}/100</span>
        </div>
      </div>
      <v-chart :option="riskOption" style="height: 300px" autoresize />
    </div>

    <!-- 特征权重分析 -->
    <div v-if="result.feature_weights" class="chart-box common-card">
      <h4>影响因素权重分析</h4>
      <v-chart :option="weightOption" style="height: 350px" autoresize />
    </div>

    <!-- 详细诊断报告 -->
    <div v-if="result.diagnosis_detail" class="common-card">
      <h4>详细诊断说明</h4>
      <div class="diagnosis-detail">
        <p v-html="result.diagnosis_detail"></p>
      </div>
    </div>

    <!-- 医疗建议 -->
    <div v-if="result.recommendation" class="common-card">
      <h4>诊疗建议</h4>
      <el-timeline>
        <el-timeline-item
          v-for="(item, index) in formatRecommendation(result.recommendation)"
          :key="index"
          :type="index === 0 ? 'primary' : ''"
        >
          {{ item }}
        </el-timeline-item>
      </el-timeline>
    </div>

    <!-- 参考资料 -->
    <div v-if="result.references && result.references.length" class="common-card">
      <h4>参考医学指南</h4>
      <ul class="reference-list">
        <li v-for="(item, index) in result.references" :key="index">
          [{{ index + 1 }}] {{ item }}
        </li>
      </ul>
    </div>
  </div>

  <div v-else class="empty-result">
    <el-empty description="暂无诊断结果数据" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { GaugeChart, BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'

use([
  CanvasRenderer,
  GaugeChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const props = defineProps({
  result: {
    type: Object,
    default: null
  }
})

// 图片URL处理
const getImageUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  const filename = path.split(/[/\\]/).pop()
  if (path.includes('images')) {
    return `/uploads/images/${filename}`
  }
  return `/uploads/tables/${filename}`
}

// 置信度颜色映射
const getConfidenceColor = (conf) => {
  if (conf > 0.8) return '#00B42A'
  if (conf > 0.6) return '#FF7D00'
  return '#F53F3F'
}

// 风险等级标签类型
const getRiskTagType = (level) => {
  const map = { '低风险': 'success', '中风险': 'warning', '高风险': 'danger' }
  return map[level] || 'info'
}

// 格式化建议内容
const formatRecommendation = (text) => {
  if (!text) return []
  return text.split(/\n|；|。/).filter(item => item.trim())
}

// 风险仪表盘配置
const riskOption = computed(() => ({
  series: [{
    type: 'gauge',
    startAngle: 180,
    endAngle: 0,
    min: 0,
    max: 100,
    splitNumber: 5,
    axisLine: {
      lineStyle: {
        width: 25,
        color: [
          [0.3, '#00B42A'],
          [0.7, '#FF7D00'],
          [1, '#F53F3F']
        ]
      }
    },
    pointer: {
      itemStyle: {
        color: 'auto'
      },
      width: 5
    },
    axisTick: {
      distance: -25,
      length: 8,
      lineStyle: {
        color: '#fff',
        width: 2
      }
    },
    splitLine: {
      distance: -25,
      length: 25,
      lineStyle: {
        color: '#fff',
        width: 4
      }
    },
    axisLabel: {
      color: 'auto',
      distance: 35,
      fontSize: 13
    },
    detail: {
      valueAnimation: true,
      formatter: '{value}',
      color: 'auto',
      fontSize: 40,
      fontWeight: 'bold',
      offsetCenter: [0, '40%']
    },
    data: [{
      value: (props.result?.risk_score || 0) * 100,
      name: '患病风险概率'
    }]
  }]
}))

// 特征权重柱状图配置
const weightOption = computed(() => {
  const weights = props.result?.feature_weights || {}
  const sortedKeys = Object.keys(weights).sort((a, b) => weights[b] - weights[a]).slice(0, 10)
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: '{b}: {c} 权重占比'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      max: 1,
      axisLabel: {
        formatter: '{value}'
      }
    },
    yAxis: {
      type: 'category',
      data: sortedKeys,
      axisLabel: {
        fontSize: 13,
        interval: 0
      }
    },
    series: [{
      type: 'bar',
      data: sortedKeys.map(k => ({
        value: weights[k],
        itemStyle: {
          color: weights[k] > 0.3 ? '#F53F3F' : weights[k] > 0.2 ? '#FF7D00' : '#165DFF'
        }
      })),
      label: {
        show: true,
        position: 'right',
        formatter: '{c}',
        fontSize: 12
      },
      barWidth: '40%'
    }]
  }
})
</script>

<style scoped>
.result-visual {
  width: 100%;
}

.empty-result {
  padding: 60px 0;
}

h4 {
  margin-bottom: 20px;
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 600;
  border-left: 4px solid var(--primary-color);
  padding-left: 12px;
  line-height: 1.2;
}

.image-comparison {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.image-box {
  flex: 1;
  min-width: 300px;
  text-align: center;
}

.image-label {
  margin-bottom: 10px;
  font-weight: 600;
  color: var(--text-regular);
}

.image-box :deep(.el-image) {
  width: 100%;
  height: 350px;
  border: 2px solid var(--border-base);
  border-radius: 8px;
  background: #fff;
}

.risk-header {
  display: flex;
  align-items: center;
  gap: 20px;
}

.risk-score {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-secondary);
}

.diagnosis-detail {
  padding: 15px;
  background: var(--bg-hover);
  border-radius: 6px;
  line-height: 1.8;
  color: var(--text-regular);
}

.reference-list {
  padding-left: 20px;
  line-height: 1.8;
  color: var(--text-regular);
}

.reference-list li {
  margin-bottom: 8px;
}

.mb-20 {
  margin-bottom: 20px;
}
</style>