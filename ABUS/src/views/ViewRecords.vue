<template>
  <div class="page-container">
    <div class="page-header">
      <h3>已核报销查看</h3>
      <div class="header-tools">
        <el-input v-model="search" placeholder="搜索申请人" clearable style="width:200px" />
        <el-select v-model="filterStatus" placeholder="筛选状态" clearable style="width:140px">
          <el-option label="全部" value="" />
          <el-option label="待审" value="待审" />
          <el-option label="已批" value="已批" />
          <el-option label="退回" value="退回" />
        </el-select>
      </div>
    </div>

    <el-table :data="filtered" stripe v-loading="loading" style="width:100%">
      <el-table-column prop="id" label="单号" width="80" />
      <el-table-column prop="applicant" label="申请人" width="100" />
      <el-table-column prop="input_date" label="申请日期" width="120" />
      <el-table-column prop="total_amount" label="金额" width="130">
        <template #default="scope">¥{{ Number(scope.row.total_amount || 0).toFixed(2) }}</template>
      </el-table-column>
      <el-table-column prop="approver_name" label="审批经理" width="110" />
      <el-table-column prop="status" label="经理审批" width="100">
        <template #default="scope">{{ scope.row.status || '—' }}</template>
      </el-table-column>
      <el-table-column prop="finance_status" label="财务审批" width="100">
        <template #default="scope">{{ scope.row.finance_status || '—' }}</template>
      </el-table-column>
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="scope">
          <el-button size="small" type="primary" @click="showDetail(scope.row)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination v-model:current-page="page" v-model:page-size="pageSize" :total="total"
      layout="total, prev, pager, next" style="margin-top:16px;justify-content:flex-end"
      @current-change="loadList" />
  </div>

  <el-drawer v-model="drawerVisible" title="报销单详情" size="600px">
    <div v-if="currentRow" class="detail-content">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="单号">{{ currentRow.id }}</el-descriptions-item>
        <el-descriptions-item label="申请人">{{ currentRow.applicant }}</el-descriptions-item>
        <el-descriptions-item label="申请日期">{{ currentRow.input_date }}</el-descriptions-item>
        <el-descriptions-item label="审批经理">{{ currentRow.approver_name }}</el-descriptions-item>
        <el-descriptions-item label="经理审批">
          <el-tag :type="getStatusType(currentRow.status)">{{ currentRow.status || '—' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="财务审批">
          <el-tag v-if="currentRow.finance_status" :type="getStatusType(currentRow.finance_status)">{{ currentRow.finance_status }}</el-tag>
          <span v-else>—</span>
        </el-descriptions-item>
        <el-descriptions-item label="总金额" :span="2">
          <strong style="color:#f56c6c;font-size:18px">¥{{ Number(currentRow.total_amount || 0).toFixed(2) }}</strong>
        </el-descriptions-item>
      </el-descriptions>

      <h4 style="margin:20px 0 10px">费用明细</h4>
      <el-table :data="detailItems" border size="small" max-height="300">
        <el-table-column prop="date" label="日期" width="110" />
        <el-table-column prop="category" label="类别" width="100" />
        <el-table-column prop="sub_cat" label="子类" width="90" />
        <el-table-column prop="reason" label="事由" />
        <el-table-column prop="department" label="部门" width="100" />
        <el-table-column prop="amount" label="金额" width="100">
          <template #default="scope">¥{{ Number(scope.row.amount || 0).toFixed(2) }}</template>
        </el-table-column>
      </el-table>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { expenseApi } from '@/api/expense'

const userStore = useUserStore()
const loading = ref(false)
const records = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const search = ref('')
const filterStatus = ref('')
const drawerVisible = ref(false)
const currentRow = ref<any>(null)
const detailItems = ref<any[]>([])

const filtered = computed(() => {
  let list = records.value
  if (search.value) list = list.filter((r: any) => r.applicant?.includes(search.value))
  if (filterStatus.value) list = list.filter((r: any) => r.status === filterStatus.value)
  return list
})

function getStatusType(status: string | undefined): '' | 'success' | 'warning' | 'danger' {
  if (!status) return ''
  const map: Record<string, 'success' | 'warning' | 'danger'> = {
    '已批': 'success', '待审': 'warning', '退回': 'danger'
  }
  return map[status] || ''
}

async function loadList() {
  loading.value = true
  try {
    const res = await expenseApi.getRecords({ user_id: userStore.userId, role: userStore.role, page: page.value, page_size: pageSize.value })
    if (res.code === 0) { records.value = res.data; total.value = res.total }
  } finally { loading.value = false }
}

async function showDetail(row: any) {
  currentRow.value = row
  const res = await expenseApi.getRecord(row.id)
  if (res.code === 0) {
    detailItems.value = res.data.items || []
    drawerVisible.value = true
  }
}

onMounted(loadList)
</script>

<style scoped>
.page-container { background:#fff; border-radius:10px; padding:20px; box-shadow:0 2px 8px rgba(0,0,0,0.06); }
.page-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:16px; }
.page-header h3 { font-size:16px; font-weight:600; color:#1a1a2e; }
.header-tools { display:flex; gap:12px; }
.detail-content { padding: 0 10px; }
</style>