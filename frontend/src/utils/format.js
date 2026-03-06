import dayjs from 'dayjs'

// 格式化日期时间
export function formatDateTime(date, format = 'YYYY-MM-DD HH:mm:ss') {
  if (!date) return '-'
  return dayjs(date).format(format)
}

// 格式化日期
export function formatDate(date, format = 'YYYY-MM-DD') {
  if (!date) return '-'
  return dayjs(date).format(format)
}

// 格式化文件大小
export function formatFileSize(size) {
  if (!size || size === 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let index = 0
  while (size >= 1024 && index < units.length - 1) {
    size /= 1024
    index++
  }
  return `${size.toFixed(2)} ${units[index]}`
}

// 格式化百分比
export function formatPercent(value, fixed = 2) {
  if (value === undefined || value === null) return '-'
  return `${(value * 100).toFixed(fixed)}%`
}