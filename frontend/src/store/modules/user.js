import { defineStore } from 'pinia'
import { login as loginApi, getCurrentUser } from '@/api/user'

// 定义 Token 的 key
const TOKEN_KEY = 'access_token'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) || '',
    userInfo: null
  }),

  getters: {
    // 是否已登录
    isLoggedIn: (state) => !!state.token,
    // 用户名
    username: (state) => state.userInfo?.username || '',
    // 是否为管理员（根据实际返回的用户信息字段调整）
    isAdmin: (state) => {
      // 示例：根据角色判断，可根据后端返回结构修改
      return state.userInfo?.role === 'admin' || state.userInfo?.role_id === 1 || false
    }
  },

  actions: {
    /**
     * 登录
     * @param {Object|string} arg1 - 登录参数对象 {username, password} 或 单独的用户名
     * @param {string} [arg2] - 密码（仅当arg1为用户名时传入）
     */
    async login(arg1, arg2) {
      try {
        // 兼容两种调用方式：对象参数 或 分开传递用户名密码
        let loginData;
        if (typeof arg1 === 'object' && arg1 !== null) {
          // 方式1：传入对象 { username, password }
          loginData = {
            username: (arg1.username || '').trim(),
            password: (arg1.password || '').trim()
          };
        } else {
          // 方式2：分开传递 login(username, password)
          loginData = {
            username: (arg1 || '').trim(),
            password: (arg2 || '').trim()
          };
        }

        // 前置参数校验
        if (!loginData.username) {
          throw new Error('用户名不能为空');
        }
        if (!loginData.password) {
          throw new Error('密码不能为空');
        }

        // 调用登录接口
        const res = await loginApi(loginData);
        
        // 校验接口返回结果
        if (!res || !res.access_token) {
          throw new Error('登录失败：未获取到令牌');
        }

        // 存储 token
        this.token = res.access_token;
        localStorage.setItem(TOKEN_KEY, res.access_token);

        // 获取用户信息
        await this.getUserInfo();

        return res; // 返回结果给调用方
      } catch (error) {
        // 清空无效 token
        this.token = '';
        localStorage.removeItem(TOKEN_KEY);
        
        // 抛出错误，让组件层捕获并提示
        throw new Error(error.message || '登录失败，请稍后重试');
      }
    },

    /**
     * 获取用户信息
     */
    async getUserInfo() {
      try {
        // 未登录时不获取用户信息
        if (!this.token) {
          throw new Error('未登录，无法获取用户信息');
        }

        const res = await getCurrentUser();
        
        // 校验返回结果
        if (!res) {
          throw new Error('获取用户信息失败：返回数据为空');
        }

        this.userInfo = res;
        return res;
      } catch (error) {
        // 清空无效用户信息
        this.userInfo = null;
        throw new Error(error.message || '获取用户信息失败');
      }
    },

    /**
     * 登出
     */
    logout() {
      try {
        // 清空状态
        this.token = '';
        this.userInfo = null;
        // 清除本地存储
        localStorage.removeItem(TOKEN_KEY);
      } catch (error) {
        console.error('登出操作失败:', error);
        throw new Error('登出失败，请手动刷新页面');
      }
    }
  }
})