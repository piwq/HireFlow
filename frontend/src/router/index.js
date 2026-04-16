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
    path: '/candidate/applications',
    component: () => import('@/views/candidate/ApplicationsView.vue'),
    meta: { role: 'candidate' },
  },
  {
    path: '/candidate/resume-builder',
    component: () => import('@/views/candidate/LiveResumeBuilderView.vue'),
    meta: { role: 'candidate' },
  },
  {
    path: '/candidate/interviews',
    component: () => import('@/views/candidate/InterviewsView.vue'),
    meta: { role: 'candidate' },
  },
  {
    path: '/hr',
    component: () => import('@/views/hr/CandidatesView.vue'),
    meta: { role: 'hr' },
  },
  {
    path: '/hr/candidates/:id',
    component: () => import('@/views/hr/CandidateCardView.vue'),
    meta: { role: 'hr' },
  },
  {
    path: '/hr/vacancies',
    component: () => import('@/views/hr/VacanciesView.vue'),
    meta: { role: 'hr' },
  },
  {
    path: '/hr/interview-requests',
    component: () => import('@/views/hr/InterviewRequestsView.vue'),
    meta: { role: 'hr' },
  },
  {
    path: '/manager',
    component: () => import('@/views/manager/ReviewView.vue'),
    meta: { role: 'manager' },
  },
  {
    path: '/manager/reviews',
    component: () => import('@/views/manager/ManagerReviewsView.vue'),
    meta: { role: 'manager' },
  },
  {
    path: '/manager/candidates',
    component: () => import('@/views/manager/ManagerCandidatesView.vue'),
    meta: { role: 'manager' },
  },
  {
    path: '/admin',
    component: () => import('@/views/admin/AdminView.vue'),
    meta: { role: 'admin' },
  },
  {
    path: '/chat',
    component: () => import('@/views/chat/ChatView.vue'),
    meta: { roles: ['hr', 'manager', 'candidate', 'admin'] },
  },
  {
    path: '/call/:roomCode',
    component: () => import('@/views/VideoCallView.vue'),
    meta: { roles: ['hr', 'manager', 'candidate', 'admin'] },
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

  // Single role restriction
  if (to.meta.role && to.meta.role !== role) {
    return `/${role}`
  }

  // Multi-role restriction
  if (to.meta.roles && !to.meta.roles.includes(role)) {
    return `/${role}`
  }
})

export default router
