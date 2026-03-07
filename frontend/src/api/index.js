import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/modules/user'

// 替换 js-cookie 为 localStorage 封装
const CookieUtil = {
  get: (key) => localStorage.getItem(key),
  set: (key, value) => localStorage.setItem(key, value),
  remove: (key) => localStorage.removeItem(key)
}

// 创建 axios 实例
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json;charset=utf-8'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 获取 token（替换 Cookies.get 为 CookieUtil.get）
    const userStore = useUserStore()
    const token = userStore.token || CookieUtil.get('access_token')
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    ElMessage.error(error.message)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    const { code, msg } = response.data
    if (code && code !== 200) {
      ElMessage.error(msg || '请求失败')
      return Promise.reject(new Error(msg || 'Error'))
    }
    return response.data
  },
  (error) => {
    const { response } = error
    if (response) {
      // 401 未授权，清除 token 并跳转登录
      if (response.status === 401) {
        const userStore = useUserStore()
        userStore.logout()
        CookieUtil.remove('access_token')
        
        ElMessage.error('登录状态已过期，请重新登录')
        
        // 跳转登录页（如果是前端路由）
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
      } else {
        ElMessage.error(response.data?.msg || `请求错误 ${response.status}`)
      }
    } else {
      ElMessage.error('网络异常，请检查连接')
    }
    return Promise.reject(error)
  }
)

// 导出请求方法
export default request

// 封装常用请求方法
export const get = (url, params = {}) => {
  return request({
    url,
    method: 'get',
    params
  })
}

export const post = (url, data = {}) => {
  return request({
    url,
    method: 'post',
    data
  })
}

export const put = (url, data = {}) => {
  return request({
    url,
    method: 'put',
    data
  })
}

export const del = (url, data = {}) => {
  return request({
    url,
    method: 'delete',
    data
  })
}