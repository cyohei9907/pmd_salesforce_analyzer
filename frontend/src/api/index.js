import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
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
  
  // 图数据查询
  getGraphData() {
    return api.get('/graph/')
  },
  
  getClassGraph(className) {
    return api.get(`/graph/class/${className}/`)
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
