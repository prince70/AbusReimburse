<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-header">
        <div class="auth-logo">🔑</div>
        <h1>重置密码</h1>
        <p>通过用户名验证身份并重置密码</p>
      </div>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" size="large" />
        </el-form-item>
        <el-form-item label="新密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入新密码" size="large" show-password />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirm">
          <el-input v-model="form.confirm" type="password" placeholder="请再次输入新密码" size="large" show-password />
        </el-form-item>
        <el-button type="primary" size="large" :loading="loading" style="width:100%;margin-top:8px" @click="handleReset">
          重置密码
        </el-button>
      </el-form>
      <div class="auth-footer">
        <el-link type="primary" @click="router.push('/login')">返回登录</el-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import http from '@/api/http'

const router = useRouter()
const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({ username: '', password: '', confirm: '' })

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
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

async function handleReset() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    // 先查询用户是否存在
    const checkRes = await http.get<any, any>('/api/auth/check-username', {
      params: { username: form.username }
    })
    if (!checkRes.exists) {
      ElMessage.error('用户名不存在')
      return
    }
    // 通过管理员端点直接重置（实际项目需短信/邮件验证，此处简化）
    ElMessage.warning('请联系系统管理员重置密码，或使用旧密码登录后在个人中心修改')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.auth-card {
  background: #fff;
  border-radius: 16px;
  padding: 48px 40px;
  width: 420px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}

.auth-header { text-align: center; margin-bottom: 36px; }
.auth-logo { font-size: 48px; margin-bottom: 12px; }
.auth-header h1 { font-size: 24px; font-weight: 700; color: #1a1a2e; margin-bottom: 6px; }
.auth-header p { font-size: 12px; color: #909399; }
.auth-footer { text-align: center; margin-top: 20px; font-size: 14px; }
</style>
