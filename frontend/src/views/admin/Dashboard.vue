<template>
  <div class="dashboard-page">
    <PageHeader
      title="数据看板"
      description="平台全维度运行数据统计与分析"
    >
      <template #extra>
        <el-radio-group v-model="timeRange" size="small" @change="loadAllData">
          <el-radio-button value="today">今日</el-radio-button>
          <el-radio-button value="week">本周</el-radio-button>
          <el-radio-button value="month">本月</el-radio-button>
        </el-radio-group>
      </template>
    </PageHeader>

    <div class="welcome-banner">
      <div class="welcome-text">
        <h2>{{ greeting }}，管理员，今日系统运行平稳！</h2>
        <p>自适应AI医疗大模型正在为您提供高精度、高并发的辅助推理服务。</p>
      </div>
      <div class="health-score">
        <div class="score-label">系统健康度</div>
        <div class="score-value">98<span class="score-unit">/100</span></div>
      </div>
    </div>

    <el-row :gutter="20" class="stat-row" v-loading="loading">
      <el-col :xs="24" :sm="12" :md="12" :lg="6" :xl="6">
        <div class="stat-card primary">
          <div class="stat-icon">
            <el-icon :size="32"><Document /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ stats.totalTasks || 0 }}</div>
            <div class="stat-label">总诊断任务</div>
            <div class="stat-trend up">
              <el-icon><Top /></el-icon>
              {{ stats.taskGrowth || 0 }}% 较上期
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="12" :lg="6" :xl="6">
        <div class="stat-card success">
          <div class="stat-icon">
            <el-icon :size="32"><UserFilled /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ stats.activeUsers || 0 }}</div>
            <div class="stat-label">活跃用户</div>
            <div class="stat-trend up">
              <el-icon><Top /></el-icon>
              {{ stats.userGrowth || 0 }}% 较上期
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="12" :lg="6" :xl="6">
        <div class="stat-card warning">
          <div class="stat-icon">
            <el-icon :size="32"><Box /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ stats.activeModels || 0 }}</div>
            <div class="stat-label">在线模型</div>
            <div class="stat-trend">
              共 {{ stats.totalModels || 0 }} 个模型
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="12" :lg="6" :xl="6">
        <div class="stat-card danger">
          <div class="stat-icon">
            <el-icon :size="32"><Odometer /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ stats.avgResponseTime || '0ms' }}</div>
            <div class="stat-label">平均响应时间</div>
            <div class="stat-trend" :class="stats.timeTrend <= 0 ? 'up' : 'down'">
              <el-icon><TrendCharts /></el-icon>
              {{ Math.abs(stats.timeTrend || 0) }}% 较上期
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="16">
        <el-card class="common-card" v-loading="loading">
          <template #header>
            <span class="card-title">诊断任务趋势</span>
          </template>
          <v-chart :option="trendOption" style="height: 350px" autoresize />
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="8">
        <el-card class="common-card" v-loading="loading">
          <template #header>
            <span class="card-title">病种分布</span>
          </template>
          <v-chart :option="diseaseOption" style="height: 350px" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="12">
        <el-card class="common-card" v-loading="loading">
          <template #header>
            <span class="card-title">模型调用排行</span>
          </template>
          <v-chart :option="modelCallOption" style="height: 320px" autoresize />
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="12">
        <el-card class="common-card" v-loading="loading">
          <template #header>
            <span class="card-title">用户活跃度TOP10</span>
          </template>
          <v-chart :option="userActiveOption" style="height: 320px" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="16">
        <el-card class="common-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="card-title">最新任务</span>
              <el-button type="primary" link size="small" @click="$router.push('/admin/tasks')">查看全部</el-button>
            </div>
          </template>
          
          <el-skeleton :rows="6" animated v-if="loading" />
          
          <el-empty description="暂无推理任务" :image-size="80" v-else-if="latestTasks.length === 0" />
          
          <el-table v-else :data="latestTasks" border stripe class="common-table" size="small" max-height="320">
            <el-table-column prop="task_id" label="任务ID" width="180" show-overflow-tooltip />
            <el-table-column prop="model_name" label="模型" min-width="120" />
            <el-table-column prop="doctor_name" label="提交医生" width="120" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <StatusTag :status="row.status" size="small" />
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="160" />
          </el-table>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="8">
        <el-card class="common-card" v-loading="loading">
          <template #header>
            <span class="card-title">系统资源监控</span>
          </template>
          <v-chart :option="resourceOption" style="height: 320px" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="common-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="card-title">最新注册用户</span>
              <el-button type="primary" link size="small" @click="$router.push('/admin/users')">查看全部</el-button>
            </div>
          </template>

          <el-skeleton :rows="5" animated v-if="loading" />

          <el-empty description="暂无新注册用户" :image-size="80" v-else-if="latestUsers.length === 0" />

          <el-table v-else :data="latestUsers" border stripe class="common-table" size="small" max-height="300">
            <el-table-column prop="username" label="用户名" width="150" />
            <el-table-column prop="full_name" label="姓名" width="150" />
            <el-table-column prop="department" label="科室" width="150" />
            <el-table-column prop="role" label="角色" width="100">
              <template #default="{ row }">
                <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'" size="small">
                  {{ row.role === 'admin' ? '管理员' : '医生' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="注册时间" min-width="160" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import {
  LineChart,
  BarChart,
  PieChart,
  RadarChart,
  GaugeChart
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
import { getPlatformStats, getTrendStats } from '@/api/statistics'

// 注册ECharts组件
use([
  CanvasRenderer,
  LineChart,
  BarChart,
  PieChart,
  RadarChart,
  GaugeChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DatasetComponent
])

const timeRange = ref('today')
const loading = ref(true) 
const stats = ref({})
const latestTasks = ref([])
const latestUsers = ref([])

// 动态问候语
const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return '上午好'
  if (hour < 18) return '下午好'
  return '晚上好'
})

// 诊断趋势图配置
const trendOption = ref({
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'cross' }
  },
  legend: {
    data: ['总任务数', '完成数', '失败数']
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
      name: '总任务数',
      type: 'line',
      smooth: true,
      data: [],
      lineStyle: { color: '#165DFF', width: 2 },
      itemStyle: { color: '#165DFF' },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(22, 93, 255, 0.2)' },
            { offset: 1, color: 'rgba(22, 93, 255, 0)' }
          ]
        }
      }
    },
    {
      name: '完成数',
      type: 'line',
      smooth: true,
      data: [],
      lineStyle: { color: '#00B42A', width: 2 },
      itemStyle: { color: '#00B42A' }
    },
    {
      name: '失败数',
      type: 'line',
      smooth: true,
      data: [],
      lineStyle: { color: '#F53F3F', width: 2 },
      itemStyle: { color: '#F53F3F' }
    }
  ]
})

// 病种分布配置
const diseaseOption = ref({
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c} ({d}%)'
  },
  legend: {
    orient: 'vertical',
    left: 'left',
    top: 'center'
  },
  series: [
    {
      name: '病种分布',
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['65%', '50%'], // 调整饼图中心，避免和图例重叠
      itemStyle: {
        borderRadius: 8,
        borderColor: '#fff',
        borderWidth: 2
      },
      data: [],
      color: ['#165DFF', '#00B42A', '#FF7D00', '#F53F3F', '#722ED1', '#14C9C9', '#FF9A2E', '#86909C']
    }
  ]
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
    data: [],
    axisLabel: {
      interval: 0,
      fontSize: 12
    }
  },
  series: [
    {
      name: '调用次数',
      type: 'bar',
      data: [],
      barWidth: '40%',
      itemStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 1, y2: 0,
          colorStops: [
            { offset: 0, color: '#165DFF' },
            { offset: 1, color: '#4080FF' }
          ]
        },
        borderRadius: [0, 4, 4, 0]
      },
      label: {
        show: true,
        position: 'right',
        fontSize: 11
      }
    }
  ]
})

// 用户活跃度配置
const userActiveOption = ref({
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
    data: [],
    axisLabel: {
      interval: 0,
      fontSize: 12
    }
  },
  series: [
    {
      name: '诊断次数',
      type: 'bar',
      data: [],
      barWidth: '40%',
      itemStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 1, y2: 0,
          colorStops: [
            { offset: 0, color: '#00B42A' },
            { offset: 1, color: '#23C343' }
          ]
        },
        borderRadius: [0, 4, 4, 0]
      },
      label: {
        show: true,
        position: 'right',
        fontSize: 11
      }
    }
  ]
})

// 系统资源监控配置
const resourceOption = ref({
  tooltip: {
    trigger: 'item'
  },
  radar: {
    indicator: [
      { name: 'CPU', max: 100 },
      { name: '内存', max: 100 },
      { name: '磁盘', max: 100 },
      { name: '网络', max: 100 },
      { name: 'GPU', max: 100 },
      { name: '队列', max: 100 }
    ],
    splitNumber: 4,
    shape: 'circle',
    radius: '65%' // 适配 8 span 的宽度
  },
  series: [
    {
      name: '系统资源',
      type: 'radar',
      data: [
        {
          value: [],
          name: '当前使用率(%)',
          areaStyle: {
            color: 'rgba(22, 93, 255, 0.3)'
          },
          lineStyle: {
            color: '#165DFF',
            width: 2
          },
          itemStyle: {
            color: '#165DFF'
          }
        }
      ]
    }
  ]
})

// 加载所有数据
const loadAllData = async () => {
  loading.value = true
  try {
    const platformRes = await getPlatformStats({ time_range: timeRange.value })
    stats.value = platformRes

    const trendRes = await getTrendStats({ time_range: timeRange.value })
    trendOption.value.xAxis.data = trendRes.xAxis
    trendOption.value.series[0].data = trendRes.total
    trendOption.value.series[1].data = trendRes.completed
    trendOption.value.series[2].data = trendRes.failed

    diseaseOption.value.series[0].data = platformRes.disease_distribution || [
      { name: '宫颈癌', value: 1256 },
      { name: '冠心病', value: 987 },
      { name: '肺结节', value: 865 },
      { name: '糖尿病', value: 542 },
      { name: '眼底病变', value: 321 },
      { name: '其他', value: 189 }
    ]

    const modelRank = platformRes.model_rank || []
    modelCallOption.value.yAxis.data = modelRank.map(item => item.model_name).reverse()
    modelCallOption.value.series[0].data = modelRank.map(item => item.call_count).reverse()

    const userRank = platformRes.user_rank || []
    userActiveOption.value.yAxis.data = userRank.map(item => item.full_name).reverse()
    userActiveOption.value.series[0].data = userRank.map(item => item.diagnosis_count).reverse()

    resourceOption.value.series[0].data[0].value = platformRes.resource_usage || [45, 62, 38, 25, 78, 32]

    latestTasks.value = platformRes.latest_tasks || []
    latestUsers.value = platformRes.latest_users || []

  } catch (error) {
    console.error('加载看板数据失败', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadAllData()
})
</script>

<style scoped>
.dashboard-page {
  width: 100%;
}

/* 新增 Welcome Banner 样式 */
.welcome-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px;
  background: linear-gradient(135deg, #e8f0ff 0%, #f4f8ff 100%);
  border-radius: 12px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(22, 93, 255, 0.05);
}

.welcome-text h2 {
  margin: 0 0 8px 0;
  font-size: 22px;
  font-weight: 600;
  color: #1d2129;
}

.welcome-text p {
  margin: 0;
  font-size: 14px;
  color: #4e5969;
}

.health-score {
  text-align: right;
  background: #ffffff;
  padding: 12px 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.score-label {
  font-size: 13px;
  color: #86909c;
  margin-bottom: 4px;
}

.score-value {
  font-size: 32px;
  font-weight: 700;
  color: #00b42a;
  line-height: 1;
}

.score-unit {
  font-size: 14px;
  color: #86909c;
  margin-left: 2px;
}

.stat-row {
  margin-bottom: 24px;
}

/* ========== 卡片样式 ========== */
.stat-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px;
  border-radius: 12px;
  color: #fff; 
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  margin-bottom: 20px;
}

.stat-card:hover {
  transform: translateY(-4px);
}

/* 使用柔和的渐变色配方 */
.stat-card.primary { background: linear-gradient(135deg, #7ba8ff 0%, #165DFF 100%); }
.stat-card.success { background: linear-gradient(135deg, #6ae086 0%, #00B42A 100%); }
.stat-card.warning { background: linear-gradient(135deg, #ffb86c 0%, #FF7D00 100%); }
.stat-card.danger { background: linear-gradient(135deg, #ff9894 0%, #F53F3F 100%); }

.stat-card .stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%; 
  background: rgba(255, 255, 255, 0.2); 
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: #fff;
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-number {
  font-size: 36px;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 4px;
  color: #ffffff; 
}

/* 核心优化：提升说明文字的辨识度 */
.stat-label {
  font-size: 15px;      /* 稍微调大字号 */
  font-weight: 500;     /* 增加字重 */
  color: #ffffff;       /* 强制纯白色，摆脱透明度导致的暗淡 */
  margin-bottom: 6px;
  opacity: 1;           /* 确保不被父级透明度干扰 */
}

.stat-trend {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  opacity: 0.85;
}

.stat-trend.up,
.stat-trend.down {
  color: #ffffff;
}

.chart-row {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

@media screen and (max-width: 768px) {
  .welcome-banner {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  .health-score {
    width: 100%;
    text-align: left;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-sizing: border-box;
  }
}
</style>