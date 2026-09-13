import { createRouter, createWebHistory } from 'vue-router'
import MainPage from '@/pages/MainPage.vue'
import LoginPage from '@/pages/LoginPage.vue'
import RegisterPage from '@/pages/RegisterPage.vue'
import SearchPage from '@/pages/SearchPage.vue'
import CasePage from '@/pages/CasePage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.PRAWOBIORCA_API_URL),
  routes: [
    {
      path: '/',
      name: 'MainPage',
      component: MainPage,
    },
    {
      path: '/regulations/:regulationId/documents',
      name: 'SearchPublicRegulation',
      component: SearchPage,
    },
    {
      path: '/user/regulations/:regulationId/documents',
      name: 'SearchUserRegulation',
      component: SearchPage,
    },
    {
      path: '/auth/login',
      name: 'LoginPage',
      component: LoginPage,
    },
    {
      path: '/accounts/register',
      name: 'RegisterPage',
      component: RegisterPage,
    },
    {
      path: '/user/cases/:id',
      name: 'CasePage',
      component: CasePage,
    },
  ],
})

export default router
