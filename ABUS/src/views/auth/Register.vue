<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-header">
        <img src="/logo.ico" alt="logo" class="auth-logo" />
        <h1>创建账户</h1>
        <p>填写信息以注册报销系统账户</p>
      </div>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="真实姓名" prop="name">
              <el-input v-model="form.name" placeholder="请输入真实姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="用户名" prop="username">
              <el-input v-model="form.username" placeholder="请输入用户名" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="密码" prop="password">
              <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="确认密码" prop="confirm">
              <el-input v-model="form.confirm" type="password" placeholder="请再次输入密码" show-password />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="所属经理" prop="supervisor_id">
          <el-select v-model="form.supervisor_id" placeholder="请选择所属经理" style="width:100%" clearable>
            <el-option v-for="s in supervisors" :key="s.id" :label="`${s.name}（${s.department || '无部门'}）`" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="部门">
              <el-select 
                v-model="form.department" 
                placeholder="请选择部门" 
                style="width:100%" 
                clearable 
                allow-create 
                filterable
                @visible-change="(val: boolean) => val && loadDepartments()"
              >
                <el-option v-for="d in departments" :key="d" :label="d" :value="d" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="车间">
              <el-select 
                v-model="form.workshop" 
                placeholder="请选择车间" 
                style="width:100%" 
                clearable 
                allow-create 
                filterable
                @visible-change="(val: boolean) => val && loadWorkshops()"
              >
                <el-option v-for="w in workshops" :key="w" :label="w" :value="w" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-button type="primary" size="large" :loading="loading" style="width:100%;margin-top:8px" @click="handleRegister">
          注册
        </el-button>
      </el-form>
      <div class="auth-footer">
        <span>已有账户？</span>
        <el-link type="primary" @click="router.push('/login')">立即登录</el-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onActivated } from 'vue'
import { useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { authApi } from '@/api/auth'
import { expenseApi } from '@/api/expense'

const router = useRouter()
const formRef = ref<FormInstance>()
const loading = ref(false)
const supervisors = ref<any[]>([])
const departments = ref<string[]>([])
const workshops = ref<string[]>([])

const form = reactive({
  name: '',
  username: '',
  password: '',
  confirm: '',
  department: '',
  workshop: '',
  supervisor_id: undefined as number | undefined
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    {
      validator: (_rule: any, value: string, callback: (e?: Error) => void) => {
        if (!value) return callback()
        authApi.checkUsername(value).then((res: any) => {
          if (res.exists) callback(new Error('用户名已被注册'))
          else callback()
        })
      },
      trigger: 'blur'
    }
  ],
  password: [{ required: true, min: 6, message: '密码至少6位', trigger: 'blur' }],
  confirm: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (_rule: any, value: string, callback: (e?: Error) => void) => {
        if (value !== form.password) callback(new Error('两次密码不一致'))
        else callback()
      },
      trigger: 'blur'
    }
  ]
}

onMounted(async () => {
  await loadData()
})

// 每次激活页面时强制刷新数据（解决快速切换不刷新的问题）
onActivated(async () => {
  await loadData()
})

// 每次进入页面时强制刷新数据
async function loadData() {
  const [supRes, deptRes, workshopRes] = await Promise.all([
    authApi.getSupervisors(),
    expenseApi.getDepartments(),
    expenseApi.getWorkshops()
  ])
  if (supRes.code === 0) supervisors.value = supRes.data
  if (deptRes.code === 0) departments.value = deptRes.data
  if (workshopRes.code === 0) workshops.value = workshopRes.data
}

// 下拉框打开时也刷新
async function loadDepartments() {
  const res = await expenseApi.getDepartments()
  if (res.code === 0) departments.value = res.data
}

async function loadWorkshops() {
  const res = await expenseApi.getWorkshops()
  if (res.code === 0) workshops.value = res.data
}

async function handleRegister() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    const res = await authApi.register({
      name: form.name,
      username: form.username,
      password: form.password,
      department: form.department || undefined,
      workshop: form.workshop || undefined,
      supervisor_id: form.supervisor_id
    })
    if (res.code === 0) {
      ElMessage.success('注册成功，请登录')
      router.push('/login')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  position: relative;
  overflow: hidden;
}

.auth-page::before {
  content: '';
  position: absolute;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(45, 140, 110, 0.1) 0%, transparent 70%);
  top: -200px;
  right: -200px;
}

.auth-page::after {
  content: '';
  position: absolute;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(45, 140, 110, 0.08) 0%, transparent 70%);
  bottom: -100px;
  left: -100px;
}

.auth-card {
  background: #fff;
  border-radius: 20px;
  padding: 40px 44px;
  width: 520px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.1);
  position: relative;
  z-index: 1;
}

.auth-header {
  text-align: center;
  margin-bottom: 32px;
}

.auth-logo {
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
}

.auth-header h1 {
  font-size: 22px;
  font-weight: 700;
  color: #212529;
  margin-bottom: 6px;
}

.auth-header p {
  font-size: 13px;
  color: #868e96;
}

.auth-footer {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: #6b7280;
}
</style>
