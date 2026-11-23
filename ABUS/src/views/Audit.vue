<template>
  <div class="page-container">
    <div class="page-header">
      <div class="header-left">
        <h3>{{ isFinance ? '财务审批' : '报销单审批' }}</h3>
        <span class="header-desc">待审批的报销单列表</span>
      </div>
      <div class="header-stats">
        <div class="stat-item">
          <span class="stat-num">{{ list.length }}</span>
          <span class="stat-label">待审批</span>
        </div>
      </div>
    </div>

    <div class="table-card">
      <el-table :data="list" stripe v-loading="loading" class="custom-table">
        <el-table-column prop="id" label="单号" width="90">
          <template #default="{ row }">
            <span class="record-id">#{{ row.id }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="applicant" label="申请人" width="110" />
        <el-table-column prop="input_date" label="申请日期" width="130" />
        <el-table-column prop="total_amount" label="金额" width="140">
          <template #default="{ row }">
            <span class="amount">¥{{ Number(row.total_amount).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="approver_name" label="审批经理" width="120" v-if="isFinance" />
        <el-table-column prop="status" label="经理审批" width="110">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small" effect="light">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="finance_status" label="财务状态" width="110" v-if="isFinance">
          <template #default="{ row }">
            <el-tag v-if="row.finance_status" :type="statusType(row.finance_status)" size="small" effect="light">{{ row.finance_status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="viewDetail(row.id)">
              <el-icon><View /></el-icon>
              详情
            </el-button>
            <el-button size="small" type="success" link @click="approve(row.id)">
              <el-icon><Check /></el-icon>
              通过
            </el-button>
            <el-button size="small" type="danger" link @click="openReject(row.id)">
              <el-icon><Close /></el-icon>
              退回
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 退回对话框 -->
    <el-dialog v-model="rejectVisible" title="退回原因" width="440px" class="reject-dialog">
      <div class="reject-content">
        <div class="reject-tip">
          <el-icon :size="20"><Warning /></el-icon>
          <span>请填写退回原因，以便申请人了解问题所在</span>
        </div>
        <el-input
          v-model="rejectReason"
          type="textarea"
          :rows="4"
          placeholder="请输入退回原因"
          maxlength="500"
          show-word-limit
        />
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="rejectVisible=false">取消</el-button>
          <el-button type="danger" :loading="submitting" @click="doReject">
            确认退回
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="报销单详情" width="800px" destroy-on-close class="detail-dialog">
      <div v-if="detailData" class="detail-content">
        <el-descriptions :column="3" border class="detail-desc">
          <el-descriptions-item label="单号">
            <span class="record-id">#{{ detailData.id }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="申请人">{{ detailData.applicant }}</el-descriptions-item>
          <el-descriptions-item label="申请日期">{{ detailData.input_date }}</el-descriptions-item>
          <el-descriptions-item label="审批经理">{{ detailData.approver_name }}</el-descriptions-item>
          <el-descriptions-item label="经理审批">
            <el-tag :type="statusType(detailData.status)" size="small" effect="light">{{ detailData.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="财务审批">
            <el-tag v-if="detailData.finance_status" :type="statusType(detailData.finance_status)" size="small" effect="light">{{ detailData.finance_status }}</el-tag>
            <span v-else class="text-muted">—</span>
          </el-descriptions-item>
          <el-descriptions-item label="总金额" :span="3">
            <span class="amount-large">¥{{ Number(detailData.total_amount).toFixed(2) }}</span>
          </el-descriptions-item>
        </el-descriptions>

        <div class="detail-items">
          <h4>
            <el-icon><List /></el-icon>
            费用明细
          </h4>
          <el-table :data="detailData.items" border size="small" class="items-table">
            <el-table-column prop="date" label="日期" width="110" />
            <el-table-column prop="category" label="类别" width="100" />
            <el-table-column prop="sub_cat" label="子类" width="90" />
            <el-table-column prop="reason" label="事由" />
            <el-table-column prop="department" label="部门" width="100" />
            <el-table-column prop="amount" label="金额" width="110">
              <template #default="{ row }">
                <span class="amount">¥{{ Number(row.amount).toFixed(2) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="attachments" label="附件" width="70" />
          </el-table>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { expenseApi } from '@/api/expense'
import { View, Check, Close, Warning, List } from '@element-plus/icons-vue'

const userStore = useUserStore()
const loading = ref(false)
const submitting = ref(false)
const list = ref<any[]>([])
const rejectVisible = ref(false)
const rejectReason = ref('')
const currentId = ref<number | null>(null)
const detailVisible = ref(false)
const detailData = ref<any>(null)

const isFinance = computed(() => userStore.role === '财务管理员')

function statusType(s: string | undefined): 'primary' | 'success' | 'warning' | 'danger' | 'info' {
  if (!s) return 'info'
  const m: Record<string, any> = { '待审': 'warning', '已批': 'success', '退回': 'danger' }
  return m[s] || 'info'
}

async function loadList() {
  loading.value = true
  try {
    let res: any
    if (isFinance.value) {
      res = await expenseApi.getFinanceAuditList()
    } else {
      res = await expenseApi.getAuditList(userStore.userId)
    }
    if (res.code === 0) list.value = res.data
  } finally {
    loading.value = false
  }
}

async function approve(id: number) {
  let res: any
  if (isFinance.value) {
    res = await expenseApi.financeApprove(id, userStore.userId)
  } else {
    res = await expenseApi.managerApprove(id, userStore.userId)
  }
  if (res.code === 0) {
    ElMessage.success('审批通过')
    loadList()
  }
}

function openReject(id: number) {
  currentId.value = id
  rejectReason.value = ''
  rejectVisible.value = true
}

async function doReject() {
  if (!rejectReason.value.trim()) {
    ElMessage.warning('请填写退回原因')
    return
  }
  submitting.value = true
  try {
    let res: any
    if (isFinance.value) {
      res = await expenseApi.financeReject(currentId.value!, rejectReason.value)
    } else {
      res = await expenseApi.managerReject(currentId.value!, rejectReason.value)
    }
    if (res.code === 0) {
      ElMessage.success('已退回')
      rejectVisible.value = false
      loadList()
    }
  } finally {
    submitting.value = false
  }
}

async function viewDetail(id: number) {
  const res = await expenseApi.getRecord(id)
  if (res.code === 0) {
    detailData.value = res.data
    detailVisible.value = true
  }
}

onMounted(loadList)
</script>

<style scoped>
.page-container {
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow-sm);
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
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

.header-stats {
  display: flex;
  gap: 24px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 24px;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: 12px;
}

.stat-num {
  font-size: 24px;
  font-weight: 700;
  color: #d97706;
}

.stat-label {
  font-size: 12px;
  color: #92400e;
}

.table-card {
  background: var(--bg-primary);
  border-radius: var(--radius-md);
  overflow: hidden;
}

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

.amount-large {
  font-weight: 700;
  font-size: 18px;
  color: #6b9080;
}

.text-muted {
  color: var(--text-tertiary);
}

/* 退回对话框 */
.reject-content {
  padding: 4px 0;
}

.reject-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #fef2f2;
  border-radius: 8px;
  color: #dc2626;
  font-size: 13px;
  margin-bottom: 16px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 详情对话框 */
.detail-content {
  padding: 0;
}

.detail-desc {
  margin-bottom: 24px;
}

.detail-items h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.detail-items h4 .el-icon {
  color: var(--primary-color);
}

.items-table {
  margin-top: 12px;
}
</style>
