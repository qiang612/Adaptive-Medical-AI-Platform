<template>
  <div class="teaching-case-page">
    <PageHeader
      title="教学案例库"
      description="浏览和学习典型病例，提升临床诊断思维能力与AI协同阅片经验"
    />

    <el-row :gutter="24" class="library-container">
      <el-col :span="5">
        <el-card class="sidebar-card" shadow="never">
          <div class="sidebar-section">
            <div class="section-title">
              <el-icon><Menu /></el-icon> 病种分类
            </div>
            <ul class="category-list">
              <li :class="{ active: searchForm.diseaseType === '' }" @click="toggleDisease('')">
                全部病种
              </li>
              <li 
                v-for="item in diseaseOptions" 
                :key="item" 
                :class="{ active: searchForm.diseaseType === item }" 
                @click="toggleDisease(item)"
              >
                {{ item }}
              </li>
            </ul>
          </div>

          <el-divider border-style="dashed" />

          <div class="sidebar-section">
            <div class="section-title">
              <el-icon><Collection /></el-icon> 病例类型
            </div>
            <ul class="category-list">
              <li :class="{ active: searchForm.caseType === '' }" @click="toggleCaseType('')">
                所有类型
              </li>
              <li 
                v-for="item in caseTypeOptions" 
                :key="item" 
                :class="{ active: searchForm.caseType === item }" 
                @click="toggleCaseType(item)"
              >
                {{ item }}
              </li>
            </ul>
          </div>
        </el-card>
      </el-col>

      <el-col :span="19">
        <div class="main-content-wrapper">
          <div class="resource-search-bar">
            <el-input
              v-model="searchForm.keyword"
              placeholder="搜索案例标题、关键词、阳性特征..."
              class="search-input"
              clearable
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            
            <el-radio-group v-model="searchForm.difficulty" class="difficulty-group" @change="loadCaseList">
              <el-radio-button value="">全部难度</el-radio-button>
              <el-radio-button value="入门">入门</el-radio-button>
              <el-radio-button value="进阶">进阶</el-radio-button>
              <el-radio-button value="高级">高级</el-radio-button>
            </el-radio-group>
          </div>

          <div v-loading="loading" class="case-grid">
            <el-row :gutter="20">
              <el-col :span="8" v-for="item in caseList" :key="item.id">
                <div class="case-card" @click="viewCaseDetail(item.id)">
                  <div class="case-cover">
                    <div class="cover-placeholder">
                      <el-icon :size="48"><Reading /></el-icon>
                      <span class="cover-text">{{ item.disease_type }}</span>
                    </div>
                    
                    <div class="case-tags">
                      <el-tag :type="getDifficultyType(item.difficulty)" effect="dark" size="small">{{ item.difficulty }}</el-tag>
                    </div>

                    <div class="hover-overlay">
                      <h5><el-icon><Key /></el-icon> 关键阳性发现</h5>
                      <ul v-if="item.findings && item.findings.length > 0">
                        <li v-for="(finding, idx) in item.findings" :key="idx">{{ finding }}</li>
                      </ul>
                      <p v-else class="default-finding">该病例具有典型的影像学特征，点击查看完整AI分析报告与医生解读。</p>
                    </div>
                  </div>

                  <div class="case-content">
                    <h3 class="case-title">{{ item.title }}</h3>
                    <p class="case-desc">{{ item.description }}</p>
                    <div class="case-meta">
                      <el-tag size="small" type="info" class="type-tag">{{ item.case_type }}</el-tag>
                      <div class="meta-right">
                        <span><el-icon><View /></el-icon> {{ item.view_count || 0 }}</span>
                        <span><el-icon><Star /></el-icon> {{ item.star_count || 0 }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </el-col>
            </el-row>

            <div v-if="caseList.length === 0 && !loading" class="empty-list">
              <el-empty description="该分类下暂无教学案例，请尝试其他关键词或分类" :image-size="120" />
            </div>

            <div class="pagination-container" v-if="caseList.length > 0">
              <Pagination
                v-model:model-value="pagination.page"
                v-model:page-size="pagination.pageSize"
                :total="pagination.total"
                @change="loadCaseList"
              />
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import Pagination from '@/components/Pagination.vue'
import { getTeachingCases } from '@/api/teaching'

const router = useRouter()
const loading = ref(false)
const caseList = ref([])

// 左侧分类静态配置
const diseaseOptions = ['宫颈癌', '肺结节', '冠心病', '糖尿病', '眼底病变']
const caseTypeOptions = ['典型病例', '疑难病例', '误诊病例', '罕见病例']

// 搜索表单
const searchForm = reactive({
  keyword: '',
  caseType: '',
  diseaseType: '',
  difficulty: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 9, // 9个正好排满3行 (3x3)
  total: 0
})

const getDifficultyType = (difficulty) => {
  const map = { '入门': 'success', '进阶': 'warning', '高级': 'danger' }
  return map[difficulty] || 'info'
}

// 侧边栏点击切换分类
const toggleDisease = (type) => {
  searchForm.diseaseType = type
  handleSearch()
}

const toggleCaseType = (type) => {
  searchForm.caseType = type
  handleSearch()
}

// 加载案例列表
const loadCaseList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      keyword: searchForm.keyword,
      case_type: searchForm.caseType,
      disease_type: searchForm.diseaseType,
      difficulty: searchForm.difficulty
    }
    const res = await getTeachingCases(params)
    
    // 模拟一下 findings 数据，为了展示悬浮效果（如果后端没返回的话）
    const items = res.items || res || []
    caseList.value = items.map(item => ({
      ...item,
      // 随机给一些测试用的阳性发现，增强视觉效果，实际应对接后端字段
      findings: item.findings || (Math.random() > 0.5 ? ['可见不规则团块影', '边缘呈毛刺状', '局部血管穿行'] : null)
    }))
    
    pagination.total = res.total || caseList.value.length
  } catch (error) {
    console.error('加载案例列表失败', error)
    ElMessage.error('加载案例列表失败')
  } finally {
    loading.value = false
  }
}

// 触发搜索
const handleSearch = () => {
  pagination.page = 1
  loadCaseList()
}

const viewCaseDetail = (id) => {
  router.push(`/teaching/${id}`)
}

onMounted(() => {
  loadCaseList()
})
</script>

<style scoped>
.teaching-case-page {
  width: 100%;
}

.library-container {
  margin-top: 20px;
  align-items: stretch;
}

/* 左侧导航树样式 */
.sidebar-card {
  height: 100%;
  border-radius: 12px;
  background-color: var(--bg-card);
  min-height: calc(100vh - 180px);
}

.sidebar-section {
  padding: 10px 0;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.category-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.category-list li {
  padding: 12px 16px 12px 40px;
  font-size: 14px;
  color: var(--text-regular);
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  border-radius: 0 20px 20px 0;
  margin-right: 16px;
}

.category-list li:hover {
  background-color: var(--el-fill-color-light);
  color: var(--el-color-primary);
}

.category-list li.active {
  background-color: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
  font-weight: 600;
}

.category-list li.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background-color: var(--el-color-primary);
  border-radius: 0 4px 4px 0;
}

/* 右侧搜索区 */
.main-content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.resource-search-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--bg-card);
  padding: 16px 24px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
}

.search-input {
  width: 400px;
}

:deep(.search-input .el-input__wrapper) {
  border-radius: 20px;
  box-shadow: 0 0 0 1px var(--el-border-color) inset;
}

/* 卡片样式与核心悬浮动效 */
.case-card {
  background: var(--bg-card);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  cursor: pointer;
  margin-bottom: 24px;
  position: relative;
}

.case-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.12);
}

.case-cover {
  position: relative;
  height: 180px;
  background: linear-gradient(135deg, #165DFF 0%, #722ED1 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  overflow: hidden; /* 关键：隐藏滑出层 */
}

.cover-placeholder {
  color: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  transition: opacity 0.3s;
}

.cover-text {
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 2px;
}

.case-tags {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 2;
}

/* 悬浮展示的关键阳性发现层 */
.hover-overlay {
  position: absolute;
  bottom: -100%; /* 初始隐藏在下方 */
  left: 0;
  right: 0;
  height: 100%;
  background: rgba(22, 93, 255, 0.95);
  backdrop-filter: blur(4px);
  color: #fff;
  padding: 24px 20px;
  transition: bottom 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  z-index: 3;
}

/* 触发滑出效果 */
.case-card:hover .hover-overlay {
  bottom: 0;
}
.case-card:hover .cover-placeholder {
  opacity: 0; /* 悬浮时隐藏底图图标 */
}

.hover-overlay h5 {
  margin: 0 0 12px;
  font-size: 15px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  border-bottom: 1px solid rgba(255,255,255,0.3);
  padding-bottom: 8px;
}

.hover-overlay ul {
  margin: 0;
  padding-left: 18px;
  font-size: 13px;
  line-height: 1.8;
}

.default-finding {
  font-size: 13px;
  line-height: 1.6;
  opacity: 0.9;
}

/* 卡片文本内容区 */
.case-content {
  padding: 20px;
}

.case-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 10px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.case-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0 0 16px;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  height: 40px; /* 锁死高度对齐 */
}

.case-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.meta-right {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--text-secondary);
  align-items: center;
}

.meta-right span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.empty-list {
  padding: 80px 0;
  background: var(--bg-card);
  border-radius: 12px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 10px;
  padding: 20px;
  background: var(--bg-card);
  border-radius: 12px;
}
</style>