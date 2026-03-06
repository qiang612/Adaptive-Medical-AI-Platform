import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    isCollapse: false,
    globalLoading: false
  }),
  actions: {
    toggleCollapse() {
      this.isCollapse = !this.isCollapse
    },
    setCollapse(value) {
      this.isCollapse = value
    },
    showLoading() {
      this.globalLoading = true
    },
    hideLoading() {
      this.globalLoading = false
    }
  }
})