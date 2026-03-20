<template>
  <el-container class="layout-container">
    <el-aside width="240px" class="sidebar">
      <div class="logo">
        <img src="/logo.ico" alt="logo" class="logo-img" />
        <div class="logo-content">
          <span class="logo-text">ABUS报销管理系统</span>
          <span class="logo-sub">Reimbursement</span>
        </div>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        class="sidebar-menu"
        :ellipsis="false"
      >
        <el-menu-item index="/">
          <el-icon><HomeFilled /></el-icon>
          <span>首页仪表盘</span>
        </el-menu-item>
        <el-menu-item v-if="isEmployee" index="/record">
          <el-icon><EditPen /></el-icon>
          <span>报销申请录入</span>
        </el-menu-item>
        <el-menu-item v-if="isManager" index="/audit">
          <el-icon><Checked /></el-icon>
          <span>报销单审批</span>
        </el-menu-item>
        <el-menu-item v-if="isFinance" index="/audit">
          <el-icon><CreditCard /></el-icon>
          <span>财务审批</span>
        </el-menu-item>
        <el-menu-item index="/view">
          <el-icon><Document /></el-icon>
          <span>已核报销查看</span>
        </el-menu-item>
        <el-menu-item index="/report">
          <el-icon><TrendCharts /></el-icon>
          <span>报销统计报表</span>
        </el-menu-item>
        <el-menu-item index="/system/user-center">
          <el-icon><User /></el-icon>
          <span>个人中心</span>
        </el-menu-item>
        <el-menu-item v-if="isAdmin" index="/system/users">
          <el-icon><UserFilled /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
      </el-menu>
      <div class="sidebar-footer">
        <div class="version">v1.0.0</div>
      </div>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <h1 class="page-title">{{ pageTitle }}</h1>
        </div>
        <div class="header-right">
          <div class="user-info">
            <el-avatar :size="36" class="user-avatar">
              {{ userStore.userInfo?.name?.charAt(0) || 'U' }}
            </el-avatar>
            <div class="user-detail">
              <span class="user-name">{{ userStore.userInfo?.name }}</span>
              <span class="user-role">{{ userStore.role }}</span>
            </div>
          </div>
          <el-divider direction="vertical" />
          <el-button type="primary" link @click="handleLogout">
            <el-icon><SwitchButton /></el-icon>
            退出登录
          </el-button>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" :key="route.fullPath" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const isEmployee = computed(() => userStore.role === '员工')
const isManager = computed(() => userStore.role === '经理')
const isFinance = computed(() => userStore.role === '财务管理员')
const isAdmin = computed(() => userStore.role === '系统管理员')

const activeMenu = computed(() => route.path)

const pageTitleMap: Record<string, string> = {
  '/': '首页仪表盘',
  '/record': '报销申请录入',
  '/audit': '报销单审批',
  '/view': '已核报销查看',
  '/report': '报销统计报表',
  '/system/user-center': '个人中心'
}

const pageTitle = computed(() => pageTitleMap[route.path] || 'ABUS报销管理系统')

async function handleLogout() {
  await ElMessageBox.confirm('确认退出登录？', '提示', { type: 'warning' })
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
  overflow: hidden;
  background: var(--bg-tertiary);
}

.sidebar {
  background: #ffffff;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 2px 0 12px rgba(0, 0, 0, 0.06);
  border-right: 1px solid var(--border-light);
}

.logo {
  height: 72px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  gap: 12px;
  border-bottom: 1px solid var(--border-light);
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
}

.logo-img {
  width: 36px;
  height: 36px;
  object-fit: contain;
}

.logo-content {
  display: flex;
  flex-direction: column;
}

.logo-text {
  color: var(--text-primary);
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.logo-sub {
  color: var(--text-tertiary);
  font-size: 10px;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.sidebar-menu {
  border-right: none;
  flex: 1;
  padding: 12px 0;
  background: transparent;
}

.sidebar-menu :deep(.el-menu-item) {
  height: 48px;
  line-height: 48px;
  margin: 4px 12px;
  padding: 0 16px !important;
  border-radius: 10px;
  color: var(--text-secondary);
  transition: all 0.25s ease;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: #f0f5f3;
  color: #6b9080;
  font-weight: 500;
}

.sidebar-menu :deep(.el-menu-item.is-active::before) {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background: linear-gradient(180deg, #6b9080 0%, #8fb3a4 100%);
  border-radius: 0 3px 3px 0;
}

.sidebar-menu :deep(.el-icon) {
  font-size: 18px;
}

.sidebar-footer {
  padding: 16px 20px;
  border-top: 1px solid var(--border-light);
}

.version {
  color: var(--text-tertiary);
  font-size: 12px;
}

.header {
  background: var(--bg-primary);
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-light);
  box-shadow: var(--shadow-sm);
  padding: 0 28px;
  height: 72px;
}

.header-left .page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: 0.5px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  background: linear-gradient(135deg, #6b9080 0%, #8fb3a4 100%);
  font-weight: 600;
}

.user-detail {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.3;
}

.user-role {
  font-size: 12px;
  color: var(--text-tertiary);
}

.el-divider--vertical {
  height: 24px;
  border-color: var(--border-color);
}

.main-content {
  background: var(--bg-tertiary);
  overflow-y: auto;
  padding: 24px;
}

/* 页面过渡动画 */
.page-enter-active,
.page-leave-active {
  transition: all 0.25s ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(12px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-12px);
}
</style>
