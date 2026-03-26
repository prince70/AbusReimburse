<!-- 前端"查看" -->
<template>
  <div class="view-page">
    <ElCard shadow="never" class="header-card">
      <template #header>
        <div class="card-header">
          <h2>已核报销</h2>
        </div>
      </template>

      <div class="filter-container">
        <ElForm :inline="true" :model="filterForm" class="form-inline">
          <ElFormItem>
            <ElDatePicker v-model="filterForm.dateRange" type="daterange" range-separator="至" start-placeholder="开始日期"
              end-placeholder="结束日期" value-format="YYYY-MM-DD" unlink-panels />
          </ElFormItem>
          <ElFormItem>
            <ElSelect v-model="filterForm.status" placeholder="状态" clearable class="status-select">
              <ElOption label="待审批" value="待审" />
              <ElOption label="已通过" value="已批" />
              <ElOption label="已拒绝" value="退回" />
            </ElSelect>
          </ElFormItem>
          <ElFormItem>
            <ElButton type="primary" @click="handleSearch">查询</ElButton>
            <ElButton @click="resetFilter">重置</ElButton>
          </ElFormItem>
        </ElForm>
      </div>

      <!-- 报销单列表 -->
      <ElTable :data="tableData" border style="width: 100%" v-loading="loading">
        <ElTableColumn prop="id" label="单号" width="80" />
        <ElTableColumn prop="input_date" label="申请日期" width="120" />
        <ElTableColumn prop="applicant" label="申请人" width="120" />
        <ElTableColumn prop="total_amount" label="金额" width="120">
          <template #default="scope">
            <span>¥ {{ scope.row.total_amount?.toFixed(2) }}</span>
          </template>
        </ElTableColumn>
        <ElTableColumn prop="status" label="审核人审批" width="100">
          <template #default="scope">
            <ElTag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </ElTag>
          </template>
        </ElTableColumn>
        <ElTableColumn prop="finance_status" label="财务审批" width="100">
          <template #default="scope">
            <ElTag v-if="scope.row.finance_status" :type="getStatusType(scope.row.finance_status)">
              {{ getStatusText(scope.row.finance_status) }}
            </ElTag>
            <span v-else>-</span>
          </template>
        </ElTableColumn>
        <!-- 主管退回原因 -->
        <ElTableColumn prop="reject_reason" label="审核人退回原因" width="160">
          <template #default="scope">
            <span v-if="scope.row.reject_reason">{{ scope.row.reject_reason }}</span>
            <span v-else>-</span>
          </template>
        </ElTableColumn>
        <!-- 财务退回原因 -->
        <ElTableColumn prop="finance_reason" label="财务退回原因" width="160">
          <template #default="scope">
            <span v-if="scope.row.finance_reason">{{ scope.row.finance_reason }}</span>
            <span v-else>-</span>
          </template>
        </ElTableColumn>
        <ElTableColumn label="操作" width="230">
          <template #default="scope">
            <ElButton type="primary" @click="openDetail(scope.row)">查看详情</ElButton>
            <ElButton type="success" @click="previewPrint(scope.row)">
              打印预览
            </ElButton>
          </template>
        </ElTableColumn>
      </ElTable>

      <!-- 分页 -->
      <div class="pagination-container">
        <ElPagination v-model:current-page="pagination.current" v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next, jumper" :total="pagination.total"
          @size-change="handleSizeChange" @current-change="handleCurrentChange" />
      </div>
    </ElCard>

    <!-- 报销单详情对话框 -->
    <ElDialog v-model="detailDialogVisible" title="报销单详情" width="80%">
      <div v-if="currentReport">
        <template v-if="!showPreview">
          <ElDescriptions :column="3" border>
            <ElDescriptionsItem label="单号">{{ currentReport.id }}</ElDescriptionsItem>
            <ElDescriptionsItem label="申请人">{{ currentReport.applicant }}</ElDescriptionsItem>
            <ElDescriptionsItem label="申请日期">{{ currentReport.input_date }}</ElDescriptionsItem>
            <ElDescriptionsItem label="总金额">
              ¥ {{ currentReport.total_amount?.toFixed(2) }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="状态">
              <ElTag :type="getStatusType(currentReport.status)">
                {{ getStatusText(currentReport.status) }}
              </ElTag>
            </ElDescriptionsItem>
            <ElDescriptionsItem v-if="currentReport.reject_reason" label="主管拒绝原因">
              {{ currentReport.reject_reason }}
            </ElDescriptionsItem>
            <ElDescriptionsItem v-if="currentReport.finance_reason" label="财务拒绝原因">
              {{ currentReport.finance_reason }}
            </ElDescriptionsItem>
          </ElDescriptions>

          <h3 class="mt-20">报销明细</h3>
          <ElTable :data="currentReport.expense_items || []" border>
            <ElTableColumn prop="date" label="日期" width="120" />
            <ElTableColumn prop="category" label="费用类别" width="120" />
            <ElTableColumn prop="sub_cat" label="费用子类" width="120" />
            <ElTableColumn prop="reason" label="事由" />
            <ElTableColumn prop="department" label="部门" width="120" />
            <ElTableColumn prop="workshop" label="车间" width="120" />
            <ElTableColumn prop="invoice" label="发票号" width="120" />
            <ElTableColumn prop="attachments" label="附件数" width="80" />
            <ElTableColumn prop="amount" label="金额" width="120">
              <template #default="scope">
                <span>¥ {{ scope.row.amount?.toFixed(2) }}</span>
              </template>
            </ElTableColumn>
            <ElTableColumn label="备注" width="150">
              <template #default="scope">
                <span>{{ scope.row.licence ? scope.row.licence + (scope.row.remark ? ' - ' + scope.row.remark : '') :
                  (scope.row.remark || '') }}</span>
              </template>
            </ElTableColumn>
          </ElTable>
        </template>

        <template v-if="showPreview">
          <h3 class="mt-20">打印预览</h3>
          <iframe v-if="printHtml" :srcdoc="printHtml" style="width:100%;height:600px;border:none;"></iframe>
        </template>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <ElButton @click="detailDialogVisible = false">关闭</ElButton>
          <ElButton v-if="showPreview" type="primary" @click="printCurrentReport">打印</ElButton>
          <ElButton v-else type="primary" @click="previewPrint(currentReport!)">
            打印预览
          </ElButton>
        </span>
      </template>
    </ElDialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import dayjs from 'dayjs'
import logoPng from '@/assets/img/common/logo.png'
import { ref as vueRef } from 'vue'
const logoData = vueRef<string>('')

const toDataUrl = async (url: string): Promise<string> => {
  const res = await fetch(url)
  const blob = await res.blob()
  return new Promise<string>((resolve) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result as string)
    reader.readAsDataURL(blob)
  })
}
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/modules/user'
import {
  ExpenseReportModel,
  getExpenseReports,
  getFinanceApprovedReports,
  getExpenseReportDetail,
} from '@/api/expense'

// 数字转中文繁体金额
const convertToChineseAmount = (amount: number): string => {
  const digits = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
  const units = ['', '拾', '佰', '仟']
  const bigUnits = ['', '萬', '億']

  if (amount === 0) return '零元整'

  // 分离整数和小数部分
  const [integerPart, decimalPart] = amount.toFixed(2).split('.')
  let result = ''

  // 处理整数部分
  if (parseInt(integerPart) === 0) {
    result = '零'
  } else {
    const intStr = integerPart
    const len = intStr.length
    let zeroFlag = false

    for (let i = 0; i < len; i++) {
      const digit = parseInt(intStr[i])
      const pos = len - i - 1
      const unitPos = pos % 4
      const bigUnitPos = Math.floor(pos / 4)

      if (digit === 0) {
        zeroFlag = true
      } else {
        if (zeroFlag && result) {
          result += digits[0] // 添加零
        }
        result += digits[digit] + units[unitPos]
        zeroFlag = false
      }

      // 添加万、亿等大单位
      if (unitPos === 0 && bigUnitPos > 0 && digit !== 0) {
        result += bigUnits[bigUnitPos]
      }
    }
  }

  result += '元'

  // 处理小数部分
  const jiao = parseInt(decimalPart[0])
  const fen = parseInt(decimalPart[1])

  if (jiao === 0 && fen === 0) {
    result += '整'
  } else {
    if (jiao !== 0) {
      result += digits[jiao] + '角'
    } else if (fen !== 0) {
      result += '零'
    }
    if (fen !== 0) {
      result += digits[fen] + '分'
    }
  }

  return result
}

// 用户信息
const userStore = useUserStore()

// 加载状态
const loading = ref(false)

// 表格数据
const tableData = ref<ExpenseReportModel[]>([])

// 过滤表单
const filterForm = reactive({
  dateRange: [] as string[],
  status: '',
})

// 分页
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

// 当前查看的报销单
const currentReport = ref<ExpenseReportModel | null>(null)

// 对话框控制
const detailDialogVisible = ref(false)
const showPreview = ref(false)

// 双击行查看详情 -> replaced by button now but keep function
const openDetail = async (row: ExpenseReportModel) => {
  try {
    const res = await getExpenseReportDetail(row.id!)
    const detail: any = (res as any).data ?? res
    currentReport.value = detail
    showPreview.value = false
    detailDialogVisible.value = true
  } catch (e) {
    ElMessage.error('获取详情失败')
  }
}

// 生成打印HTML
const printHtml = computed(() => {
  if (!currentReport.value) return ''
  const rpt = currentReport.value
  const userInfo = userStore.info

  // 计算总附件数
  const totalAttachments = rpt.expense_items.reduce((sum, item) => sum + (item.attachments || 0), 0)

  const rowsHtml = rpt.expense_items
    .map((item, index) => {
      // 组合备注：车牌号 - 备注
      let remarkText = ''
      if (item.licence) {
        remarkText = item.licence
      }
      if (item.remark) {
        remarkText = remarkText ? `${remarkText} - ${item.remark}` : item.remark
      }

      // 序号从1开始，表示第几个子项
      const serialNumber = index + 1

      return `
        <tr>
          <td>${serialNumber}</td>
          <td>${item.category}</td>
          <td>${item.sub_cat ?? ''}</td>
          <td>${item.reason ?? ''}</td>
          <td>${item.department ?? ''}${item.workshop ? '/' + item.workshop : ''}</td>
          <td>${item.invoice ?? ''}</td>
          <td>${item.amount.toFixed(2)}</td>
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
          <h2 style="display: inline-block; margin: 0;">万晖五金（深圳）有限公司</h2>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
          <h2 style="margin: 0;">报销单</h2>
          <span style="font-size: 12pt;">流水号: ${String(rpt.id + 100).padStart(3, '0')}</span>
        </div>
        <div class="header-info" style="display: flex; justify-content: space-between; margin-bottom: 10px;">
          <span>申请人: ${rpt.applicant}</span>
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
            <td colspan="4" style="text-align: left; padding-left: 10px;">人民币: ${convertToChineseAmount(rpt.total_amount)}</td>
            <td colspan="2" style="white-space: nowrap;">¥ ${rpt.total_amount.toFixed(2)}</td>
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

// 打印当前报销单
const printCurrentReport = () => {
  if (!printHtml.value) return
  const newWin = window.open('', '_blank')
  if (newWin) {
    newWin.document.write(printHtml.value)
    newWin.document.close()
    newWin.focus()
    newWin.print()
  }
}

// 生成HTML辅助(供单行打印预览) - 已废弃，使用printHtml computed
const generatePrintHtml = (rpt: ExpenseReportModel) => {
  return ''
}

const previewPrint = async (row: ExpenseReportModel) => {
  // 移除审批状态检查，申请后即可打印预览

  try {
    const res = await getExpenseReportDetail(row.id!)
    const detail: any = (res as any).data ?? res
    currentReport.value = detail
    showPreview.value = true
    detailDialogVisible.value = true
  } catch (e) {
    ElMessage.error('生成预览失败')
  }
}

// 获取状态显示类型
const getStatusType = (status?: string) => {
  switch (status) {
    case '草稿':
      return 'info'
    case '待审':
      return 'warning'
    case '已批':
      return 'success'
    case '退回':
      return 'danger'
    default:
      return 'info'
  }
}

// 获取状态显示文本
const getStatusText = (status?: string) => {
  switch (status) {
    case '草稿':
      return '草稿'
    case '待审':
      return '待审批'
    case '已批':
      return '已通过'
    case '退回':
      return '已拒绝'
    default:
      return '未知'
  }
}

// 加载报销单列表
const loadData = async () => {
  loading.value = true
  try {
    let params: any = {
      skip: (pagination.current - 1) * pagination.pageSize,
      limit: pagination.pageSize
    }

    if (filterForm.status) {
      params.status = filterForm.status
    }

    if (filterForm.dateRange && filterForm.dateRange.length === 2) {
      params.start_date = filterForm.dateRange[0]
      params.end_date = filterForm.dateRange[1]
    }

    // 新增：传递用户ID和角色以实现权限控制
    params.user_id = userStore.info.id
    params.role = userStore.info.role

    // 只查finance_status不为null的报销单
    const response: any = await getFinanceApprovedReports(params)

    // 处理响应数据
    if (response && typeof response === 'object') {
      tableData.value = response.items || []
      pagination.total = response.total || 0
    } else {
      console.error('API返回格式异常:', response)
      ElMessage.error('数据格式错误')
    }
  } catch (error: any) {
    console.error('加载数据失败:', error)
    ElMessage.error(`加载失败: ${error.message || '未知错误'}`)
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.current = 1
  loadData()
}

// 重置过滤条件
const resetFilter = () => {
  filterForm.dateRange = []
  filterForm.status = ''
  handleSearch()
}

// 分页大小变化
const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  loadData()
}

// 页码变化
const handleCurrentChange = (val: number) => {
  pagination.current = val
  loadData()
}

// 页面加载时初始化
onMounted(() => {
  loadData()
})

onMounted(async () => {
  if (!logoData.value) {
    try {
      logoData.value = await toDataUrl(logoPng)
    } catch (e) {
      console.error('加载logo失败', e)
    }
  }
})
</script>

<style lang="scss" scoped>
.view-page {
  padding: 20px;

  .header-card {
    margin-bottom: 20px;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .filter-container {
    margin-bottom: 20px;
  }

  .status-select {
    min-width: 140px;
  }

  .status-select :deep(.el-input__wrapper) {
    height: 36px;
    font-size: 14px;
  }

  .pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }

  .mt-20 {
    margin-top: 20px;
  }
}
</style>