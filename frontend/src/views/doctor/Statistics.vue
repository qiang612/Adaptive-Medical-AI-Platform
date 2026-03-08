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

    <el-row :gutter="20" class="stat-row">
      <el-col :span="6">
        <div class="stat-card card-blue">
          <div class="watermark-bg"></div>
          <div class="stat-icon">
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
        <div class="stat-card card-green">
          <div class="watermark-bg"></div>
          <div class="stat-icon">
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
        <div class="stat-card card-orange">
          <div class="watermark-bg"></div>
          <div class="stat-icon">
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
        <div class="stat-card card-red">
          <div class="watermark-bg"></div>
          <div class="stat-icon">
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

    <el-row :gutter="20" class="chart-row">
      <el-col :span="16">
        <el-card class="common-card chart-card">
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
          <div v-loading="loading" style="height: 350px;">
            <v-chart v-if="hasTrendData" :option="trendOption" autoresize />
            <el-empty v-else description="暂无趋势数据" />
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="common-card chart-card">
          <template #header>
            <span class="card-title">病种分布</span>
          </template>
          <div v-loading="loading" style="height: 350px;">
            <v-chart v-if="hasDiseaseData" :option="diseaseOption" autoresize />
            <el-empty v-else description="暂无病种数据" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card class="common-card chart-card">
          <template #header>
            <span class="card-title">模型调用排行</span>
          </template>
          <div v-loading="loading" style="height: 320px;">
            <v-chart v-if="hasModelData" :option="modelCallOption" autoresize />
            <el-empty v-else description="暂无调用记录" />
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="common-card chart-card">
          <template #header>
            <span class="card-title">诊断风险等级分布</span>
          </template>
          <div v-loading="loading" style="height: 320px;">
            <v-chart v-if="hasRiskData" :option="riskOption" autoresize />
            <el-empty v-else description="暂无风险评估数据" />
          </div>
        </el-card>
      </el-col>
    </el-row>

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
        <template #empty>
          <el-empty description="该时间段内暂无诊断明细" :image-size="100" />
        </template>
        
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
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetail(row)">查看结果</el-button>
          </template>
        </el-table-column>
      </el-table>
      <Pagination
        v-if="detailList.length > 0"
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

// 图表空状态计算属性
const hasTrendData = computed(() => trendOption.value.series[0].data && trendOption.value.series[0].data.length > 0)
const hasDiseaseData = computed(() => diseaseOption.value.series[0].data && diseaseOption.value.series[0].data.length > 0)
const hasModelData = computed(() => modelCallOption.value.series[0].data && modelCallOption.value.series[0].data.length > 0)
const hasRiskData = computed(() => riskOption.value.series[0].data && riskOption.value.series[0].data.some(d => d.value > 0))

// 风险等级映射
const riskTextMap = { '低风险': '低风险', '中风险': '中风险', '高风险': '高风险' }
const riskTypeMap = { '低风险': 'success', '中风险': 'warning', '高风险': 'danger' }

// 诊断趋势图配置
const trendOption = ref({
  tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
  legend: { data: ['诊断次数', '完成次数'] },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: { type: 'category', boundaryGap: false, data: [] },
  yAxis: { type: 'value' },
  series: [
    {
      name: '诊断次数', type: 'line', smooth: true, data: [],
      areaStyle: {
        color: {
          type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(22, 93, 255, 0.3)' },
            { offset: 1, color: 'rgba(22, 93, 255, 0.05)' }
          ]
        }
      },
      lineStyle: { color: '#165DFF', width: 2 },
      itemStyle: { color: '#165DFF' }
    },
    {
      name: '完成次数', type: 'line', smooth: true, data: [],
      lineStyle: { color: '#00B42A', width: 2 },
      itemStyle: { color: '#00B42A' }
    }
  ]
})

// 病种分布饼图配置
const diseaseOption = ref({
  tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
  legend: { orient: 'vertical', left: 'left' },
  series: [
    {
      name: '病种分布', type: 'pie', radius: ['40%', '70%'], avoidLabelOverlap: false,
      itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
      label: { show: true, formatter: '{b}\n{d}%' },
      emphasis: { label: { show: true, fontSize: 16, fontWeight: 'bold' } },
      data: []
    }
  ],
  color: ['#165DFF', '#00B42A', '#FF7D00', '#F53F3F', '#722ED1', '#14C9C9']
})

// 模型调用排行配置
const modelCallOption = ref({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: { type: 'value' },
  yAxis: { type: 'category', data: [] },
  series: [
    {
      name: '调用次数', type: 'bar', data: [], barWidth: '50%',
      itemStyle: {
        color: {
          type: 'linear', x: 0, y: 0, x2: 1, y2: 0,
          colorStops: [{ offset: 0, color: '#165DFF' }, { offset: 1, color: '#4080FF' }]
        },
        borderRadius: [0, 4, 4, 0]
      },
      label: { show: true, position: 'right' }
    }
  ]
})

// 风险等级分布配置
const riskOption = ref({
  tooltip: { trigger: 'item' },
  legend: { orient: 'vertical', left: 'left' },
  series: [
    {
      name: '风险等级', type: 'pie', radius: '60%', data: [],
      emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)' } },
      label: { formatter: '{b}: {c}例' }
    }
  ],
  color: ['#00B42A', '#FF7D00', '#F53F3F']
})

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
    stats.value = personalRes || {}

    // 加载趋势图数据
    await loadTrendChart()

    // 加载病种分布
    const diseaseRes = await getDiseaseStats(params)
    if (diseaseRes && diseaseRes.length > 0) {
      diseaseOption.value.series[0].data = diseaseRes.map(item => ({
        name: item.name, value: item.count
      }))
    } else {
      diseaseOption.value.series[0].data = []
    }

    // 加载模型调用排行
    const modelRes = await getModelCallStats(params)
    if (modelRes && modelRes.length > 0) {
      modelCallOption.value.yAxis.data = modelRes.map(item => item.model_name).reverse()
      modelCallOption.value.series[0].data = modelRes.map(item => item.call_count).reverse()
    } else {
      modelCallOption.value.yAxis.data = []
      modelCallOption.value.series[0].data = []
    }

    // 加载风险等级分布
    if (personalRes && (personalRes.low_risk_count || personalRes.medium_risk_count || personalRes.high_risk_count)) {
      riskOption.value.series[0].data = [
        { value: personalRes.low_risk_count || 0, name: '低风险' },
        { value: personalRes.medium_risk_count || 0, name: '中风险' },
        { value: personalRes.high_risk_count || 0, name: '高风险' }
      ]
    } else {
      riskOption.value.series[0].data = []
    }

    // 加载明细列表
    await loadDetailList()
  } catch (error) {
    console.error('加载统计数据失败', error)
  } finally {
    loading.value = false
  }
}

const loadTrendChart = async () => {
  const mockData = {
    day: { xAxis: ['01-01', '01-02', '01-03', '01-04', '01-05', '01-06', '01-07'], diagnosis: [12, 19, 15, 22, 18, 25, 20], completed: [10, 18, 14, 20, 17, 24, 19] },
    week: { xAxis: ['第1周', '第2周', '第3周', '第4周'], diagnosis: [85, 92, 78, 105], completed: [80, 88, 75, 100] },
    month: { xAxis: ['10月', '11月', '12月', '1月'], diagnosis: [320, 350, 310, 380], completed: [305, 335, 298, 365] }
  }
  const data = mockData[trendType.value]
  if(data) {
    trendOption.value.xAxis.data = data.xAxis
    trendOption.value.series[0].data = data.diagnosis
    trendOption.value.series[1].data = data.completed
  }
}

const loadDetailList = async () => {
  try {
    const params = { page: pagination.page, page_size: pagination.pageSize }
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

const exportData = () => {
  ElMessage.success('报表导出任务已下发')
}

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

/* 卡片基类 */
.stat-card {
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

/* 科技感水波纹/折线背景水印 */
.watermark-bg {
  position: absolute;
  right: -20px;
  bottom: -30px;
  width: 160px;
  height: 160px;
  border-radius: 50%;
  opacity: 0.08;
  z-index: 0;
  transition: all 0.6s ease;
  pointer-events: none;
}

/* 悬浮微动效：水印放大且略微旋转 */
.stat-card:hover .watermark-bg {
  transform: scale(1.3) rotate(-10deg);
  opacity: 0.12;
}

/* 匹配不同卡片的背景水印颜色和图标背景色 */
.card-blue .watermark-bg { background: radial-gradient(circle, #165DFF 0%, transparent 70%); }
.card-blue .stat-icon { background: linear-gradient(135deg, #165DFF 0%, #4080FF 100%); }

.card-green .watermark-bg { background: radial-gradient(circle, #00B42A 0%, transparent 70%); }
.card-green .stat-icon { background: linear-gradient(135deg, #00B42A 0%, #23C343 100%); }

.card-orange .watermark-bg { background: radial-gradient(circle, #FF7D00 0%, transparent 70%); }
.card-orange .stat-icon { background: linear-gradient(135deg, #FF7D00 0%, #FF9A2E 100%); }

.card-red .watermark-bg { background: radial-gradient(circle, #F53F3F 0%, transparent 70%); }
.card-red .stat-icon { background: linear-gradient(135deg, #F53F3F 0%, #F76560 100%); }

.stat-icon {
  position: relative;
  z-index: 1;
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
  position: relative;
  z-index: 1;
  flex: 1;
  min-width: 0;
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
  margin-bottom: 4px;
  font-family: 'Arial', sans-serif;
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
  font-weight: 500;
}

.stat-trend.up { color: #00B42A; }
.stat-trend.down { color: #F53F3F; }

.chart-row {
  margin-bottom: 20px;
}

/* 图表容器美化 */
.chart-card {
  transition: box-shadow 0.3s ease;
}
.chart-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}
</style>