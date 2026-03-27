// 导入你封装的 request 实例
import request from './index'

/**
 * 登录接口（适配后端 /api/v1/users/login 路径）
 * @param {string|Object} arg1 用户名 或 包含username/password的对象
 * @param {string} [arg2] 密码（仅当arg1是字符串时需要）
 * @returns {Promise} 登录结果
 */
export function login(arg1, arg2) {
  // 兼容两种调用方式：对象参数 或 分开传递用户名密码
  let username, password;
  if (typeof arg1 === 'object' && arg1 !== null) {
    // 方式1：传入对象 { username, password }
    username = (arg1.username || '').trim();
    password = (arg1.password || '').trim();
  } else {
    // 方式2：分开传递 login('admin', '123456')
    username = (arg1 || '').trim();
    password = (arg2 || '').trim();
  }

  // 前置校验：避免空值请求
  if (!username || !password) {
    console.error('登录参数校验失败:', { username, password, arg1, arg2 }); // 调试用
    return Promise.reject(new Error('用户名和密码不能为空'));
  }

  // OAuth2 密码流必须用 URLSearchParams 格式
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);

  return request.post('/users/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  }).catch(error => {
    console.error('登录接口请求失败:', error);
    const errMsg = {
      404: '登录接口不存在，请检查后端路由配置',
      401: '用户名或密码错误',
      500: '服务器内部错误，请稍后重试'
    }[error.response?.status] || error.response?.data?.detail || '登录失败，请检查账号密码或接口配置';
    throw new Error(errMsg);
  });
}

/**
 * 获取当前用户信息
 * @returns {Promise} 用户信息
 */
export function getCurrentUser() {
  return request.get('/users/me')
    .catch(error => {
      console.error('获取用户信息失败:', error)
      const errMsg = error.response?.status === 401
        ? '登录状态失效，请重新登录'
        : '获取用户信息失败'
      throw new Error(errMsg)
    })
}

/**
 * 获取用户列表
 * @param {Object} params 查询参数（如 page、page_size、keyword）
 * @returns {Promise} 用户列表
 */
export function getUsers(params = {}) {
  const queryParams = { page: 1, page_size: 10, ...params }
  return request.get('/users/', { params: queryParams })
    .catch(error => {
      console.error('获取用户列表失败:', error)
      throw new Error('获取用户列表失败')
    })
}

/**
 * 创建用户
 * @param {Object} data 用户信息（username/password/role/full_name 等）
 * @returns {Promise} 创建结果
 */
export function createUser(data) {
  const requiredFields = ['username', 'password', 'role', 'full_name']
  const missingFields = requiredFields.filter(field => !data[field])
  if (missingFields.length > 0) {
    return Promise.reject(new Error(`创建用户失败：缺少必填字段 ${missingFields.join(', ')}`))
  }

  const submitData = {
    username: data.username,
    password: data.password,
    full_name: data.full_name,
    role: data.role,
    email: data.email || null,
    phone: data.phone || null,
    department: data.department || null,
    is_active: data.is_active !== undefined ? data.is_active : true
  }

  return request.post('/users/register', submitData)
    .catch(error => {
      console.error('创建用户失败:', error)
      throw new Error(error.response?.data?.detail || '创建用户失败')
    })
}

/**
 * 更新用户信息
 * @param {string|number} id 用户ID
 * @param {Object} data 要更新的用户信息
 * @returns {Promise} 更新结果
 */
export function updateUser(id, data) {
  // 防呆处理：避免 id 为空导致的 404
  if (!id) {
    return Promise.reject(new Error('用户ID不能为空'))
  }

  return request.put(`/users/${id}`, data)
    .catch(error => {
      console.error('更新用户失败:', error)
      throw new Error(error.response?.data?.detail || '更新用户失败')
    })
}

/**
 * 删除用户
 * @param {string|number} id 用户ID
 * @returns {Promise} 删除结果
 */
export function deleteUser(id) {
  if (!id) {
    return Promise.reject(new Error('用户ID不能为空'))
  }

  return request.delete(`/users/${id}`)
    .catch(error => {
      console.error('删除用户失败:', error)
      throw new Error('删除用户失败')
    })
}

/**
 * 重置用户密码
 * @param {string|number} id 用户ID
 * @param {Object} data 密码信息（如 new_password）
 * @returns {Promise} 重置结果
 */
export function resetUserPassword(id, data) {
  if (!id) {
    return Promise.reject(new Error('用户ID不能为空'))
  }

  // 校验新密码
  if (!data?.new_password) {
    return Promise.reject(new Error('新密码不能为空'))
  }

  return request.post(`/users/${id}/reset-password`, data)
    .catch(error => {
      console.error('重置密码失败:', error)
      throw new Error('重置密码失败')
    })
}

/**
 * 切换用户状态
 * @param {string|number} id 用户ID
 * @param {boolean} is_active 是否激活
 * @returns {Promise} 切换结果
 */
export function toggleUserStatus(id, is_active) {
  if (!id) {
    return Promise.reject(new Error('用户ID不能为空'))
  }

  // 确保 is_active 是布尔值
  const status = typeof is_active === 'boolean' ? is_active : Boolean(is_active)

  return request.patch(`/users/${id}/status`, { is_active: status })
    .catch(error => {
      console.error('切换用户状态失败:', error)
      throw new Error('切换用户状态失败')
    })
}

/**
 * 获取角色列表
 * @returns {Promise} 角色列表
 */
export function getRoles() {
  return request.get('/roles/')
    .catch(error => {
      console.error('获取角色列表失败:', error)
      throw new Error('获取角色列表失败')
    })
}

/**
 * 更新用户角色
 * @param {string|number} id 用户ID
 * @param {string|number} roleId 角色ID
 * @returns {Promise} 更新结果
 */
export function updateUserRole(id, roleId) {
  if (!id || !roleId) {
    return Promise.reject(new Error('用户ID和角色ID不能为空'))
  }

  return request.put(`/users/${id}/role`, { role_id: roleId })
    .catch(error => {
      console.error('更新用户角色失败:', error)
      throw new Error('更新用户角色失败')
    })
}

/**
 * 获取模型列表（解决后端 /api/v1/models/ 422 错误）
 * @param {Object} params 查询参数（默认 limit=100）
 * @returns {Promise} 模型列表
 */
export function getModels(params = {}) {
  // 增强默认参数：补充 page 参数，避免后端校验失败
  const queryParams = {
    limit: 100,
    page: 1,
    ...params
  }
  return request.get('/models/', { params: queryParams })
    .catch(error => {
      console.error('获取模型列表失败:', error)
      throw new Error('获取模型列表失败')
    })
}

/**
 * 获取活跃模型（核心修复：解决 422 Unprocessable Entity 错误）
 * @param {string|number} modelId 模型ID（后端必填参数）
 * @returns {Promise} 活跃模型信息
 */
export function getActiveModel(modelId) {
  // 前置校验：必须传入模型ID
  if (!modelId) {
    return Promise.reject(new Error('模型ID不能为空（后端必填参数）'))
  }

  // 核心修复：传递 model_id 参数，解决 422 错误
  return request.get('/models/active', {
    params: { model_id: modelId } // 补充后端要求的必填参数
  }).catch(error => {
    console.error('获取活跃模型失败:', error)
    const errMsg = error.response?.status === 422
      ? '获取活跃模型失败：缺少模型ID参数'
      : error.response?.data?.detail || '获取活跃模型失败'
    throw new Error(errMsg)
  })
}

// 新增：通用的请求工具函数（可选，用于简化重复逻辑）
export function requestWrapper(apiFunc, ...args) {
  return apiFunc(...args)
    .catch(error => {
      console.error('请求失败:', error)
      if (error.message.includes('登录状态失效')) {
        window.location.href = '/login'
      }
      throw error
    })
}

export function uploadMyAvatar(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/users/me/avatar', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }).catch(error => {
    console.error('上传头像失败:', error)
    throw new Error(error.response?.data?.detail || '上传头像失败')
  })
}

export function uploadUserAvatar(userId, file) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post(`/users/${userId}/avatar`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }).catch(error => {
    console.error('上传用户头像失败:', error)
    throw new Error(error.response?.data?.detail || '上传用户头像失败')
  })
}