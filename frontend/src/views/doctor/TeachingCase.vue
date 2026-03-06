<template>
  <div class="teaching-case-page">
    <PageHeader
      title="教学案例库"
      description="浏览和学习典型病例，提升临床诊断思维能力"
    />

    <!-- 搜索筛选区 -->
    <SearchBar
      :show-keyword="true"
      keyword-placeholder="搜索案例标题、病种、关键词"
      @search="handleSearch"
      @reset="handleReset"
    >
      <el-form-item label="病例类型">
        <el-select v-model="searchForm.caseType" placeholder="全部" clearable style="width: 160px" @change="loadCaseList">
          <el-option label="典型病例" value="典型病例" />
          <el-option label="疑难病例" value="疑难病例" />
          <el-option label="误诊病例" value="误诊病例" />
          <el-option label="罕见病例" value="罕见病例" />
        </el-select>
      </el-form-item>
      <el-form-item label="病种">
        <el-select v-model="searchForm.diseaseType" placeholder="全部" clearable style="width: 160px" @change="loadCaseList">
          <el-option label="宫颈癌" value="宫颈癌" />
          <el-option label="肺结节" value="肺结节" />
          <el-option label="冠心病" value="冠心病" />
          <el-option label="糖尿病" value="糖尿病" />
          <el-option label="眼底病变" value="眼底病变" />
        </el-select>
      </el-form-item>
      <el-form-item label="难度">
        <el-select v-model="searchForm.difficulty" placeholder="全部" clearable style="width: 160px" @change="loadCaseList">
          <el-option label="入门" value="入门" />
          <el-option label="进阶" value="进阶" />
          <el-option label="高级" value="高级" />
        </el-select>
      </el-form-item>
    </SearchBar>

    <!-- 案例列表 -->
    <el-row :gutter="20">
      <el-col :span="8" v-for="item in caseList" :key="item.id">
        <div class="case-card" @click="viewCaseDetail(item.id)">
          <div class="case-cover">
            <div class="cover-placeholder">
              <el-icon :size="48"><Reading /></el-icon>
            </div>
            <div class="case-tags">
              <el-tag :type="getDifficultyType(item.difficulty)" size="small">{{ item.difficulty }}</el-tag>
              <el-tag type="info" size="small">{{ item.case_type }}</el-tag>
            </div>
          </div>
          <div class="case-content">
            <h3 class="case-title">{{ item.title }}</h3>
            <p class="case-desc">{{ item.description }}</p>
            <div class="case-meta">
              <span class="disease-tag">{{ item.disease_type }}</span>
              <div class="meta-right">
                <span><el-icon><View /></el-icon> {{ item.view_count }}</span>
                <span><el-icon><Star /></el-icon> {{ item.star_count }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <div v-if="caseList.length === 0" class="empty-list">
      <el-empty description="暂无案例" />
    </div>

    <Pagination
      v-if="caseList.length > 0"
      v-model:model-value="pagination.page"
      v-model:page-size="pagination.pageSize"
      :total="pagination.total"
      @change="loadCaseList"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import SearchBar from '@/components/SearchBar.vue'
import Pagination from '@/components/Pagination.vue'
import { getTeachingCases } from '@/api/teaching'

const router = useRouter()
const caseList = ref([])

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
  pageSize: 9,
  total: 0
})

// 获取难度标签类型
const getDifficultyType = (difficulty) => {
  const map = { '入门': 'success', '进阶': 'warning', '高级': 'danger' }
  return map[difficulty] || 'info'
}

// 加载案例列表
const loadCaseList = async () => {
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
    caseList.value = res.items || res || []
    pagination.total = res.total || caseList.value.length
  } catch (error) {
    console.error('加载案例列表失败', error)
    ElMessage.error('加载案例列表失败')
  }
}

// 搜索
const handleSearch = (params) => {
  Object.assign(searchForm, params)
  pagination.page = 1
  loadCaseList()
}

// 重置
const handleReset = () => {
  Object.keys(searchForm).forEach(key => {
    searchForm[key] = ''
  })
  pagination.page = 1
  loadCaseList()
}

// 查看案例详情
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

.case-card {
  background: var(--bg-card);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
  cursor: pointer;
  margin-bottom: 24px;
}

.case-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.case-cover {
  position: relative;
  height: 180px;
  background: linear-gradient(135deg, #165DFF 0%, #722ED1 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.cover-placeholder {
  color: rgba(255, 255, 255, 0.8);
}

.case-tags {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  gap: 8px;
}

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
}

.case-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.disease-tag {
  font-size: 13px;
  color: var(--primary-color);
  font-weight: 500;
}

.meta-right {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: var(--text-secondary);
  align-items: center;
}

.meta-right span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.empty-list {
  padding: 60px 0;
}
</style>