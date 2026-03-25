import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/modules/user'

const TokenKey = 'access_token'

const TokenUtil = {
  get: () => localStorage.getItem(TokenKey),
  set: (token) => localStorage.setItem(TokenKey, token),
  remove: () => localStorage.removeItem(TokenKey)
}

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json;charset=utf-8'
  }
})

request.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    const token = userStore.token || TokenUtil.get()

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
      if (response.status === 401) {
        const userStore = useUserStore()
        userStore.logout()
        TokenUtil.remove()

        ElMessage.error('登录状态已过期，请重新登录')

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

export default request

export const get = (url, params = {}) => {
  return request({ url, method: 'get', params })
}

export const post = (url, data = {}) => {
  return request({ url, method: 'post', data })
}

export const put = (url, data = {}) => {
  return request({ url, method: 'put', data })
}

export const del = (url, data = {}) => {
  return request({ url, method: 'delete', data })
}

export { TokenUtil }