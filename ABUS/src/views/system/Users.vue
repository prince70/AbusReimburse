<template>
  <div class="page-container">
    <div class="page-header">
      <div class="header-left">
        <h3>用户管理</h3>
        <span class="header-desc">管理系统用户账户和权限</span>
      </div>
      <el-button type="primary" @click="openCreate">
        <el-icon><Plus /></el-icon>
        新增用户
      </el-button>
    </div>

    <div class="table-card">
      <el-table :data="users" stripe v-loading="loading" class="custom-table">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="department" label="部门" width="120" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="roleType(row.role)" size="small" effect="light">{{ row.role }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="editUser(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button size="small" type="danger" link @click="deleteUser(row.id)" :disabled="row.id === userStore.userId">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 用户编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑用户' : '新增用户'" width="500px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" :disabled="!!editingId" />
        </el-form-item>
        <el-form-item v-if="!editingId" label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" placeholder="请选择角色" style="width:100%">
            <el-option label="员工" value="员工" />
            <el-option label="经理" value="经理" />
            <el-option label="财务管理员" value="财务管理员" />
            <el-option label="系统管理员" value="系统管理员" />
          </el-select>
        </el-form-item>
        <el-form-item label="部门">
          <el-select v-model="form.department" placeholder="请选择部门" style="width:100%" clearable allow-create filterable>
            <el-option v-for="d in departments" :key="d" :label="d" :value="d" />
          </el-select>
        </el-form-item>
        <el-form-item label="车间">
          <el-select v-model="form.workshop" placeholder="请选择车间" style="width:100%" clearable allow-create filterable>
            <el-option v-for="w in workshops" :key="w" :label="w" :value="w" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitForm">{{ editingId ? '保存' : '创建' }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { authApi } from '@/api/auth'
import { expenseApi } from '@/api/expense'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'

const userStore = useUserStore()
const loading = ref(false)
const submitting = ref(false)
const users = ref<any[]>([])
const departments = ref<string[]>([])
const workshops = ref<string[]>([])
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()

const form = reactive({
  name: '',
  username: '',
  password: '',
  role: '员工',
  department: '',
  workshop: ''
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

function roleType(role: string): 'primary' | 'success' | 'warning' | 'danger' | 'info' {
  const map: Record<string, any> = { '员工': 'primary', '经理': 'success', '财务管理员': 'warning', '系统管理员': 'danger' }
  return map[role] || 'info'
}

async function loadUsers() {
  loading.value = true
  try {
    const res = await authApi.getAllUsers()
    if (res.code === 0) users.value = res.data
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  Object.assign(form, { name: '', username: '', password: '', role: '员工', department: '', workshop: '' })
  dialogVisible.value = true
}

function editUser(row: any) {
  editingId.value = row.id
  Object.assign(form, {
    name: row.name,
    username: row.username,
    password: '',
    role: row.role,
    department: row.department || '',
    workshop: row.workshop || ''
  })
  dialogVisible.value = true
}

async function deleteUser(id: number) {
  await ElMessageBox.confirm('确认删除该用户？', '提示', { type: 'warning' })
  const res = await authApi.deleteUser(id)
  if (res.code === 0) {
    ElMessage.success('删除成功')
    loadUsers()
  }
}

async function submitForm() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const data: any = {
      name: form.name,
      username: form.username,
      role: form.role,
      department: form.department || undefined,
      workshop: form.workshop || undefined
    }
    if (!editingId.value) {
      data.password = form.password
    }
    const res = editingId.value 
      ? await authApi.updateUser(editingId.value, data)
      : await authApi.register(data)
    if (res.code === 0) {
      ElMessage.success(editingId.value ? '保存成功' : '创建成功')
      dialogVisible.value = false
      loadUsers()
    }
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  await loadUsers()
  const [deptRes, workshopRes] = await Promise.all([
    expenseApi.getDepartments(),
    expenseApi.getWorkshops()
  ])
  if (deptRes.code === 0) departments.value = deptRes.data
  if (workshopRes.code === 0) workshops.value = workshopRes.data
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
</style>