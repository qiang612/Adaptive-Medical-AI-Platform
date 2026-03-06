// 校验手机号
export function validatePhone(phone) {
  const reg = /^1[3-9]\d{9}$/
  return reg.test(phone)
}

// 校验邮箱
export function validateEmail(email) {
  const reg = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
  return reg.test(email)
}

// 校验身份证号
export function validateIdCard(idCard) {
  const reg = /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/
  return reg.test(idCard)
}

// 校验密码强度
export function validatePasswordStrength(password) {
  const result = {
    level: 0,
    msg: ''
  }
  if (!password) {
    result.msg = '请输入密码'
    return result
  }
  if (password.length < 6) {
    result.msg = '密码长度不能少于6位'
    return result
  }
  if (/\d/.test(password)) result.level++
  if (/[a-z]/.test(password)) result.level++
  if (/[A-Z]/.test(password)) result.level++
  if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) result.level++

  if (result.level < 2) {
    result.msg = '密码强度较弱，建议包含数字和字母'
  } else if (result.level < 3) {
    result.msg = '密码强度中等'
  } else {
    result.msg = '密码强度强'
  }
  return result
}