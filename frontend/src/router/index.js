import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import GraphView from '../views/GraphView.vue'
import ImportData from '../views/ImportData.vue'
import Statistics from '../views/Statistics.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/graph',
    name: 'GraphView',
    component: GraphView
  },
  {
    path: '/import',
    name: 'ImportData',
    component: ImportData
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: Statistics
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
