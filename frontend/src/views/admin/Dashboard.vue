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

    <!-- 核心指标卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :span="6">
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
      <el-col :span="6">
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
      <el-col :span="6">
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
      <el-col :span="6">
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

    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <!-- 诊断趋势图 -->
      <el-col :span="16">
        <el-card class="common-card">
          <template #header>
            <span class="card-title">诊断任务趋势</span>
          </template>
          <v-chart :option="trendOption" style="height: 350px" autoresize />
        </el-card>
      </el-col>

      <!-- 病种分布 -->
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
      <!-- 模型调用排行 -->
      <el-col :span="8">
        <el-card class="common-card">
          <template #header>
            <span class="card-title">模型调用排行</span>
          </template>
          <v-chart :option="modelCallOption" style="height: 320px" autoresize />
        </el-card>
      </el-col>

      <!-- 用户活跃度 -->
      <el-col :span="8">
        <el-card class="common-card">
          <template #header>
            <span class="card-title">用户活跃度TOP10</span>
          </template>
          <v-chart :option="userActiveOption" style="height: 320px" autoresize />
        </el-card>
      </el-col>

      <!-- 系统资源监控 -->
      <el-col :span="8">
        <el-card class="common-card">
          <template #header>
            <span class="card-title">系统资源监控</span>
          </template>
          <v-chart :option="resourceOption" style="height: 320px" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <!-- 实时数据表格 -->
    <el-row :gutter="20">
      <!-- 最新任务 -->
      <el-col :span="12">
        <el-card class="common-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">最新任务</span>
              <el-button type="primary" link size="small" @click="$router.push('/admin/tasks')">查看全部</el-button>
            </div>
          </template>
          <el-table :data="latestTasks" border class="common-table" size="small" max-height="300">
            <el-table-column prop="task_id" label="任务ID" width="120" show-overflow-tooltip />
            <el-table-column prop="model_name" label="模型" width="120" />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <StatusTag :status="row.status" size="small" />
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="160" />
          </el-table>
        </el-card>
      </el-col>

      <!-- 最新用户 -->
      <el-col :span="12">
        <el-card class="common-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">最新注册用户</span>
              <el-button type="primary" link size="small" @click="$router.push('/admin/users')">查看全部</el-button>
            </div>
          </template>
          <el-table :data="latestUsers" border class="common-table" size="small" max-height="300">
            <el-table-column prop="username" label="用户名" width="100" />
            <el-table-column prop="full_name" label="姓名" width="100" />
            <el-table-column prop="role" label="角色" width="80">
              <template #default="{ row }">
                <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'" size="small">
                  {{ row.role === 'admin' ? '管理员' : '医生' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="注册时间" width="160" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
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
const stats = ref({})
const latestTasks = ref([])
const latestUsers = ref([])

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
      center: ['60%', '50%'],
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
      fontSize: 11
    }
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
      fontSize: 11
    }
  },
  series: [
    {
      name: '诊断次数',
      type: 'bar',
      data: [],
      barWidth: '50%',
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
      { name: 'CPU使用率', max: 100 },
      { name: '内存使用率', max: 100 },
      { name: '磁盘使用率', max: 100 },
      { name: '网络带宽', max: 100 },
      { name: 'GPU使用率', max: 100 },
      { name: '队列负载', max: 100 }
    ],
    splitNumber: 4,
    shape: 'circle'
  },
  series: [
    {
      name: '系统资源',
      type: 'radar',
      data: [
        {
          value: [],
          name: '当前使用率',
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
  try {
    // 加载平台基础统计
    const platformRes = await getPlatformStats({ time_range: timeRange.value })
    stats.value = platformRes

    // 加载趋势数据
    const trendRes = await getTrendStats({ time_range: timeRange.value })
    trendOption.value.xAxis.data = trendRes.xAxis
    trendOption.value.series[0].data = trendRes.total
    trendOption.value.series[1].data = trendRes.completed
    trendOption.value.series[2].data = trendRes.failed

    // 病种分布数据
    diseaseOption.value.series[0].data = platformRes.disease_distribution || [
      { name: '宫颈癌', value: 1256 },
      { name: '冠心病', value: 987 },
      { name: '肺结节', value: 865 },
      { name: '糖尿病', value: 542 },
      { name: '眼底病变', value: 321 },
      { name: '其他', value: 189 }
    ]

    // 模型调用排行
    const modelRank = platformRes.model_rank || []
    modelCallOption.value.yAxis.data = modelRank.map(item => item.model_name).reverse()
    modelCallOption.value.series[0].data = modelRank.map(item => item.call_count).reverse()

    // 用户活跃度
    const userRank = platformRes.user_rank || []
    userActiveOption.value.yAxis.data = userRank.map(item => item.full_name).reverse()
    userActiveOption.value.series[0].data = userRank.map(item => item.diagnosis_count).reverse()

    // 系统资源
    resourceOption.value.series[0].data[0].value = platformRes.resource_usage || [45, 62, 38, 25, 78, 32]

    // 最新任务
    latestTasks.value = platformRes.latest_tasks || []

    // 最新用户
    latestUsers.value = platformRes.latest_users || []

  } catch (error) {
    console.error('加载看板数据失败', error)
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

.stat-row {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
}

.stat-card.primary {
  background: linear-gradient(135deg, #165DFF 0%, #4080FF 100%);
  color: #fff;
}

.stat-card.success {
  background: linear-gradient(135deg, #00B42A 0%, #23C343 100%);
  color: #fff;
}

.stat-card.warning {
  background: linear-gradient(135deg, #FF7D00 0%, #FF9A2E 100%);
  color: #fff;
}

.stat-card.danger {
  background: linear-gradient(135deg, #F53F3F 0%, #F76560 100%);
  color: #fff;
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
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
  font-size: 36px;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.85;
  margin-bottom: 6px;
}

.stat-trend {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  opacity: 0.9;
}

.stat-trend.up {
  color: #fff;
}

.stat-trend.down {
  color: #FFECE8;
}

.chart-row {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>