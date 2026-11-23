<template>
  <div class="page-container">
    <div class="page-header">
      <div class="header-left">
        <h3>报销统计报表</h3>
        <span class="header-desc">查看报销数据统计分析</span>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stat-row">
      <el-col :span="6" v-for="card in statCards" :key="card.label">
        <div class="stat-card" :style="{ '--card-accent': card.color }">
          <div class="stat-icon-wrap" :style="{ background: card.bgColor }">
            <el-icon :size="22" :style="{ color: card.color }">
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

    <!-- 图表区域 -->
    <el-row :gutter="20">
      <!-- 部门分布 -->
      <el-col :span="12">
        <div class="section-card">
          <div class="section-header">
            <div class="section-title">
              <el-icon><PieChart /></el-icon>
              <span>部门报销金额分布</span>
            </div>
          </div>
          <div class="chart-body">
            <div v-for="item in deptData" :key="item.department" class="progress-row">
              <span class="dept-name">{{ item.department }}</span>
              <div class="progress-wrapper">
                <el-progress 
                  :percentage="deptPercent(item.total)" 
                  :stroke-width="12"
                  :show-text="false"
                  :color="getDeptColor(item.department)"
                />
              </div>
              <span class="dept-amount">¥{{ Number(item.total).toFixed(0) }}</span>
            </div>
            <el-empty v-if="deptData.length === 0" description="暂无数据" :image-size="80" />
          </div>
        </div>
      </el-col>

      <!-- 月度趋势 -->
      <el-col :span="12">
        <div class="section-card">
          <div class="section-header">
            <div class="section-title">
              <el-icon><TrendCharts /></el-icon>
              <span>月度报销趋势</span>
            </div>
          </div>
          <div class="chart-body">
            <div v-for="item in monthlyData" :key="item.month" class="progress-row">
              <span class="dept-name">{{ item.month }}</span>
              <div class="progress-wrapper">
                <el-progress 
                  :percentage="monthPercent(item.total)" 
                  :stroke-width="12"
                  :show-text="false"
                  color="#6b9080"
                />
              </div>
              <span class="dept-amount">¥{{ Number(item.total).toFixed(0) }}</span>
            </div>
            <el-empty v-if="monthlyData.length === 0" description="暂无数据" :image-size="80" />
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 明细列表 -->
    <div class="section-card">
      <div class="section-header">
        <div class="section-title">
          <el-icon><List /></el-icon>
          <span>报销单明细列表</span>
        </div>
      </div>
      <el-table :data="records" stripe size="small" v-loading="loading" class="custom-table">
        <el-table-column prop="id" label="单号" width="80">
          <template #default="{ row }">
            <span class="record-id">#{{ row.id }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="applicant" label="申请人" width="100" />
        <el-table-column prop="input_date" label="日期" width="120" />
        <el-table-column prop="total_amount" label="金额" width="130">
          <template #default="{ row }">
            <span class="amount">¥{{ Number(row.total_amount).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="approver_name" label="经理" width="100" />
        <el-table-column prop="status" label="经理审批" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small" effect="light">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="finance_status" label="财务审批" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.finance_status" :type="statusType(row.finance_status)" size="small" effect="light">{{ row.finance_status }}</el-tag>
            <span v-else class="text-muted">—</span>
          </template>
        </el-table-column>
        <el-table-column prop="finance_name" label="财务" width="100" />
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { expenseApi } from '@/api/expense'
import { List, PieChart, TrendCharts, Document, Clock, CircleCheck, Money } from '@element-plus/icons-vue'

const userStore = useUserStore()
const loading = ref(false)
const stats = ref<any>({})
const deptData = ref<any[]>([])
const monthlyData = ref<any[]>([])
const records = ref<any[]>([])

const deptColors = ['#6b9080', '#8fb3a4', '#c9a86c', '#c17a7a', '#8a9aa8', '#4a6b5c']

const statCards = computed(() => [
  {
    label: '报销总数',
    value: stats.value.total ?? 0,
    iconComponent: Document,
    color: '#6b9080',
    bgColor: 'rgba(107, 144, 128, 0.08)'
  },
  { 
    label: '待审批', 
    value: stats.value.pending ?? 0, 
    iconComponent: Clock, 
    color: '#d4a84b',
    bgColor: 'rgba(212, 168, 75, 0.08)'
  },
  {
    label: '已批准',
    value: stats.value.approved ?? 0,
    iconComponent: CircleCheck,
    color: '#6b9080',
    bgColor: 'rgba(107, 144, 128, 0.08)'
  },
  { 
    label: '总金额(¥)', 
    value: stats.value.total_amount ? Number(stats.value.total_amount).toFixed(0) : '0', 
    iconComponent: Money, 
    color: '#c75c5c',
    bgColor: 'rgba(199, 92, 92, 0.08)'
  }
])

const maxDept = computed(() => Math.max(...deptData.value.map((d: any) => Number(d.total)), 1))
const maxMonth = computed(() => Math.max(...monthlyData.value.map((d: any) => Number(d.total)), 1))

function deptPercent(total: number) { return Math.round((Number(total) / maxDept.value) * 100) }
function monthPercent(total: number) { return Math.round((Number(total) / maxMonth.value) * 100) }

function getDeptColor(dept: string) {
  const idx = deptData.value.findIndex((d: any) => d.department === dept)
  return deptColors[idx % deptColors.length]
}

function statusType(s: string | undefined): 'primary' | 'success' | 'warning' | 'danger' | 'info' {
  if (!s) return 'info'
  const m: Record<string, any> = { '待审': 'warning', '已批': 'success', '退回': 'danger' }
  return m[s] || 'info'
}

onMounted(async () => {
  loading.value = true
  try {
    const [statRes, deptRes, monthRes, recRes] = await Promise.all([
      expenseApi.getStatistics({ user_id: userStore.userId, role: userStore.role }),
      expenseApi.getDepartmentReport(),
      expenseApi.getMonthlyReport(),
      expenseApi.getRecords({ user_id: userStore.userId, role: userStore.role, page: 1, page_size: 100 })
    ])
    if (statRes.code === 0) stats.value = statRes.data
    if (deptRes.code === 0) deptData.value = deptRes.data
    if (monthRes.code === 0) monthlyData.value = monthRes.data
    if (recRes.code === 0) records.value = recRes.data
  } finally { loading.value = false }
})
</script>

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  padding: 20px 24px;
  box-shadow: var(--shadow-sm);
}

.header-left h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.header-desc {
  font-size: 13px;
  color: var(--text-tertiary);
}

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
  width: 48px;
  height: 48px;
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
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
}

.stat-label {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 2px;
}

.section-card {
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
}

.section-header {
  margin-bottom: 20px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.section-title .el-icon {
  color: var(--primary-color);
}

.chart-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.progress-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.dept-name {
  width: 80px;
  font-size: 13px;
  color: var(--text-secondary);
  flex-shrink: 0;
  text-align: right;
}

.progress-wrapper {
  flex: 1;
}

.dept-amount {
  width: 80px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  text-align: right;
  flex-shrink: 0;
}

.custom-table {
  margin-top: 8px;
}

.record-id {
  font-weight: 600;
  color: var(--text-secondary);
}

.amount {
  font-weight: 600;
  color: #6b9080;
}

.text-muted {
  color: var(--text-tertiary);
}
</style>
