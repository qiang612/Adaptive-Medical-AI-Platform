import { defineStore } from 'pinia'
import { getSystemConfig } from '@/api/system'

export const useSystemStore = defineStore('system', {
  state: () => ({
    systemConfig: null
  }),
  actions: {
    async loadSystemConfig() {
      try {
        const res = await getSystemConfig()
        this.systemConfig = res
        return res
      } catch (error) {
        console.error('加载系统配置失败', error)
        return null
      }
    }
  }
})