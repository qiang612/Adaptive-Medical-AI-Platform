<template>
  <div class="case-detail-page">
    <div class="page-nav">
      <el-button type="primary" link @click="goBack">
        <el-icon><ArrowLeft /></el-icon>
        返回案例库
      </el-button>
    </div>

    <el-row :gutter="20">
      <el-col :span="18">
        <el-card class="common-card detail-header-card">
          <div class="detail-header">
            <div class="header-left">
              <div class="case-tags">
                <el-tag :type="getDifficultyType(caseDetail.difficulty)" size="large">{{ caseDetail.difficulty }}</el-tag>
                <el-tag type="info" size="large">{{ caseDetail.case_type }}</el-tag>
                <el-tag type="primary" size="large">{{ caseDetail.disease_type }}</el-tag>
              </div>
              <h1 class="case-title">{{ caseDetail.title }}</h1>
              <p class="case-desc">{{ caseDetail.description }}</p>
              <div class="case-meta">
                <span class="author">
                  <el-avatar :size="28" :src="caseDetail.author_avatar" />
                  {{ caseDetail.author_name || '佚名医生' }}
                </span>
                <span><el-icon><View /></el-icon> {{ caseDetail.view_count || 0 }} 次学习</span>
                <span><el-icon><Star /></el-icon> {{ caseDetail.star_count || 0 }} 人收藏</span>
                <span>{{ caseDetail.created_at || caseDetail.create_time }}</span>
              </div>
            </div>
            <div class="header-right">
              <el-button :type="isStared ? 'warning' : 'default'" @click="toggleStar">
                <el-icon><Star /></el-icon>
                {{ isStared ? '已收藏' : '收藏' }}
              </el-button>
              <el-button type="primary">
                <el-icon><Share /></el-icon>
                分享
              </el-button>
            </div>
          </div>
        </el-card>

        <el-card class="common-card mt-20">
          <el-tabs v-model="activeTab" type="border-card">
            <el-tab-pane label="病例介绍" name="intro">
              <div class="content-section">
                <h3 class="section-title">基本信息</h3>
                <el-descriptions :column="2" border class="info-table">
                  <el-descriptions-item label="患者性别">{{ caseDetail.gender || '女' }}</el-descriptions-item>
                  <el-descriptions-item label="患者年龄">{{ caseDetail.age || '45岁' }}</el-descriptions-item>
                  <el-descriptions-item label="主诉" :span="2">{{ caseDetail.chief_complaint || '体检发现异常，要求进一步检查' }}</el-descriptions-item>
                  <el-descriptions-item label="现病史" :span="2">{{ caseDetail.history_of_present_illness || '患者近期常规体检提示异常，无明显临床症状，前来就诊。' }}</el-descriptions-item>
                  <el-descriptions-item label="既往史" :span="2">{{ caseDetail.past_history || '既往体健，否认高血压、糖尿病、心脏病等重大疾病史。' }}</el-descriptions-item>
                </el-descriptions>

                <h3 class="section-title">检查资料</h3>
                <el-table :data="examData" border class="common-table mb-20">
                  <el-table-column prop="item" label="检查项目" width="200" />
                  <el-table-column prop="result" label="检查结果" />
                  <el-table-column prop="reference" label="参考值" width="250" />
                </el-table>

                <h3 class="section-title">影像资料</h3>
                <div class="image-gallery">
                  <div v-for="(img, index) in caseImages" :key="index" class="image-item">
                    <el-image
                      :src="img"
                      :preview-src-list="caseImages"
                      :initial-index="index"
                      fit="cover"
                      style="width: 100%; height: 200px; border-radius: 8px"
                    />
                    <span class="image-label">{{ imgLabels[index] }}</span>
                  </div>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="诊断思路" name="diagnosis">
              <div class="content-section">
                <el-steps direction="vertical" :current="3" finish-status="success">
                  <el-step title="第一步：病史分析">
                    <template #description>
                      <p>结合患者年龄及既往史，全面评估危险因素，关注核心主诉及偶发阳性体征。</p>
                      <p>需要重点关注：家族史、近期用药史及相关专科检查结果。</p>
                    </template>
                  </el-step>
                  <el-step title="第二步：检查结果解读">
                    <template #description>
                      <p>实验室检查：关注异常指标及其动态变化趋势。</p>
                      <p>影像学检查：识别关键阳性特征（如病灶形态、边缘、密度/信号改变等）。</p>
                      <p>病理/活检结果：作为最终确诊的“金标准”，结合免疫组化进一步分型。</p>
                    </template>
                  </el-step>
                  <el-step title="第三步：诊断与鉴别诊断">
                    <template #description>
                      <p>明确诊断：综合临床表现、影像特征与病理结果给出最终诊断。</p>
                      <p>鉴别诊断：需排除其他可能引起类似临床表现或影像学特征的良恶性疾病。</p>
                    </template>
                  </el-step>
                  <el-step title="第四步：治疗方案制定">
                    <template #description>
                      <p>基于患者的具体分期、年龄、基础疾病等因素，制定个体化综合治疗方案。</p>
                      <p>治疗方案：考虑手术、介入、放化疗或药物保守治疗等。</p>
                    </template>
                  </el-step>
                  <el-step title="第五步：随访与管理">
                    <template #description>
                      <p>评估近期疗效，监测不良反应。</p>
                      <p>长期随访计划：制定规律的复查时间表，关注复发或进展迹象。</p>
                    </template>
                  </el-step>
                </el-steps>
              </div>
            </el-tab-pane>

            <el-tab-pane label="专家点评" name="comment">
              <div class="content-section">
                <div class="comment-block">
                  <div class="comment-header">
                    <el-avatar :size="40" src="" />
                    <div class="commenter-info">
                      <span class="commenter-name">指导教授</span>
                      <span class="commenter-title">三甲医院 主任医师</span>
                    </div>
                  </div>
                  <div class="comment-content">
                    <h4 class="comment-title">病例核心要点点评</h4>
                    <p>本病例是临床工作中的典型代表，具有重要的教学与实战指导价值：</p>
                    <ol>
                      <li>
                        <strong>筛查与评估的规范性</strong>：早期发现和规范化的辅助检查是准确诊断的基础。本案例通过合理的检查组合快速锁定了病变区域。
                      </li>
                      <li>
                        <strong>影像与AI协同诊断</strong>：充分利用了医学影像特征，并结合AI辅助分析（如阳性病灶检出），有效降低了漏诊率。
                      </li>
                      <li>
                        <strong>诊疗思路的严谨性</strong>：从异常发现到确诊，严格遵循了临床标准路径。不仅给出了明确诊断，还进行了详尽的鉴别分析。
                      </li>
                      <li>
                        <strong>治疗的个体化与全周期管理</strong>：治疗方案切合患者实际情况，术后随访计划完善，体现了以患者为中心的现代医疗理念。
                      </li>
                    </ol>
                  </div>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="相关资料" name="materials">
              <div class="content-section">
                <h3 class="section-title">指南与文献</h3>
                <el-table :data="guideList" border class="common-table mb-20">
                  <el-table-column prop="name" label="资料名称" />
                  <el-table-column prop="type" label="类型" width="120" />
                  <el-table-column prop="publish_time" label="发布时间" width="150" />
                  <el-table-column label="操作" width="120">
                    <template #default="{ row }">
                      <el-button type="primary" link size="small" :href="row.url" target="_blank">查看下载</el-button>
                    </template>
                  </el-table-column>
                </el-table>

                <h3 class="section-title">相关课件</h3>
                <el-row :gutter="20">
                  <el-col :span="8" v-for="(course, index) in courseList" :key="index">
                    <div class="course-card">
                      <div class="course-cover">
                        <el-icon :size="40"><Reading /></el-icon>
                      </div>
                      <h4 class="course-title">{{ course.name }}</h4>
                      <p class="course-desc">{{ course.desc }}</p>
                      <el-button type="primary" size="small" style="width: 100%; margin-top: 10px">查看课件</el-button>
                    </div>
                  </el-col>
                </el-row>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>

        <el-card class="common-card mt-20">
          <template #header>
            <div class="card-header">
              <span class="card-title">病例讨论区</span>
              <span class="comment-count">{{ commentList.length }} 条讨论</span>
            </div>
          </template>

          <div class="comment-input-section">
            <el-input
              v-model="commentInput"
              type="textarea"
              :rows="3"
              placeholder="分享你的学习心得、诊断思路或疑问"
            />
            <div class="comment-submit">
              <el-button type="primary" @click="submitComment">发布评论</el-button>
            </div>
          </div>

          <el-divider />

          <div class="comment-list">
            <div v-for="comment in commentList" :key="comment.id" class="comment-item">
              <div class="comment-header">
                <el-avatar :size="36" :src="comment.avatar" />
                <div class="commenter-info">
                  <span class="commenter-name">{{ comment.user_name }}</span>
                  <span class="comment-time">{{ comment.created_at }}</span>
                </div>
              </div>
              <div class="comment-content">
                <p>{{ comment.content }}</p>
              </div>
              <div class="comment-footer">
                <el-button type="default" link size="small" @click="likeComment(comment.id)">
                  <el-icon><ThumbUp /></el-icon>
                  {{ comment.like_count }}
                </el-button>
                <el-button type="default" link size="small">
                  <el-icon><ChatDotRound /></el-icon>
                  回复
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="common-card mb-20">
          <template #header>
            <span class="card-title">学习进度</span>
          </template>
          <el-progress :percentage="learnProgress" :color="getProgressColor(learnProgress)" />
          <div class="progress-steps">
            <div class="progress-item" :class="{ completed: learnProgress >= 25 }">
              <el-icon><CircleCheck v-if="learnProgress >= 25" /><CircleClose v-else /></el-icon>
              <span>病例介绍</span>
            </div>
            <div class="progress-item" :class="{ completed: learnProgress >= 50 }">
              <el-icon><CircleCheck v-if="learnProgress >= 50" /><CircleClose v-else /></el-icon>
              <span>诊断思路</span>
            </div>
            <div class="progress-item" :class="{ completed: learnProgress >= 75 }">
              <el-icon><CircleCheck v-if="learnProgress >= 75" /><CircleClose v-else /></el-icon>
              <span>专家点评</span>
            </div>
            <div class="progress-item" :class="{ completed: learnProgress >= 100 }">
              <el-icon><CircleCheck v-if="learnProgress >= 100" /><CircleClose v-else /></el-icon>
              <span>相关资料</span>
            </div>
          </div>
        </el-card>

        <el-card class="common-card mb-20">
          <template #header>
            <span class="card-title">病例核心信息</span>
          </template>
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="病种">{{ caseDetail.disease_type || '未知分类' }}</el-descriptions-item>
            <el-descriptions-item label="病例类型">{{ caseDetail.case_type || '典型病例' }}</el-descriptions-item>
            <el-descriptions-item label="难度">{{ caseDetail.difficulty || '入门' }}</el-descriptions-item>
            <el-descriptions-item label="患者年龄">{{ caseDetail.age || '保密' }}</el-descriptions-item>
            <el-descriptions-item label="阳性发现">{{ (caseDetail.findings && caseDetail.findings[0]) || '影像学见异常病灶' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card class="common-card mb-20">
          <template #header>
            <span class="card-title">相关案例推荐</span>
          </template>
          <div class="related-case-list">
            <div
              v-for="item in relatedCaseList"
              :key="item.id"
              class="related-case-item"
              @click="goToCaseDetail(item.id)"
            >
              <h5 class="case-title">{{ item.title }}</h5>
              <div class="case-meta">
                <el-tag size="small" type="info">{{ item.disease_type }}</el-tag>
                <span class="view-count">{{ item.view_count }} 次学习</span>
              </div>
            </div>
          </div>
        </el-card>

        <el-card class="common-card">
          <template #header>
            <span class="card-title">学习工具</span>
          </template>
          <div class="tool-list">
            <el-button type="primary" style="width: 100%; margin-bottom: 10px">
              <el-icon><Download /></el-icon>
              下载病例PDF
            </el-button>
            <el-button type="default" style="width: 100%; margin-bottom: 10px">
              <el-icon><Printer /></el-icon>
              打印病例
            </el-button>
            <el-button type="default" style="width: 100%">
              <el-icon><Collection /></el-icon>
              加入学习收藏夹
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed } from 'vue' // 🔥 修复白屏报错：引入了 computed
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import { getTeachingCaseDetail } from '@/api/teaching' // 🔥 引入请求后端单条数据的 API

const router = useRouter()
const route = useRoute()
const caseId = computed(() => route.params.id)

const activeTab = ref('intro')
const isStared = ref(false)
const commentInput = ref('')
const learnProgress = ref(0)

// 案例详情
const caseDetail = ref({})

// 检查数据 (这里先留静态示例，如果有需要也可以随同案例详情一起存后端)
const examData = ref([
  { item: '常规生化全套', result: '多数指标正常', reference: '见具体化验单' },
  { item: '专科特异性抗体/标志物', result: '部分指标异常升高', reference: '阴性或正常范围' },
  { item: '血常规', result: 'WBC 6.5×10^9/L', reference: 'WBC 4-10×10^9/L' },
  { item: '肝肾功能', result: '正常', reference: '正常范围' },
  { item: '凝血功能', result: '正常', reference: '正常范围' }
])

// 病例图片
const caseImages = ref([
  'https://images.unsplash.com/photo-1579403124614-197f69d8187b?w=800&q=80',
  'https://images.unsplash.com/photo-1558636508-e0db3814bd1d?w=800&q=80'
])
const imgLabels = ref([
  '临床影像检查图像 (CT/MRI/阴道镜等)',
  '病理切片HE染色图像'
])

// 指南列表
const guideList = ref([
  { id: 1, name: '相关疾病诊疗指南（2024年版）', type: '临床指南', publish_time: '2024-03-15', url: '#' },
  { id: 2, name: '临床影像诊断与处理共识', type: '专家共识', publish_time: '2023-05-20', url: '#' }
])

// 课件列表
const courseList = ref([
  { name: '典型疾病影像特征诊断与鉴别', desc: '系统讲解疾病的多模态影像表现与实战鉴别技巧' },
  { name: '临床规范操作与前沿进展', desc: '深入探讨前沿技术与诊疗规范的结合点' }
])

// 评论列表
const commentList = ref([
  {
    id: 1,
    user_name: '李医生',
    avatar: '',
    content: '这个病例的阳性特征非常典型，对于提升阅片经验很有帮助，感谢分享！',
    created_at: '2025-12-16 10:25',
    like_count: 12
  },
  {
    id: 2,
    user_name: '张医生',
    avatar: '',
    content: '专家点评非常到位，把病例的核心要点和临床警示都讲清楚了，学习到了很多。',
    created_at: '2025-12-18 15:10',
    like_count: 8
  }
])

// 相关案例列表
const relatedCaseList = ref([
  { id: 1, title: '典型右上肺周围型肺癌伴胸膜牵拉', disease_type: '肺结节', view_count: 456 },
  { id: 2, title: '早期宫颈病变(CIN II)的阴道镜下表现', disease_type: '宫颈癌', view_count: 1256 },
  { id: 3, title: '复杂冠脉多支病变伴严重钙化', disease_type: '冠心病', view_count: 320 }
])

// 获取难度标签类型
const getDifficultyType = (difficulty) => {
  const map = { '入门': 'success', '进阶': 'warning', '高级': 'danger' }
  return map[difficulty] || 'info'
}

// 获取进度条颜色
const getProgressColor = (progress) => {
  if (progress >= 100) return '#00B42A'
  if (progress >= 75) return '#165DFF'
  if (progress >= 50) return '#FF7D00'
  return '#909399'
}

// 返回上一页
const goBack = () => {
  router.push('/teaching')
}

// 切换收藏
const toggleStar = () => {
  isStared.value = !isStared.value
  ElMessage.success(isStared.value ? '收藏成功' : '已取消收藏')
}

// 提交评论
const submitComment = () => {
  if (!commentInput.value.trim()) {
    ElMessage.warning('请输入评论内容')
    return
  }
  const newComment = {
    id: commentList.value.length + 1,
    user_name: '当前用户',
    avatar: '',
    content: commentInput.value,
    created_at: new Date().toLocaleString(),
    like_count: 0
  }
  commentList.value.unshift(newComment)
  commentInput.value = ''
  ElMessage.success('评论发布成功')
}

// 点赞评论
const likeComment = (id) => {
  const comment = commentList.value.find(item => item.id === id)
  if (comment) {
    comment.like_count += 1
    ElMessage.success('点赞成功')
  }
}

// 跳转到案例详情
const goToCaseDetail = (id) => {
  router.push(`/teaching/${id}`)
  // 刷新页面数据（vue-router同一组件参数变化不会触发onMounted，需手动调用）
  setTimeout(() => {
    loadCaseDetail()
  }, 100)
}

// 🔥 优化后的加载案例详情逻辑
const loadCaseDetail = async () => {
  try {
    // 优先尝试从后端获取真实数据
    const res = await getTeachingCaseDetail(caseId.value)
    
    // 如果获取成功且对象不为空
    if (res && res.id) {
      caseDetail.value = res
      return // 成功获取直接返回，不再执行下面的模拟数据
    }
  } catch (error) {
    console.warn('获取真实案例详情失败或接口尚未实现，将使用本地模拟数据兜底防止白屏。', error)
  }

  // 兜底方案：如果后端没有写 /cases/{id} 接口或者网络请求失败，使用默认数据填补页面
  caseDetail.value = {
    id: caseId.value,
    title: '案例详情请求失败或暂无对应数据',
    case_type: '未知类型',
    disease_type: '暂未分类',
    difficulty: '入门',
    description: '未能从数据库获取到该ID对应的具体教学案例数据，当前展示为系统模拟页面。',
    view_count: 0,
    star_count: 0,
    author_name: '系统测试员',
    author_avatar: '',
    created_at: new Date().toLocaleDateString(),
    gender: '未知',
    age: '未知',
    findings: ['未见明显异常'],
    chief_complaint: '无',
    history_of_present_illness: '无详细现病史记录。',
    past_history: '无',
    final_diagnosis: '等待明确诊断',
    treatment: '对症观察'
  }
}

// 监听tab切换，更新学习进度
watch(activeTab, (newTab) => {
  const progressMap = {
    intro: 25,
    diagnosis: 50,
    comment: 75,
    materials: 100
  }
  if (progressMap[newTab] > learnProgress.value) {
    learnProgress.value = progressMap[newTab]
  }
})

// 监听路由参数变化（解决右侧推荐点击后页面不刷新的问题）
watch(() => route.params.id, (newId, oldId) => {
  if (newId !== oldId && route.path.includes('/teaching/')) {
    activeTab.value = 'intro'
    learnProgress.value = 0
    loadCaseDetail()
  }
})

onMounted(() => {
  loadCaseDetail()
})
</script>

<style scoped>
.case-detail-page {
  width: 100%;
}

.page-nav {
  margin-bottom: 20px;
}

.detail-header-card {
  width: 100%;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
}

.header-left {
  flex: 1;
}

.case-tags {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.case-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 16px;
  line-height: 1.3;
}

.case-desc {
  font-size: 15px;
  color: var(--text-secondary);
  margin: 0 0 20px;
  line-height: 1.6;
}

.case-meta {
  display: flex;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
  font-size: 14px;
  color: var(--text-secondary);
}

.case-meta span {
  display: flex;
  align-items: center;
  gap: 6px;
}

.author {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  color: var(--text-primary);
}

.header-right {
  display: flex;
  gap: 12px;
}

.mt-20 {
  margin-top: 20px;
}

.mb-20 {
  margin-bottom: 20px;
}

.content-section {
  width: 100%;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px;
  padding-left: 12px;
  border-left: 4px solid var(--primary-color);
}

.image-gallery {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.image-item {
  width: calc(50% - 10px);
  text-align: center;
}

.image-label {
  display: block;
  margin-top: 10px;
  font-size: 14px;
  color: var(--text-regular);
  font-weight: 500;
}

.comment-block {
  width: 100%;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.commenter-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.commenter-name {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 16px;
}

.commenter-title {
  font-size: 13px;
  color: var(--text-secondary);
}

.comment-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 20px 0 12px;
}

.comment-content {
  line-height: 1.8;
  color: var(--text-regular);
}

.comment-content p,
.comment-content li {
  margin-bottom: 10px;
}

.course-card {
  padding: 20px;
  border: 1px solid var(--border-light);
  border-radius: 8px;
  text-align: center;
  transition: all 0.3s ease;
}

.course-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(22, 93, 255, 0.1);
}

.course-cover {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color) 0%, #4080FF 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
}

.course-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 6px;
}

.course-desc {
  font-size: 12px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}

.comment-input-section {
  margin-bottom: 20px;
}

.comment-submit {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
}

.comment-count {
  font-size: 14px;
  color: var(--text-secondary);
}

.comment-list {
  width: 100%;
}

.comment-item {
  padding: 16px 0;
  border-bottom: 1px solid var(--border-light);
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-item .comment-header {
  margin-bottom: 10px;
}

.comment-item .commenter-name {
  font-size: 14px;
}

.comment-time {
  font-size: 12px;
  color: var(--text-secondary);
  margin-left: 12px;
}

.comment-content {
  font-size: 14px;
  color: var(--text-regular);
  line-height: 1.6;
  margin-bottom: 10px;
}

.comment-footer {
  display: flex;
  gap: 16px;
}

.progress-steps {
  margin-top: 20px;
}

.progress-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  font-size: 14px;
  color: var(--text-secondary);
}

.progress-item.completed {
  color: var(--success-color);
}

.related-case-list {
  width: 100%;
}

.related-case-item {
  padding: 12px 0;
  border-bottom: 1px solid var(--border-light);
  cursor: pointer;
  transition: all 0.3s ease;
}

.related-case-item:last-child {
  border-bottom: none;
}

.related-case-item:hover {
  background: var(--bg-hover);
  padding-left: 8px;
}

.related-case-item .case-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin: 0 0 8px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.related-case-item .case-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: var(--text-secondary);
}

.view-count {
  font-size: 12px;
}

.tool-list {
  width: 100%;
}
</style>