import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/auth/Login.vue'),
      meta: { guest: true }
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/auth/Register.vue'),
      meta: { guest: true }
    },
    {
      path: '/forget-password',
      name: 'ForgetPassword',
      component: () => import('@/views/auth/ForgetPassword.vue'),
      meta: { guest: true }
    },
    {
      path: '/',
      component: () => import('@/components/Layout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'Index',
          component: () => import('@/views/Index.vue')
        },
        {
          path: 'record',
          name: 'Record',
          component: () => import('@/views/Record.vue')
        },
        {
          path: 'audit',
          name: 'Audit',
          component: () => import('@/views/Audit.vue')
        },
        {
          path: 'view',
          name: 'View',
          component: () => import('@/views/ViewRecords.vue')
        },
        {
          path: 'report',
          name: 'Report',
          component: () => import('@/views/Report.vue')
        },
        {
          path: 'system/user-center',
          name: 'UserCenter',
          component: () => import('@/views/system/UserCenter.vue')
        },
        {
          path: 'system/users',
          name: 'Users',
          component: () => import('@/views/system/Users.vue')
        }
      ]
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ]
})

router.beforeEach((to, _from, next) => {
  const userStore = useUserStore()
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next('/login')
  } else if (to.meta.guest && userStore.isLoggedIn) {
    next('/')
  } else {
    next()
  }
})

export default router
