<template>
  <div class="statistics-page">
    <PageHeader
      title="统计分析"
      description="查看个人诊断数据统计、模型调用情况及病种分布分析"
    >
      <template #extra>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          @change="loadStatistics"
        />
      </template>
    </PageHeader>

    <!-- 统计卡片区域 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #165DFF 0%, #4080FF 100%);">
            <el-icon :size="28"><Document /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ stats.totalDiagnosis || 0 }}</div>
            <div class="stat-label">总诊断次数</div>
            <div class="stat-trend" :class="stats.diagnosisTrend >= 0 ? 'up' : 'down'">
              <el-icon><TrendCharts /></el-icon>
              {{ Math.abs(stats.diagnosisTrend || 0) }}% 较上期
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #00B42A 0%, #23C343 100%);">
            <el-icon :size="28"><CircleCheck /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ stats.completedRate || '0%' }}</div>
            <div class="stat-label">诊断完成率</div>
            <div class="stat-trend up">
              <el-icon><Top /></el-icon>
              稳定
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #FF7D00 0%, #FF9A2E 100%);">
            <el-icon :size="28"><UserFilled /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ stats.totalPatients || 0 }}</div>
            <div class="stat-label">服务患者数</div>
            <div class="stat-trend up">
              <el-icon><TrendCharts /></el-icon>
              {{ stats.patientsTrend || 0 }}% 较上期
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #F53F3F 0%, #F76560 100%);">
            <el-icon :size="28"><DataAnalysis /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ stats.avgTime || '0s' }}</div>
            <div class="stat-label">平均诊断耗时</div>
            <div class="stat-trend" :class="stats.timeTrend <= 0 ? 'up' : 'down'">
              <el-icon><TrendCharts /></el-icon>
              {{ Math.abs(stats.timeTrend || 0) }}% 较上期
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <!-- 诊断趋势图 -->
      <el-col :span="16">
        <el-card class="common-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">诊断趋势分析</span>
              <el-radio-group v-model="trendType" size="small" @change="loadTrendChart">
                <el-radio-button value="day">按日</el-radio-button>
                <el-radio-button value="week">按周</el-radio-button>
                <el-radio-button value="month">按月</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <v-chart :option="trendOption" style="height: 350px" autoresize />
        </el-card>
      </el-col>

      <!-- 病种分布饼图 -->
      <el-col :span="8">
        <el-card class="common-card">
          <template #header>
            <span class="card-title">病种分布</span>
          </template>
          <v-chart :option="diseaseOption" style="height: 350px" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <!-- 模型调用统计 -->
      <el-col :span="12">
        <el-card class="common-card">
          <template #header>
            <span class="card-title">模型调用排行</span>
          </template>
          <v-chart :option="modelCallOption" style="height: 320px" autoresize />
        </el-card>
      </el-col>

      <!-- 风险等级分布 -->
      <el-col :span="12">
        <el-card class="common-card">
          <template #header>
            <span class="card-title">诊断风险等级分布</span>
          </template>
          <v-chart :option="riskOption" style="height: 320px" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <!-- 详细数据表格 -->
    <el-card class="common-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">诊断明细数据</span>
          <el-button type="primary" size="small" @click="exportData">
            <el-icon><Download /></el-icon>
            导出数据
          </el-button>
        </div>
      </template>
      <el-table :data="detailList" border class="common-table" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="patient_name" label="患者姓名" width="120" />
        <el-table-column prop="model_name" label="使用模型" width="150" />
        <el-table-column prop="disease_type" label="病种类型" width="120" />
        <el-table-column prop="risk_level" label="风险等级" width="100">
          <template #default="{ row }">
            <StatusTag :status="row.risk_level" :textMap="riskTextMap" :typeMap="riskTypeMap" />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="诊断时间" width="180" />
        <el-table-column prop="duration" label="耗时" width="100" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetail(row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
      <Pagination
        v-model:model-value="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        @change="loadDetailList"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import {
  LineChart,
  BarChart,
  PieChart,
  RadarChart
} from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DatasetComponent
} from 'echarts/components'
import PageHeader from '@/components/PageHeader.vue'
import StatusTag from '@/components/StatusTag.vue'
import Pagination from '@/components/Pagination.vue'
import { getPersonalStats, getDiseaseStats, getModelCallStats } from '@/api/statistics'
import { getMyTasks } from '@/api/task'
import { formatDateTime } from '@/utils/format'

use([
  CanvasRenderer,
  LineChart,
  BarChart,
  PieChart,
  RadarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DatasetComponent
])

const router = useRouter()

const loading = ref(false)
const dateRange = ref([])
const trendType = ref('day')
const stats = ref({})
const detailList = ref([])

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 风险等级映射
const riskTextMap = {
  '低风险': '低风险',
  '中风险': '中风险',
  '高风险': '高风险'
}
const riskTypeMap = {
  '低风险': 'success',
  '中风险': 'warning',
  '高风险': 'danger'
}

// 诊断趋势图配置
const trendOption = ref({
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'cross' }
  },
  legend: {
    data: ['诊断次数', '完成次数']
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: []
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      name: '诊断次数',
      type: 'line',
      smooth: true,
      data: [],
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(22, 93, 255, 0.3)' },
            { offset: 1, color: 'rgba(22, 93, 255, 0.05)' }
          ]
        }
      },
      lineStyle: {
        color: '#165DFF',
        width: 2
      },
      itemStyle: {
        color: '#165DFF'
      }
    },
    {
      name: '完成次数',
      type: 'line',
      smooth: true,
      data: [],
      lineStyle: {
        color: '#00B42A',
        width: 2
      },
      itemStyle: {
        color: '#00B42A'
      }
    }
  ]
})

// 病种分布饼图配置
const diseaseOption = ref({
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c} ({d}%)'
  },
  legend: {
    orient: 'vertical',
    left: 'left'
  },
  series: [
    {
      name: '病种分布',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: true,
        formatter: '{b}\n{d}%'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 16,
          fontWeight: 'bold'
        }
      },
      data: []
    }
  ],
  color: ['#165DFF', '#00B42A', '#FF7D00', '#F53F3F', '#722ED1', '#14C9C9']
})

// 模型调用排行配置
const modelCallOption = ref({
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'shadow' }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'value'
  },
  yAxis: {
    type: 'category',
    data: []
  },
  series: [
    {
      name: '调用次数',
      type: 'bar',
      data: [],
      barWidth: '50%',
      itemStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 1,
          y2: 0,
          colorStops: [
            { offset: 0, color: '#165DFF' },
            { offset: 1, color: '#4080FF' }
          ]
        },
        borderRadius: [0, 4, 4, 0]
      },
      label: {
        show: true,
        position: 'right'
      }
    }
  ]
})

// 风险等级分布配置
const riskOption = ref({
  tooltip: {
    trigger: 'item'
  },
  legend: {
    orient: 'vertical',
    left: 'left'
  },
  series: [
    {
      name: '风险等级',
      type: 'pie',
      radius: '60%',
      data: [],
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      },
      label: {
        formatter: '{b}: {c}例'
      }
    }
  ],
  color: ['#00B42A', '#FF7D00', '#F53F3F']
})

// 加载统计数据
const loadStatistics = async () => {
  loading.value = true
  try {
    const params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }

    // 加载基础统计
    const personalRes = await getPersonalStats(params)
    stats.value = personalRes

    // 加载趋势图数据
    await loadTrendChart()

    // 加载病种分布
    const diseaseRes = await getDiseaseStats(params)
    diseaseOption.value.series[0].data = diseaseRes.map(item => ({
      name: item.name,
      value: item.count
    }))

    // 加载模型调用排行
    const modelRes = await getModelCallStats(params)
    modelCallOption.value.yAxis.data = modelRes.map(item => item.model_name).reverse()
    modelCallOption.value.series[0].data = modelRes.map(item => item.call_count).reverse()

    // 加载风险等级分布
    riskOption.value.series[0].data = [
      { value: personalRes.low_risk_count || 0, name: '低风险' },
      { value: personalRes.medium_risk_count || 0, name: '中风险' },
      { value: personalRes.high_risk_count || 0, name: '高风险' }
    ]

    // 加载明细列表
    await loadDetailList()
  } catch (error) {
    console.error('加载统计数据失败', error)
    ElMessage.error('加载统计数据失败')
  } finally {
    loading.value = false
  }
}

// 加载趋势图
const loadTrendChart = async () => {
  // 模拟趋势数据，实际对接后端接口
  const mockData = {
    day: {
      xAxis: ['01-01', '01-02', '01-03', '01-04', '01-05', '01-06', '01-07'],
      diagnosis: [12, 19, 15, 22, 18, 25, 20],
      completed: [10, 18, 14, 20, 17, 24, 19]
    },
    week: {
      xAxis: ['第1周', '第2周', '第3周', '第4周'],
      diagnosis: [85, 92, 78, 105],
      completed: [80, 88, 75, 100]
    },
    month: {
      xAxis: ['10月', '11月', '12月', '1月'],
      diagnosis: [320, 350, 310, 380],
      completed: [305, 335, 298, 365]
    }
  }

  const data = mockData[trendType.value]
  trendOption.value.xAxis.data = data.xAxis
  trendOption.value.series[0].data = data.diagnosis
  trendOption.value.series[1].data = data.completed
}

// 加载明细列表
const loadDetailList = async () => {
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }

    const res = await getMyTasks(params)
    detailList.value = res.items || res || []
    pagination.total = res.total || detailList.value.length
  } catch (error) {
    console.error('加载明细列表失败', error)
  }
}

// 导出数据
const exportData = () => {
  ElMessage.success('数据导出功能开发中')
}

// 查看详情
const viewDetail = (row) => {
  router.push(`/tasks`)
}

onMounted(() => {
  loadStatistics()
})
</script>

<style scoped>
.statistics-page {
  width: 100%;
}

.stat-row {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.stat-trend {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.stat-trend.up {
  color: #00B42A;
}

.stat-trend.down {
  color: #F53F3F;
}

.chart-row {
  margin-bottom: 20px;
}
</style>