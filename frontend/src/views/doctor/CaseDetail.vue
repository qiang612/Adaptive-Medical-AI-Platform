<template>
  <div class="case-detail-page">
    <div class="page-nav">
      <el-button type="primary" link @click="goBack">
        <el-icon><ArrowLeft /></el-icon>
        返回案例库
      </el-button>
    </div>

    <el-row :gutter="20">
      <!-- 左侧主内容区 -->
      <el-col :span="18">
        <!-- 案例头部 -->
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
                  {{ caseDetail.author_name }}
                </span>
                <span><el-icon><View /></el-icon> {{ caseDetail.view_count }} 次学习</span>
                <span><el-icon><Star /></el-icon> {{ caseDetail.star_count }} 人收藏</span>
                <span>{{ caseDetail.created_at }}</span>
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

        <!-- 案例内容区 -->
        <el-card class="common-card mt-20">
          <el-tabs v-model="activeTab" type="border-card">
            <el-tab-pane label="病例介绍" name="intro">
              <div class="content-section">
                <h3 class="section-title">基本信息</h3>
                <el-descriptions :column="2" border class="info-table">
                  <el-descriptions-item label="患者性别">{{ caseDetail.gender || '女' }}</el-descriptions-item>
                  <el-descriptions-item label="患者年龄">{{ caseDetail.age || '45岁' }}</el-descriptions-item>
                  <el-descriptions-item label="主诉" :span="2">{{ caseDetail.chief_complaint || '体检发现宫颈异常' }}</el-descriptions-item>
                  <el-descriptions-item label="现病史" :span="2">{{ caseDetail.history_of_present_illness || '患者于1周前常规体检，宫颈细胞学检查提示ASC-US，无明显阴道流血、排液等症状。' }}</el-descriptions-item>
                  <el-descriptions-item label="既往史" :span="2">{{ caseDetail.past_history || '既往体健，否认高血压、糖尿病、心脏病史。' }}</el-descriptions-item>
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
                      <p>患者为中年女性，常规体检发现宫颈细胞学异常，无明显临床症状。</p>
                      <p>需要重点关注：年龄、性生活史、孕产史、家族史、既往宫颈检查史。</p>
                    </template>
                  </el-step>
                  <el-step title="第二步：检查结果解读">
                    <template #description>
                      <p>宫颈细胞学：ASC-US（意义不明确的非典型鳞状细胞）</p>
                      <p>HPV检测：高危型HPV16、18型阳性，病毒载量较高。</p>
                      <p>阴道镜检查：宫颈转化区可见醋白上皮，碘试验阴性，取活检送病理。</p>
                      <p>病理结果：宫颈高级别鳞状上皮内病变（HSIL/CIN II-III级）。</p>
                    </template>
                  </el-step>
                  <el-step title="第三步：诊断与鉴别诊断">
                    <template #description>
                      <p>明确诊断：宫颈高级别鳞状上皮内病变（HSIL），高危型HPV持续感染。</p>
                      <p>鉴别诊断：
                        <ul>
                          <li>宫颈低级别鳞状上皮内病变（LSIL）</li>
                          <li>宫颈炎症</li>
                          <li>宫颈腺癌</li>
                        </ul>
                      </p>
                    </template>
                  </el-step>
                  <el-step title="第四步：治疗方案制定">
                    <template #description>
                      <p>患者为HSIL，属于癌前病变，有进展为宫颈癌的风险，无生育需求。</p>
                      <p>治疗方案：宫颈环形电切术（LEEP术），术后定期随访HPV及细胞学检查。</p>
                      <p>术后病理：切缘阴性，无浸润癌证据。</p>
                    </template>
                  </el-step>
                  <el-step title="第五步：随访与管理">
                    <template #description>
                      <p>术后6个月复查HPV阴性，细胞学正常。</p>
                      <p>长期随访计划：每年一次HPV联合细胞学筛查，持续20年。</p>
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
                      <span class="commenter-name">王教授</span>
                      <span class="commenter-title">北京协和医院 妇产科 主任医师</span>
                    </div>
                  </div>
                  <div class="comment-content">
                    <h4 class="comment-title">病例核心要点点评</h4>
                    <p>本病例是宫颈癌前病变早期筛查与规范处理的典型案例，具有重要的教学价值：</p>
                    <ol>
                      <li>
                        <strong>筛查策略的规范性</strong>：采用宫颈细胞学联合HPV检测的联合筛查方案，是目前国内外指南推荐的宫颈癌筛查金标准。本病例通过联合筛查发现了细胞学异常，进一步通过HPV分型检测明确了高危型别，为后续诊疗提供了关键依据。
                      </li>
                      <li>
                        <strong>诊断流程的严谨性</strong>：从筛查异常到阴道镜检查、病理活检，严格遵循了宫颈癌前病变的三阶梯诊断流程。病理结果是诊断的金标准，本病例通过活检明确了HSIL的诊断，避免了过度治疗或治疗不足。
                      </li>
                      <li>
                        <strong>治疗方案的个体化</strong>：结合患者的年龄、病变级别、生育需求等因素，选择了LEEP术作为治疗方案，既完整切除了病变组织，又最大程度保留了宫颈的解剖结构，符合临床诊疗规范。
                      </li>
                      <li>
                        <strong>术后随访的重要性</strong>：HSIL患者术后仍有复发风险，长期规范的随访是预防宫颈癌发生的关键。本病例制定了完善的随访计划，体现了全周期管理的理念。
                      </li>
                    </ol>
                    <h4 class="comment-title">临床警示</h4>
                    <p>宫颈癌是唯一可以通过早期筛查和预防实现治愈的恶性肿瘤，高危型HPV持续感染是宫颈癌发生的必要条件。对于30岁以上女性，推荐每3-5年进行一次HPV联合细胞学筛查，早发现、早诊断、早治疗是降低宫颈癌发病率和死亡率的关键。</p>
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

        <!-- 讨论区 -->
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

      <!-- 右侧侧边栏 -->
      <el-col :span="6">
        <!-- 学习进度 -->
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

        <!-- 病例核心信息 -->
        <el-card class="common-card mb-20">
          <template #header>
            <span class="card-title">病例核心信息</span>
          </template>
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="病种">{{ caseDetail.disease_type || '宫颈癌' }}</el-descriptions-item>
            <el-descriptions-item label="病例类型">{{ caseDetail.case_type || '典型病例' }}</el-descriptions-item>
            <el-descriptions-item label="难度">{{ caseDetail.difficulty || '入门' }}</el-descriptions-item>
            <el-descriptions-item label="患者年龄">{{ caseDetail.age || '45岁' }}</el-descriptions-item>
            <el-descriptions-item label="最终诊断">{{ caseDetail.final_diagnosis || '宫颈高级别鳞状上皮内病变' }}</el-descriptions-item>
            <el-descriptions-item label="治疗方案">{{ caseDetail.treatment || 'LEEP术' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 相关案例推荐 -->
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

        <!-- 学习工具 -->
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
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'

const router = useRouter()
const route = useRoute()
const caseId = computed(() => route.params.id)

const activeTab = ref('intro')
const isStared = ref(false)
const commentInput = ref('')
const learnProgress = ref(0)

// 案例详情
const caseDetail = ref({})

// 检查数据
const examData = ref([
  { item: '宫颈细胞学', result: 'ASC-US', reference: '未见上皮内病变或恶性病变' },
  { item: 'HPV检测', result: '16型阳性、18型阳性', reference: '阴性' },
  { item: '血常规', result: 'WBC 6.5×10^9/L，Hb 125g/L', reference: 'WBC 4-10×10^9/L，Hb 110-150g/L' },
  { item: '肝肾功能', result: '正常', reference: '正常范围' },
  { item: '凝血功能', result: '正常', reference: '正常范围' }
])

// 病例图片
const caseImages = ref([
  'https://images.unsplash.com/photo-1579403124614-197f69d8187b?w=800&q=80',
  'https://images.unsplash.com/photo-1558636508-e0db3814bd1d?w=800&q=80'
])
const imgLabels = ref([
  '宫颈阴道镜检查图像',
  '宫颈病理切片HE染色图像'
])

// 指南列表
const guideList = ref([
  {
    id: 1,
    name: '中国子宫颈癌筛查及早诊早治指南（2024年版）',
    type: '临床指南',
    publish_time: '2024-03-15',
    url: '#'
  },
  {
    id: 2,
    name: 'WHO宫颈癌前病变筛查与治疗指南',
    type: '国际指南',
    publish_time: '2023-05-20',
    url: '#'
  },
  {
    id: 3,
    name: 'ASCCP子宫颈癌筛查异常管理共识指南',
    type: '国际指南',
    publish_time: '2022-04-10',
    url: '#'
  }
])

// 课件列表
const courseList = ref([
  {
    name: '宫颈癌前病变的诊断与治疗',
    desc: '系统讲解宫颈癌前病变的三阶梯诊断流程与治疗方案选择'
  },
  {
    name: '阴道镜检查规范操作',
    desc: '阴道镜检查的操作要点、图像解读与活检技巧'
  },
  {
    name: 'HPV感染的临床管理',
    desc: 'HPV感染的自然史、风险分层与临床干预策略'
  }
])

// 评论列表
const commentList = ref([
  {
    id: 1,
    user_name: '李医生',
    avatar: '',
    content: '这个病例非常典型，对于基层医生学习宫颈癌筛查规范很有帮助，感谢分享！',
    created_at: '2025-12-16 10:25',
    like_count: 12
  },
  {
    id: 2,
    user_name: '张医生',
    avatar: '',
    content: '请问对于有生育需求的HSIL患者，治疗方案的选择有什么需要特别注意的地方吗？',
    created_at: '2025-12-17 08:40',
    like_count: 5
  },
  {
    id: 3,
    user_name: '王医生',
    avatar: '',
    content: '专家点评非常到位，把病例的核心要点和临床警示都讲清楚了，学习到了很多。',
    created_at: '2025-12-18 15:10',
    like_count: 8
  }
])

// 相关案例列表
const relatedCaseList = ref([
  {
    id: 5,
    title: '宫颈癌筛查假阴性病例分析',
    disease_type: '宫颈癌',
    view_count: 456
  },
  {
    id: 1,
    title: '宫颈癌早期筛查典型病例分析',
    disease_type: '宫颈癌',
    view_count: 1256
  },
  {
    id: 7,
    title: 'HPV持续感染病例管理',
    disease_type: '宫颈癌',
    view_count: 320
  }
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
  // 刷新页面数据
  caseId.value = id
  loadCaseDetail()
}

// 加载案例详情
const loadCaseDetail = async () => {
  // 模拟API调用
  await new Promise(resolve => setTimeout(resolve, 500))
  // 模拟数据
  caseDetail.value = {
    id: caseId.value,
    title: '宫颈癌早期筛查典型病例分析',
    case_type: '典型病例',
    disease_type: '宫颈癌',
    difficulty: '入门',
    description: '通过宫颈细胞学检查结合HPV检测，早期发现宫颈癌前病变的典型案例。',
    view_count: 1256,
    star_count: 89,
    author_name: '张医生',
    author_avatar: '',
    created_at: '2025-12-15',
    gender: '女',
    age: '45岁',
    chief_complaint: '体检发现宫颈异常',
    history_of_present_illness: '患者于1周前常规体检，宫颈细胞学检查提示ASC-US，无明显阴道流血、排液等症状。',
    past_history: '既往体健，否认高血压、糖尿病、心脏病史。',
    final_diagnosis: '宫颈高级别鳞状上皮内病变（HSIL/CIN II-III级）',
    treatment: '宫颈环形电切术（LEEP术）'
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