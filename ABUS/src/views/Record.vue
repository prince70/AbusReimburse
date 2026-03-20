<template>
  <div class="page-container">
    <div class="page-header">
      <div class="header-left">
        <h3>报销申请录入</h3>
        <span class="header-desc">创建和管理您的报销申请</span>
      </div>
      <el-button type="primary" @click="openCreate">
        <el-icon><Plus /></el-icon>
        新建报销单
      </el-button>
    </div>

    <div class="table-card">
      <el-table :data="records" stripe v-loading="loading" class="custom-table">
        <el-table-column prop="id" label="单号" width="90">
          <template #default="{ row }">
            <span class="record-id">#{{ row.id }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="input_date" label="申请日期" width="130" />
        <el-table-column prop="total_amount" label="金额" width="140">
          <template #default="{ row }">
            <span class="amount">¥{{ Number(row.total_amount).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="approver_name" label="审批经理" width="120" />
        <el-table-column prop="status" label="经理审批" width="110">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small" effect="light">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="finance_status" label="财务审批" width="110">
          <template #default="{ row }">
            <el-tag v-if="row.finance_status" :type="statusType(row.finance_status)" size="small" effect="light">{{ row.finance_status }}</el-tag>
            <span v-else class="text-muted">—</span>
          </template>
        </el-table-column>
        <el-table-column prop="reject_reason" label="退回原因" show-overflow-tooltip min-width="150" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="viewDetail(row.id)">
              <el-icon><View /></el-icon>
              查看
            </el-button>
            <el-button size="small" type="warning" link @click="editRecord(row)" :disabled="row.status !== '待审'">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button size="small" type="danger" link @click="deleteRecord(row.id)" :disabled="row.status !== '待审'">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @current-change="loadRecords"
          @size-change="loadRecords"
        />
      </div>
    </div>

    <!-- 新建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingId ? '编辑报销单' : '新建报销单'"
      width="960px"
      destroy-on-close
      :close-on-click-modal="false"
      class="form-dialog"
    >
      <el-form ref="formRef" :model="form" label-position="top" class="expense-form">
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="申请日期" prop="input_date" :rules="[{required:true,message:'请选择申请日期'}]">
              <el-date-picker
                v-model="form.input_date"
                type="date"
                value-format="YYYY-MM-DD"
                placeholder="选择日期"
                style="width:100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="审批经理" prop="approver_id" :rules="[{required:true,message:'请选择审批经理'}]">
              <el-select v-model="form.approver_id" placeholder="请选择审批经理" style="width:100%" @change="onApproverChange">
                <el-option v-for="s in supervisors" :key="s.id" :label="s.name" :value="s.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <div class="items-section">
          <div class="items-header">
            <div class="items-title">
              <el-icon><List /></el-icon>
              <span>费用明细</span>
              <el-tag size="small" type="info">{{ form.items.length }} 条</el-tag>
            </div>
            <el-button size="small" type="primary" @click="addItem">
              <el-icon><Plus /></el-icon>
              添加明细
            </el-button>
          </div>

          <div class="items-table-header">
            <div class="th-col date">日期</div>
            <div class="th-col category">类别</div>
            <div class="th-col sub-cat">子类</div>
            <div class="th-col reason">事由</div>
            <div class="th-col dept">部门</div>
            <div class="th-col amount">金额</div>
            <div class="th-col attach">附件</div>
            <div class="th-col action"></div>
          </div>

          <transition-group name="item-list" tag="div" class="items-body">
            <div v-for="(item, idx) in form.items" :key="idx" class="item-row">
              <div class="td-col date">
                <el-date-picker v-model="item.date" type="date" value-format="YYYY-MM-DD" placeholder="日期" size="small" style="width:100%" />
              </div>
              <div class="td-col category">
                <el-select v-model="item.category" placeholder="类别" size="small" style="width:100%" @change="() => (item.sub_cat='')">
                  <el-option v-for="c in categories" :key="c.name" :label="c.name" :value="c.name" />
                </el-select>
              </div>
              <div class="td-col sub-cat">
                <el-select v-model="item.sub_cat" placeholder="子类" size="small" style="width:100%" clearable>
                  <el-option v-for="s in getSubCats(item.category)" :key="s" :label="s" :value="s" />
                </el-select>
              </div>
              <div class="td-col reason">
                <el-input v-model="item.reason" placeholder="请输入事由" size="small" />
              </div>
              <div class="td-col dept">
                <el-select v-model="item.department" placeholder="部门" size="small" style="width:100%">
                  <el-option v-for="d in departments" :key="d" :label="d" :value="d" />
                </el-select>
              </div>
              <div class="td-col amount">
                <el-input-number v-model="item.amount" :min="0" :precision="2" size="small" style="width:100%" @change="calcTotal" />
              </div>
              <div class="td-col attach">
                <el-input-number v-model="item.attachments" :min="0" :max="99" size="small" style="width:70px" />
              </div>
              <div class="td-col action">
                <el-button size="small" type="danger" text @click="removeItem(idx)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
          </transition-group>

          <div class="total-row">
            <div class="total-info">
              <span>共 <strong>{{ form.items.length }}</strong> 条明细</span>
            </div>
            <div class="total-amount">
              合计金额：<span class="amount">¥{{ form.total_amount.toFixed(2) }}</span>
            </div>
          </div>
        </div>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible=false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="submitForm">
            {{ editingId ? '保存修改' : '提交申请' }}
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
          <el-descriptions-item v-if="detailData.reject_reason" label="退回原因" :span="3">
            <span class="reject-reason">{{ detailData.reject_reason }}</span>
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
import { ref, reactive, onMounted } from 'vue'
import type { FormInstance } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { expenseApi } from '@/api/expense'
import { authApi } from '@/api/auth'
import dayjs from 'dayjs'
import { Plus, View, Edit, Delete, List } from '@element-plus/icons-vue'

const userStore = useUserStore()
const loading = ref(false)
const submitting = ref(false)
const records = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const supervisors = ref<any[]>([])
const departments = ref<string[]>([])
const categories = ref<any[]>([])
const dialogVisible = ref(false)
const detailVisible = ref(false)
const detailData = ref<any>(null)
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()

const form = reactive({
  input_date: dayjs().format('YYYY-MM-DD'),
  approver_id: undefined as number | undefined,
  approver_name: '',
  total_amount: 0,
  items: [] as any[]
})

function statusType(status: string): 'primary' | 'success' | 'warning' | 'danger' | 'info' {
  const map: Record<string, any> = { '待审': 'warning', '已批': 'success', '退回': 'danger' }
  return map[status] || 'info'
}

function getSubCats(category: string): string[] {
  const c = categories.value.find((x: any) => x.name === category)
  return c ? c.sub : []
}

function onApproverChange(id: number) {
  const s = supervisors.value.find((x: any) => x.id === id)
  form.approver_name = s ? s.name : ''
}

function addItem() {
  form.items.push({
    date: dayjs().format('YYYY-MM-DD'),
    category: '',
    sub_cat: '',
    reason: '',
    department: userStore.userInfo?.department || '',
    workshop: userStore.userInfo?.workshop || '',
    licence: '',
    invoice: '',
    attachments: 0,
    amount: 0
  })
}

function removeItem(idx: number) {
  form.items.splice(idx, 1)
  calcTotal()
}

function calcTotal() {
  form.total_amount = form.items.reduce((s: number, i: any) => s + (Number(i.amount) || 0), 0)
}

async function loadRecords() {
  loading.value = true
  try {
    const res = await expenseApi.getRecords({
      user_id: userStore.userId,
      role: userStore.role,
      page: page.value,
      page_size: pageSize.value
    })
    if (res.code === 0) {
      records.value = res.data
      total.value = res.total
    }
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  Object.assign(form, {
    input_date: dayjs().format('YYYY-MM-DD'),
    approver_id: undefined,
    approver_name: '',
    total_amount: 0,
    items: []
  })
  addItem()
  dialogVisible.value = true
}

async function editRecord(row: any) {
  const res = await expenseApi.getRecord(row.id)
  if (res.code !== 0) return
  editingId.value = row.id
  Object.assign(form, {
    input_date: res.data.input_date,
    approver_id: res.data.approver_id,
    approver_name: res.data.approver_name,
    total_amount: Number(res.data.total_amount),
    items: res.data.items.map((i: any) => ({ ...i, amount: Number(i.amount) }))
  })
  dialogVisible.value = true
}

async function viewDetail(id: number) {
  const res = await expenseApi.getRecord(id)
  if (res.code === 0) {
    detailData.value = res.data
    detailVisible.value = true
  }
}

async function deleteRecord(id: number) {
  await ElMessageBox.confirm('确认删除该报销单？', '提示', { type: 'warning' })
  const res = await expenseApi.deleteRecord(id)
  if (res.code === 0) {
    ElMessage.success('删除成功')
    loadRecords()
  }
}

async function submitForm() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  if (form.items.length === 0) {
    ElMessage.warning('请至少添加一条费用明细')
    return
  }
  calcTotal()
  submitting.value = true
  try {
    const payload = {
      user_id: userStore.userId,
      applicant: userStore.userInfo!.name,
      input_date: form.input_date,
      approver_id: form.approver_id!,
      approver_name: form.approver_name,
      total_amount: form.total_amount,
      items: form.items
    }
    const res = editingId.value
      ? await expenseApi.updateRecord(editingId.value, payload)
      : await expenseApi.createRecord(payload)
    if (res.code === 0) {
      ElMessage.success(editingId.value ? '更新成功' : '提交成功')
      dialogVisible.value = false
      loadRecords()
    }
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  const [supRes, deptRes, catRes] = await Promise.all([
    authApi.getSupervisors(),
    expenseApi.getDepartments(),
    expenseApi.getCategories()
  ])
  if (supRes.code === 0) supervisors.value = supRes.data
  if (deptRes.code === 0) departments.value = deptRes.data
  if (catRes.code === 0) categories.value = catRes.data
  loadRecords()
})
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

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  padding: 16px 0 0;
  border-top: 1px solid var(--border-light);
  margin-top: 16px;
}

/* 表单对话框 */
.form-dialog :deep(.el-dialog__body) {
  padding: 24px;
}

.expense-form :deep(.el-form-item__label) {
  font-weight: 500;
}

.items-section {
  margin-top: 24px;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.items-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-light);
}

.items-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: var(--text-primary);
}

.items-title .el-icon {
  color: var(--primary-color);
}

.items-table-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: var(--bg-tertiary);
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
}

.items-body {
  max-height: 300px;
  overflow-y: auto;
}

.item-row {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-light);
  transition: background-color var(--transition-fast);
}

.item-row:hover {
  background: var(--bg-secondary);
}

.item-row:last-child {
  border-bottom: none;
}

.th-col, .td-col {
  padding: 0 8px;
}

.th-col.date, .td-col.date { width: 110px; flex-shrink: 0; }
.th-col.category, .td-col.category { width: 100px; flex-shrink: 0; }
.th-col.sub-cat, .td-col.sub-cat { width: 90px; flex-shrink: 0; }
.th-col.reason, .td-col.reason { flex: 1; min-width: 120px; }
.th-col.dept, .td-col.dept { width: 100px; flex-shrink: 0; }
.th-col.amount, .td-col.amount { width: 100px; flex-shrink: 0; }
.th-col.attach, .td-col.attach { width: 80px; flex-shrink: 0; text-align: center; }
.th-col.action, .td-col.action { width: 50px; flex-shrink: 0; text-align: center; }

.total-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-light);
}

.total-info {
  font-size: 13px;
  color: var(--text-secondary);
}

.total-info strong {
  color: var(--text-primary);
}

.total-amount {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.total-amount .amount {
  font-size: 20px;
  margin-left: 8px;
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

.reject-reason {
  color: #ef4444;
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

/* 列表过渡动画 */
.item-list-enter-active,
.item-list-leave-active {
  transition: all 0.3s ease;
}

.item-list-enter-from,
.item-list-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}
</style>
