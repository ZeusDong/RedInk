import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import OutlineView from '../views/OutlineView.vue'
import GenerateView from '../views/GenerateView.vue'
import ResultView from '../views/ResultView.vue'
import HistoryView from '../views/HistoryView.vue'
import SettingsView from '../views/SettingsView.vue'
import ReferenceView from '../views/ReferenceView.vue'
import AnalysisView from '../views/AnalysisView.vue'
import SummaryView from '../views/SummaryView.vue'
import AICreationView from '../views/AICreationView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/outline',
      name: 'outline',
      component: OutlineView
    },
    {
      path: '/generate',
      name: 'generate',
      component: GenerateView
    },
    {
      path: '/result',
      name: 'result',
      component: ResultView
    },
    {
      path: '/history',
      name: 'history',
      component: HistoryView
    },
    {
      path: '/history/:id',
      name: 'history-detail',
      component: HistoryView
    },
    {
      path: '/reference',
      name: 'reference',
      component: ReferenceView
    },
    {
      path: '/analysis',
      name: 'analysis',
      component: AnalysisView
    },
    {
      path: '/summary',
      name: 'summary',
      component: SummaryView
    },
    {
      path: '/settings',
      name: 'settings',
      component: SettingsView
    },
    {
      path: '/ai-creation',
      component: AICreationView,
      children: [
        {
          path: '',
          redirect: '/ai-creation/create'
        },
        {
          path: 'create',
          name: 'QuickCreate',
          component: () => import('@/components/ai-creation/quick-create/QuickCreatePage.vue')
        },
        {
          path: 'recommend',
          name: 'SmartRecommend',
          component: () => import('@/components/ai-creation/smart-recommend/SmartRecommendPage.vue')
        },
        {
          path: 'templates',
          name: 'TemplateLibrary',
          component: () => import('@/components/ai-creation/template-library/TemplateLibraryPage.vue')
        },
        {
          path: 'optimize',
          name: 'ContentOptimize',
          component: () => import('@/components/ai-creation/content-optimize/ContentOptimizePage.vue')
        }
      ]
    }
  ]
})

export default router
