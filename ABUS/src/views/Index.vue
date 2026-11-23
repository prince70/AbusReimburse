<template>
  <div class="dashboard">
    <!-- 欢迎栏 -->
    <div class="welcome-banner">
      <div class="welcome-content">
        <div class="welcome-greeting">
          <h2>你好，{{ userStore.userInfo?.name }}</h2>
        </div>
        <p class="welcome-info">
          <el-tag size="small" effect="dark" class="role-tag">{{ userStore.role }}</el-tag>
          <span class="divider">·</span>
          <span>{{ userStore.userInfo?.department || '未设置部门' }}</span>
        </p>
      </div>
      <div class="welcome-date">
        <div class="date-main">{{ todayMain }}</div>
        <div class="date-sub">{{ todaySub }}</div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stat-row">
      <el-col :span="6" v-for="(card, index) in statCards" :key="card.label">
        <div 
          class="stat-card" 
          :style="{ '--card-accent': card.color }"
        >
          <div class="stat-icon-wrap" :style="{ background: card.bgColor }">
            <el-icon :size="20" :style="{ color: card.color }">
              <component :is="card.iconComponent" />
            </el-icon>
          </div>
          <div class="stat-body">
            <span class="stat-value">{{ card.value }}</span>
            <span class="stat-label">{{ card.label }}</span>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 内容区域 -->
    <el-row :gutter="20">
      <!-- 最近报销单 -->
      <el-col :span="24">
        <div class="section-card">
          <div class="section-header">
            <div class="section-title">
              <el-icon><Document /></el-icon>
              <span>最近报销记录</span>
            </div>
            <el-button type="primary" link @click="router.push('/view')">
              查看全部 <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
          <el-table 
            :data="recentRecords" 
            stripe 
            style="width:100%" 
            v-loading="loading"
            class="custom-table"
          >
            <el-table-column prop="id" label="单号" width="80">
              <template #default="{ row }">
                <span class="record-id">#{{ row.id }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="applicant" label="申请人" width="100" />
            <el-table-column prop="input_date" label="申请日期" width="120" />
            <el-table-column prop="total_amount" label="金额" width="130">
              <template #default="{ row }">
                <span class="amount">¥{{ Number(row.total_amount).toFixed(2) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="经理审批" width="100">
              <template #default="{ row }">
                <el-tag :type="statusType(row.status)" size="small" effect="light">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="finance_status" label="财务审批" width="100">
              <template #default="{ row }">
                <el-tag v-if="row.finance_status" :type="statusType(row.finance_status)" size="small" effect="light">{{ row.finance_status }}</el-tag>
                <span v-else class="text-gray">—</span>
              </template>
            </el-table-column>
            <el-table-column prop="approver_name" label="审批经理" min-width="100" />
          </el-table>
        </div>
      </el-col>
    </el-row>

    <!-- 快捷操作 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <div class="section-card quick-actions">
          <div class="section-header">
            <div class="section-title">
              <el-icon><Lightning /></el-icon>
              <span>快捷操作</span>
            </div>
          </div>
          <div class="action-list">
            <div class="action-item" @click="router.push('/record')" v-if="isEmployee">
              <div class="action-icon" style="background: linear-gradient(135deg, #6b9080 0%, #4a6b5c 100%);">
                <el-icon :size="20"><Plus /></el-icon>
              </div>
              <div class="action-content">
                <span class="action-title">新建报销单</span>
                <span class="action-desc">提交新的费用报销申请</span>
              </div>
              <el-icon class="action-arrow"><ArrowRight /></el-icon>
            </div>
            <div class="action-item" @click="router.push('/audit')" v-if="isManager || isFinance">
              <div class="action-icon" style="background: linear-gradient(135deg, #d4a84b 0%, #b8923f 100%);">
                <el-icon :size="20"><Checked /></el-icon>
              </div>
              <div class="action-content">
                <span class="action-title">审批待办</span>
                <span class="action-desc">处理待审批的报销单</span>
              </div>
              <el-icon class="action-arrow"><ArrowRight /></el-icon>
            </div>
            <div class="action-item" @click="router.push('/view')">
              <div class="action-icon" style="background: linear-gradient(135deg, #6b9080 0%, #4a6b5c 100%);">
                <el-icon :size="20"><Document /></el-icon>
              </div>
              <div class="action-content">
                <span class="action-title">报销记录</span>
                <span class="action-desc">查看已通过的报销记录</span>
              </div>
              <el-icon class="action-arrow"><ArrowRight /></el-icon>
            </div>
            <div class="action-item" @click="router.push('/report')">
              <div class="action-icon" style="background: linear-gradient(135deg, #8fb3a4 0%, #6b9080 100%);">
                <el-icon :size="20"><TrendCharts /></el-icon>
              </div>
              <div class="action-content">
                <span class="action-title">统计报表</span>
                <span class="action-desc">查看报销数据统计</span>
              </div>
              <el-icon class="action-arrow"><ArrowRight /></el-icon>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { expenseApi } from '@/api/expense'
import dayjs from 'dayjs'
import { 
  Document, Plus, Checked, TrendCharts, ArrowRight, Lightning,
  List, Clock, CircleCheck, Money
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const stats = ref<any>({})
const recentRecords = ref<any[]>([])

const isEmployee = computed(() => userStore.role === '员工')
const isManager = computed(() => userStore.role === '经理')
const isFinance = computed(() => userStore.role === '财务管理员')

const todayMain = computed(() => dayjs().format('YYYY年MM月DD日'))
const todaySub = computed(() => dayjs().format('dddd'))

const statCards = computed(() => [
  {
    label: '报销总数',
    value: stats.value.total ?? 0,
    iconComponent: List,
    color: '#6b9080',
    bgColor: 'rgba(107, 144, 128, 0.08)',
    trend: 12
  },
  { 
    label: '待审批', 
    value: stats.value.pending ?? 0, 
    iconComponent: Clock, 
    color: '#d4a84b',
    bgColor: 'rgba(212, 168, 75, 0.08)',
    trend: -5
  },
  { 
    label: '已批准',
    value: stats.value.approved ?? 0,
    iconComponent: CircleCheck,
    color: '#6b9080',
    bgColor: 'rgba(107, 144, 128, 0.08)',
    trend: 8
  },
  { 
    label: '总金额(¥)', 
    value: stats.value.total_amount ? Number(stats.value.total_amount).toFixed(0) : '0', 
    iconComponent: Money, 
    color: '#c75c5c',
    bgColor: 'rgba(199, 92, 92, 0.08)',
    trend: 15
  }
])

function statusType(status: string): 'primary' | 'success' | 'warning' | 'danger' | 'info' {
  const map: Record<string, 'primary' | 'success' | 'warning' | 'danger' | 'info'> = {
    '待审': 'warning', '已批': 'success', '退回': 'danger'
  }
  return map[status] || 'info'
}

onMounted(async () => {
  loading.value = true
  try {
    const [statsRes, recordsRes] = await Promise.all([
      expenseApi.getStatistics({ user_id: userStore.userId, role: userStore.role }),
      expenseApi.getRecords({ user_id: userStore.userId, role: userStore.role, page: 1, page_size: 8 })
    ])
    if (statsRes.code === 0) stats.value = statsRes.data
    if (recordsRes.code === 0) recentRecords.value = recordsRes.data
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

/* 欢迎栏 */
.welcome-banner {
  background: linear-gradient(135deg, #6b9080 0%, #4a6b5c 50%, #3d5a4d 100%);
  color: #fff;
  border-radius: 16px;
  padding: 28px 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(45, 140, 110, 0.2);
}

.welcome-banner::before {
  content: '';
  position: absolute;
  top: -30%;
  right: -5%;
  width: 250px;
  height: 250px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.15) 0%, transparent 70%);
  pointer-events: none;
}

.welcome-banner::after {
  content: '';
  position: absolute;
  bottom: -20%;
  right: 25%;
  width: 150px;
  height: 150px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  pointer-events: none;
}

.welcome-content {
  position: relative;
  z-index: 1;
}

.welcome-greeting {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.welcome-banner h2 {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.welcome-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  opacity: 0.9;
}

.welcome-info .divider {
  opacity: 0.5;
}

.role-tag {
  background: rgba(255, 255, 255, 0.2) !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  color: #fff !important;
}

.welcome-date {
  text-align: right;
  position: relative;
  z-index: 1;
}

.date-main {
  font-size: 16px;
  font-weight: 500;
  opacity: 0.9;
}

.date-sub {
  font-size: 13px;
  opacity: 0.7;
}

/* 统计卡片 */
.stat-row {
  margin-bottom: 4px;
}

.stat-card {
  background: var(--bg-primary);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
  position: relative;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--card-accent);
  border-radius: 12px 12px 0 0;
}

.stat-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-body {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 22px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.2;
}

.stat-label {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 2px;
}

/* 区块卡片 */
.section-card {
  background: var(--bg-primary);
  border-radius: 14px;
  padding: 24px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.section-title .el-icon {
  color: var(--primary-color);
}

/* 表格样式 */
.custom-table {
  --el-table-border-color: var(--border-light);
}

.record-id {
  font-weight: 600;
  color: var(--text-secondary);
}

.amount {
  font-weight: 600;
  color: #6b9080;
}

.text-gray {
  color: var(--text-tertiary);
}

/* 快捷操作 */
.quick-actions .action-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-item:hover {
  background: var(--bg-hover);
}

.action-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.action-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.action-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.action-desc {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 2px;
}

.action-arrow {
  color: var(--text-tertiary);
  transition: all 0.25s ease;
}

.action-item:hover .action-arrow {
  color: var(--primary-color);
  transform: translateX(4px);
}
</style>
