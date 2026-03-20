<template>
  <router-view v-slot="{ Component }">
    <transition name="fade-slide" mode="out-in">
      <component :is="Component" />
    </transition>
  </router-view>
</template>

<script setup lang="ts">
</script>

<style>
:root {
  /* 专业企业级配色 - 低饱和度简洁风格 */
  --primary-color: #6b9080;
  --primary-light: #8fb3a4;
  --primary-dark: #4a6b5c;
  --primary-subtle: #f0f5f3;
  --success-color: #6b9080;
  --success-subtle: #f0f5f3;
  --warning-color: #c9a86c;
  --warning-subtle: #faf6ef;
  --danger-color: #c17a7a;
  --danger-subtle: #faf5f5;
  --info-color: #8a9aa8;
  --info-subtle: #f5f7f9;
  
  /* 文字颜色 - 柔和深色 */
  --text-primary: #212529;
  --text-secondary: #495057;
  --text-tertiary: #868e96;
  --text-disabled: #adb5bd;
  
  /* 背景色 - 清爽浅色系 */
  --bg-primary: #ffffff;
  --bg-secondary: #f8f9fa;
  --bg-tertiary: #f1f3f5;
  --bg-hover: #e9ecef;
  
  /* 边框颜色 */
  --border-color: #dee2e6;
  --border-light: #f1f3f5;
  
  /* 阴影 - 柔和精致 */
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.06);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.08);
  --shadow-lg: 0 12px 24px rgba(0, 0, 0, 0.12);
  --shadow-xl: 0 20px 40px rgba(0, 0, 0, 0.15);
  
  /* 圆角 - 更圆润 */
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 14px;
  --radius-xl: 20px;
  --radius-full: 9999px;
  
  /* 过渡 */
  --transition-fast: 0.15s ease;
  --transition-normal: 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  --transition-slow: 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background-color: var(--bg-tertiary);
  color: var(--text-primary);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  min-height: 100vh;
}

/* 滚动条样式 - 更精致 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #ced4da;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #adb5bd;
}

/* 全局过渡动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all var(--transition-normal);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Element Plus 组件全局样式优化 - 柔和风格 */
.el-button {
  border-radius: var(--radius-md);
  font-weight: 500;
  transition: all var(--transition-fast);
  border-color: var(--border-color);
}

.el-button:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.el-button:active {
  transform: translateY(0);
}

.el-button--primary {
  background: linear-gradient(135deg, #2d8c6e 0%, #1f6b53 100%);
  border: none;
}

.el-button--primary:hover {
  background: linear-gradient(135deg, #5ba896 0%, #2d8c6e 100%);
}

.el-input__wrapper {
  border-radius: var(--radius-md);
  box-shadow: 0 0 0 1px var(--border-color) inset;
  transition: all var(--transition-fast);
  background: var(--bg-primary);
}

.el-input__wrapper:hover {
  box-shadow: 0 0 0 1px #adb5db inset;
}

.el-input__wrapper.is-focus {
  box-shadow: 0 0 0 2px var(--primary-subtle) inset, 0 0 0 1px var(--primary-color) inset;
}

.el-select .el-input__wrapper {
  border-radius: var(--radius-md);
}

.el-table {
  --el-table-border-color: var(--border-light);
  --el-table-header-bg-color: var(--bg-secondary);
  --el-table-row-hover-bg-color: var(--bg-hover);
  font-size: 14px;
  --el-table-border: 1px solid var(--border-light);
}

.el-table th.el-table__cell {
  font-weight: 600;
  color: var(--text-secondary);
  background: var(--bg-secondary) !important;
}

.el-table .el-table__row {
  transition: all var(--transition-fast);
}

.el-table .el-table__row:hover > td {
  background-color: var(--bg-hover) !important;
}

.el-card {
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-normal);
}

.el-card:hover {
  box-shadow: var(--shadow-md);
  border-color: #dee2e6;
}

.el-dialog {
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: var(--shadow-xl);
}

.el-dialog__header {
  padding: 20px 24px 16px;
  border-bottom: 1px solid var(--border-light);
  background: var(--bg-secondary);
}

.el-dialog__title {
  font-weight: 600;
  font-size: 16px;
  color: var(--text-primary);
}

.el-dialog__body {
  padding: 24px;
}

.el-tag {
  border-radius: var(--radius-sm);
  font-weight: 500;
  border: none;
}

.el-tag--warning {
  background: var(--warning-subtle);
  color: #f59f00;
}

.el-tag--success {
  background: var(--success-subtle);
  color: #2f9e44;
}

.el-tag--danger {
  background: var(--danger-subtle);
  color: #e03131;
}

.el-tag--info {
  background: var(--info-subtle);
  color: var(--text-secondary);
}

.el-pagination {
  --el-pagination-button-bg-color: var(--bg-secondary);
}

.el-pagination .el-pager li {
  border-radius: var(--radius-sm);
  margin: 0 2px;
}

.el-pagination .el-pager li.is-active {
  background: linear-gradient(135deg, #2d8c6e 0%, #1f6b53 100%);
  border: none;
}

.el-form-item__label {
  font-weight: 500;
  color: var(--text-secondary);
}

.el-descriptions__label {
  font-weight: 500;
  color: var(--text-secondary);
}

.el-descriptions__cell {
  border-color: var(--border-light);
}

/* 页面容器通用样式 */
.page-container {
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow-sm);
  animation: pageIn 0.3s ease;
}

@keyframes pageIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 卡片悬停效果 */
.card-hover {
  transition: all var(--transition-normal);
}

.card-hover:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
}

/* 数字动画 */
.number-animate {
  font-variant-numeric: tabular-nums;
  transition: all var(--transition-normal);
}

/* 渐变背景 */
.gradient-bg {
  background: linear-gradient(135deg, #2d8c6e 0%, #5ba896 100%);
}

/* 玻璃拟态效果 */
.glass {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.5);
}

/* 选中项高亮 */
.el-menu-item.is-active {
  background: linear-gradient(90deg, #e8f5f1 0%, transparent 100%) !important;
  color: #2d8c6e !important;
}

.el-menu-item.is-active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background: linear-gradient(180deg, #2d8c6e 0%, #5ba896 100%);
  border-radius: 0 3px 3px 0;
}
</style>
