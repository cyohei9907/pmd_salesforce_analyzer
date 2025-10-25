import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.PROD ? '/api' : 'http://localhost:8000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default {
  // 导入相关
  importFile(filePath) {
    return api.post('/import/file/', { file_path: filePath })
  },
  
  importDirectory(directoryPath) {
    return api.post('/import/directory/', { directory_path: directoryPath })
  },
  
  // Git仓库相关
  cloneRepository(repoUrl, branch = 'main', force = false) {
    return api.post('/git/clone/', { repo_url: repoUrl, branch, force })
  },
  
  analyzeRepository(repoName, apexDir = 'force-app/main/default/classes') {
    return api.post('/git/analyze/', { repo_name: repoName, apex_dir: apexDir })
  },
  
  cloneAndAnalyze(repoUrl, branch = 'main', apexDir = 'force-app/main/default/classes', force = false, autoImport = true) {
    return api.post('/git/clone-and-analyze/', { 
      repo_url: repoUrl, 
      branch, 
      apex_dir: apexDir, 
      force, 
      auto_import: autoImport 
    })
  },
  
  listRepositories() {
    return api.get('/git/repositories/')
  },
  
  deleteRepository(repoName) {
    return api.delete(`/git/repositories/${repoName}/`)
  },
  
  // 图数据查询
  getGraphData() {
    return api.get('/graph/')
  },
  
  getClassGraph(className) {
    return api.get(`/graph/class/${className}/`)
  },
  
  // 图布局保存和加载
  saveGraphLayout(layout) {
    return api.post('/graph/layout/', { layout })
  },
  
  loadGraphLayout() {
    return api.get('/graph/layout/load/')
  },
  
  // 统计信息
  getStatistics() {
    return api.get('/statistics/')
  },
  
  getImportedFiles() {
    return api.get('/files/')
  },
  
  // 清空数据库
  clearDatabase() {
    return api.delete('/clear/')
  }
}
