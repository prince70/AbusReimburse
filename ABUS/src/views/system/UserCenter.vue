<template>
  <div class="page-container">
    <div class="page-header">
      <h3>个人中心</h3>
      <span class="header-desc">管理您的个人信息和账户设置</span>
    </div>

    <el-row :gutter="24">
      <el-col :span="10">
        <div class="profile-card">
          <el-avatar :size="72" class="avatar">{{ userStore.userInfo?.name?.charAt(0) }}</el-avatar>
          <div class="profile-info">
            <h3>{{ userStore.userInfo?.name }}</h3>
            <p>{{ userStore.userInfo?.username }}</p>
            <el-tag :type="roleTagType" size="small">{{ userStore.role }}</el-tag>
          </div>
        </div>

        <div class="section-card">
          <div class="section-title">基本信息</div>
          <el-form ref="profileRef" :model="profileForm" label-width="80px">
            <el-form-item label="真实姓名" prop="name" :rules="[{required:true,message:'必填'}]">
              <el-input v-model="profileForm.name" />
            </el-form-item>
            <el-form-item label="部门">
              <el-select 
                v-model="profileForm.department" 
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
            <el-form-item label="车间">
              <el-select 
                v-model="profileForm.workshop" 
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
            <el-form-item label="所属经理">
              <el-select v-model="profileForm.supervisor_id" clearable style="width:100%">
                <el-option v-for="s in supervisors" :key="s.id" :label="`${s.name}（${s.department||''}）`" :value="s.id" />
              </el-select>
            </el-form-item>
            <el-button type="primary" :loading="savingProfile" @click="saveProfile">保存信息</el-button>
          </el-form>
        </div>
      </el-col>

      <el-col :span="14">
        <div class="section-card">
          <div class="section-title">修改密码</div>
          <el-form ref="pwdRef" :model="pwdForm" :rules="pwdRules" label-width="100px">
            <el-form-item label="原密码" prop="old_password">
              <el-input v-model="pwdForm.old_password" type="password" show-password />
            </el-form-item>
            <el-form-item label="新密码" prop="new_password">
              <el-input v-model="pwdForm.new_password" type="password" show-password />
            </el-form-item>
            <el-form-item label="确认新密码" prop="confirm">
              <el-input v-model="pwdForm.confirm" type="password" show-password />
            </el-form-item>
            <el-button type="warning" :loading="savingPwd" @click="changePwd">修改密码</el-button>
          </el-form>
        </div>

        <div class="section-card">
          <div class="section-title">账户信息</div>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="用户名">{{ userStore.userInfo?.username }}</el-descriptions-item>
            <el-descriptions-item label="角色">{{ userStore.userInfo?.role }}</el-descriptions-item>
            <el-descriptions-item label="注册时间" :span="2">{{ userStore.userInfo?.created_at }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onActivated } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { authApi } from '@/api/auth'
import { expenseApi } from '@/api/expense'

const userStore = useUserStore()
const profileRef = ref<FormInstance>()
const pwdRef = ref<FormInstance>()
const savingProfile = ref(false)
const savingPwd = ref(false)
const supervisors = ref<any[]>([])
const departments = ref<string[]>([])
const workshops = ref<string[]>([])

const profileForm = reactive({
  name: userStore.userInfo?.name || '',
  department: userStore.userInfo?.department || '',
  workshop: userStore.userInfo?.workshop || '',
  supervisor_id: userStore.userInfo?.supervisor_id as number | undefined
})

const pwdForm = reactive({ old_password: '', new_password: '', confirm: '' })

const pwdRules: FormRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [{ required: true, min: 6, message: '密码至少6位', trigger: 'blur' }],
  confirm: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (_: any, val: string, cb: (e?: Error) => void) => {
        if (val !== pwdForm.new_password) cb(new Error('两次密码不一致'))
        else cb()
      },
      trigger: 'blur'
    }
  ]
}

const roleTagType = computed(() => {
  const m: Record<string, 'primary' | 'success' | 'warning' | 'danger' | 'info'> = {
    '员工': 'primary', '经理': 'success', '财务管理员': 'warning', '系统管理员': 'danger'
  }
  return m[userStore.role] || 'info'
})

async function saveProfile() {
  const valid = await profileRef.value?.validate().catch(() => false)
  if (!valid) return
  savingProfile.value = true
  try {
    const res = await authApi.updateProfile(userStore.userId, profileForm)
    if (res.code === 0) {
      ElMessage.success('保存成功')
      userStore.setUser({ ...userStore.userInfo!, ...profileForm })
    }
  } finally { savingProfile.value = false }
}

async function changePwd() {
  const valid = await pwdRef.value?.validate().catch(() => false)
  if (!valid) return
  savingPwd.value = true
  try {
    const res = await authApi.changePassword({
      user_id: userStore.userId,
      old_password: pwdForm.old_password,
      new_password: pwdForm.new_password
    })
    if (res.code === 0) {
      ElMessage.success('密码修改成功')
      pwdForm.old_password = ''
      pwdForm.new_password = ''
      pwdForm.confirm = ''
    }
  } finally { savingPwd.value = false }
}

onMounted(async () => {
  await loadData()
})

// 每次激活页面时强制刷新数据（解决快速切换不刷新的问题）
onActivated(async () => {
  await loadData()
})

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

async function loadDepartments() {
  const res = await expenseApi.getDepartments()
  if (res.code === 0) departments.value = res.data
}

async function loadWorkshops() {
  const res = await expenseApi.getWorkshops()
  if (res.code === 0) workshops.value = res.data
}
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

.page-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.header-desc {
  font-size: 13px;
  color: var(--text-tertiary);
}

.profile-card {
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  padding: 28px 20px;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.avatar {
  background: linear-gradient(135deg, #6b9080 0%, #8fb3a4 100%);
  font-weight: 600;
}

.profile-info {
  text-align: center;
}

.profile-info h3 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.profile-info p {
  font-size: 13px;
  color: var(--text-tertiary);
  margin-bottom: 8px;
}

.section-card {
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  padding: 24px 20px;
  box-shadow: var(--shadow-sm);
  margin-bottom: 20px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-light);
}
</style>
