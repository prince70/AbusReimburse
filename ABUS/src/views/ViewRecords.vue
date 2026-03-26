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

      <div class="detail-actions">
        <el-button type="primary" @click="openPrintPreview">打印预览</el-button>
      </div>
    </div>
  </el-drawer>

  <el-dialog v-model="printDialogVisible" title="打印预览" width="80%">
    <iframe v-if="printHtml" :srcdoc="printHtml" style="width:100%;height:600px;border:none;"></iframe>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="printDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="printCurrentReport">打印</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { expenseApi } from '@/api/expense'
import dayjs from 'dayjs'
import { ElMessage } from 'element-plus'

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
const printDialogVisible = ref(false)
const logoData = ref('')

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

async function toDataUrl(url: string): Promise<string> {
  const res = await fetch(url)
  const blob = await res.blob()
  return new Promise((resolve) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result as string)
    reader.readAsDataURL(blob)
  })
}

function convertToChineseAmount(amount: number): string {
  const digits = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
  const units = ['', '拾', '佰', '仟']
  const bigUnits = ['', '萬', '億']
  if (!amount) return '零元整'

  const [integerPart, decimalPart] = Number(amount).toFixed(2).split('.')
  let result = ''

  if (parseInt(integerPart, 10) === 0) {
    result = '零'
  } else {
    const len = integerPart.length
    let zeroFlag = false
    for (let i = 0; i < len; i++) {
      const digit = parseInt(integerPart[i], 10)
      const pos = len - i - 1
      const unitPos = pos % 4
      const bigUnitPos = Math.floor(pos / 4)
      if (digit === 0) {
        zeroFlag = true
      } else {
        if (zeroFlag && result) result += digits[0]
        result += digits[digit] + units[unitPos]
        zeroFlag = false
      }
      if (unitPos === 0 && bigUnitPos > 0 && digit !== 0) {
        result += bigUnits[bigUnitPos]
      }
    }
  }

  result += '元'
  const jiao = parseInt(decimalPart[0], 10)
  const fen = parseInt(decimalPart[1], 10)
  if (jiao === 0 && fen === 0) {
    result += '整'
  } else {
    if (jiao !== 0) result += digits[jiao] + '角'
    else if (fen !== 0) result += '零'
    if (fen !== 0) result += digits[fen] + '分'
  }
  return result
}

const printHtml = computed(() => {
  if (!currentRow.value) return ''
  const rpt = currentRow.value
  const items = detailItems.value || []
  const totalAttachments = items.reduce((sum: number, item: any) => sum + (item.attachments || 0), 0)

  const rowsHtml = items
    .map((item: any, index: number) => {
      let remarkText = ''
      if (item.licence) remarkText = item.licence
      if (item.remark) remarkText = remarkText ? `${remarkText} - ${item.remark}` : item.remark
      return `
        <tr>
          <td>${index + 1}</td>
          <td>${item.category ?? ''}</td>
          <td>${item.sub_cat ?? ''}</td>
          <td>${item.reason ?? ''}</td>
          <td>${item.department ?? ''}${item.workshop ? '/' + item.workshop : ''}</td>
          <td>${item.invoice ?? ''}</td>
          <td>${Number(item.amount || 0).toFixed(2)}</td>
          <td>${remarkText}</td>
        </tr>
      `
    })
    .join('')

  return `
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <style>
          body {
            font-family: "Helvetica Neue", Helvetica, Arial, "PingFang SC", sans-serif;
            padding: 20px;
          }
          h2 {
            text-align: center;
            margin-bottom: 20px;
            display: inline-block;
            margin-left: 10px;
            vertical-align: middle;
            font-size: 14pt;
            font-weight: bold;
          }
          table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
          }
          th,
          td {
            border: 1px solid #333;
            padding: 6px;
            text-align: center;
          }
          th {
            background: #f2f2f2;
            font-size: 10.5pt;
            font-weight: bold;
          }
          td {
            font-size: 10.5pt;
          }
          .header-info {
            font-size: 12pt;
            margin-bottom: 10px;
          }
          .signature-section {
            margin-top: 30px;
          }
        </style>
      </head>
      <body>
        <div style="text-align: center; margin-bottom: 10px;">
          <div style="display: inline-flex; align-items: center; gap: 8px;">
            ${logoData.value ? `<img src="${logoData.value}" alt="logo" style="width: 26px; height: 26px; object-fit: contain;" />` : ''}
            <h2 style="display: inline-block; margin: 0;">万晖五金（深圳）有限公司</h2>
          </div>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
          <h2 style="margin: 0;">报销单</h2>
          <span style="font-size: 12pt;">流水号: ${String((rpt.id || 0) + 100).padStart(3, '0')}</span>
        </div>
        <div class="header-info" style="display: flex; justify-content: space-between; margin-bottom: 10px;">
          <span>申请人: ${rpt.applicant ?? ''}</span>
          <span>申请日期: ${dayjs(rpt.input_date).format('YYYY-MM-DD')}</span>
          <span>附件: ${totalAttachments}</span>
          <span>单位: 元</span>
        </div>
        <table>
          <thead>
            <tr>
              <th>序号</th>
              <th>类别</th>
              <th>子类</th>
              <th>事由</th>
              <th>部门/车间</th>
              <th>发票号</th>
              <th>金额</th>
              <th>备注</th>
            </tr>
          </thead>
          <tbody>
            ${rowsHtml}
          </tbody>
          <tr>
            <td colspan="2">合计</td>
            <td colspan="4" style="text-align: left; padding-left: 10px;">人民币: ${convertToChineseAmount(Number(rpt.total_amount || 0))}</td>
            <td colspan="2" style="white-space: nowrap;">￥ ${Number(rpt.total_amount || 0).toFixed(2)}</td>
          </tr>
        </table>
        <div class="signature-section" style="display: flex; justify-content: space-around; margin-top: 40px;">
          <div style="text-align: center;">
            <div>申请人签字:</div>
          </div>
          <div style="text-align: center;">
            <div>审核人签字:</div>
          </div>
          <div style="text-align: center;">
            <div>出纳签字:</div>
          </div>
        </div>
      </body>
    </html>
  `
})

async function loadList() {
  loading.value = true
  try {
    const res = await expenseApi.getRecords({ user_id: userStore.userId, role: userStore.role, page: page.value, page_size: pageSize.value })
    if (res.code === 0) { records.value = res.data; total.value = res.total }
  } finally { loading.value = false }
}

async function showDetail(row: any) {
  try {
    const res = await expenseApi.getRecord(row.id)
    if (res.code === 0) {
      currentRow.value = res.data
      detailItems.value = res.data.items || []
      drawerVisible.value = true
    }
  } catch {
    ElMessage.error('获取详情失败')
  }
}

function openPrintPreview() {
  if (!currentRow.value) return
  printDialogVisible.value = true
}

function printCurrentReport() {
  if (!printHtml.value) return
  const newWin = window.open('', '_blank')
  if (!newWin) return
  newWin.document.write(printHtml.value)
  newWin.document.close()
  newWin.focus()
  newWin.print()
}

onMounted(loadList)
onMounted(async () => {
  if (!logoData.value) {
    try {
      logoData.value = await toDataUrl('/logo.ico')
    } catch {
      logoData.value = ''
    }
  }
})
</script>

<style scoped>
.page-container { background:#fff; border-radius:10px; padding:20px; box-shadow:0 2px 8px rgba(0,0,0,0.06); }
.page-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:16px; }
.page-header h3 { font-size:16px; font-weight:600; color:#1a1a2e; }
.header-tools { display:flex; gap:12px; }
.detail-content { padding: 0 10px; }
.detail-actions { margin-top: 12px; display: flex; justify-content: flex-end; }
</style>
