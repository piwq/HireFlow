import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: () => import('@/views/LoginView.vue'), meta: { guest: true } },
  { path: '/register', component: () => import('@/views/RegisterView.vue'), meta: { guest: true } },
  {
    path: '/candidate',
    component: () => import('@/views/candidate/ProfileView.vue'),
    meta: { role: 'candidate' },
  },
  {
    path: '/hr',
    component: () => import('@/views/hr/CandidatesView.vue'),
    meta: { role: 'hr' },
  },
  {
    path: '/manager',
    component: () => import('@/views/manager/ReviewView.vue'),
    meta: { role: 'manager' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role')

  if (!token && !to.meta.guest) {
    return '/login'
  }

  if (token && to.meta.guest) {
    return `/${role}`
  }

  if (to.meta.role && to.meta.role !== role) {
    return `/${role}`
  }
})

export default router
