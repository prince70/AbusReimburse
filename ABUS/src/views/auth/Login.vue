<template>
  <div class="login-page">
    <div class="login-bg">
      <div class="bg-shape shape-1"></div>
      <div class="bg-shape shape-2"></div>
      <div class="bg-shape shape-3"></div>
    </div>
    <div class="login-container">
      <div class="login-card">
        <div class="login-header">
          <div class="login-logo">
            <img src="/logo.ico" alt="logo" />
          </div>
          <h1>ABUS报销管理系统</h1>
          <p>ABUS Hardware Reimbursement Platform</p>
        </div>
        <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent="handleLogin" class="login-form">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="form.username" placeholder="请输入用户名" size="large" prefix-icon="User" />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input v-model="form.password" type="password" placeholder="请输入密码" size="large" prefix-icon="Lock" show-password />
          </el-form-item>
          <el-button type="primary" native-type="submit" size="large" :loading="loading" class="login-btn">
            登录
          </el-button>
        </el-form>
        <div class="login-footer">
          <span>还没有账户？</span>
          <el-link type="primary" @click="router.push('/register')">立即注册</el-link>
          <span class="divider">|</span>
          <el-link @click="router.push('/forget-password')">忘记密码</el-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { authApi } from '@/api/auth'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({ username: '', password: '' })

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    const res = await authApi.login(form)
    if (res.code === 0) {
      userStore.setUser(res.data)
      ElMessage.success(`欢迎回来，${res.data.name}！`)
      router.push('/')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.login-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.bg-shape {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.4;
  animation: float 25s ease-in-out infinite;
}

.shape-1 {
  width: 500px;
  height: 500px;
  background: #6b9080;
  top: -150px;
  right: -150px;
  animation-delay: 0s;
}

.shape-2 {
  width: 400px;
  height: 400px;
  background: #8fb3a4;
  bottom: -100px;
  left: -100px;
  animation-delay: -8s;
}

.shape-3 {
  width: 300px;
  height: 300px;
  background: #4a6b5c;
  top: 40%;
  left: 30%;
  transform: translate(-50%, -50%);
  animation-delay: -16s;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -30px) scale(1.05); }
  66% { transform: translate(-20px, 20px) scale(0.95); }
}

.login-container {
  position: relative;
  z-index: 1;
}

.login-card {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 48px 44px;
  width: 420px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.8);
  animation: cardIn 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes cardIn {
  from {
    opacity: 0;
    transform: translateY(40px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.login-header {
  text-align: center;
  margin-bottom: 36px;
}

.login-logo {
  width: 80px;
  height: 80px;
  background: #fff;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  box-shadow: 0 8px 24px rgba(45, 140, 110, 0.15);
  overflow: hidden;
}

.login-logo img {
  width: 56px;
  height: 56px;
  object-fit: contain;
}

.login-header h1 {
  font-size: 24px;
  font-weight: 700;
  color: #212529;
  margin-bottom: 8px;
}

.login-header p {
  font-size: 13px;
  color: #868e96;
  letter-spacing: 1px;
}

.login-form {
  margin-bottom: 24px;
}

.login-form :deep(.el-form-item__label) {
  font-weight: 500;
  color: #495057;
}

.login-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  margin-top: 8px;
  background: linear-gradient(135deg, #6b9080 0%, #4a6b5c 100%);
  border: none;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(107, 144, 128, 0.2);
}

.login-footer {
  text-align: center;
  font-size: 14px;
  color: #6b7280;
}

.login-footer .divider {
  margin: 0 10px;
  color: #dee2e6;
}
</style>
