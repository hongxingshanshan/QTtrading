import { useState, useEffect } from 'react'

/**
 * 持久化 state 到 sessionStorage 的 hook
 * 页面跳转后返回时，状态会恢复
 */
export function usePersistedState<T>(
  key: string,
  initialValue: T
): [T, (value: T | ((prev: T) => T)) => void] {
  // 初始化时从 sessionStorage 读取
  const [state, setState] = useState<T>(() => {
    try {
      const stored = sessionStorage.getItem(key)
      if (stored !== null) {
        return JSON.parse(stored)
      }
    } catch (e) {
      console.warn(`Failed to parse persisted state for key "${key}":`, e)
    }
    return initialValue
  })

  // 状态变化时同步到 sessionStorage
  useEffect(() => {
    try {
      sessionStorage.setItem(key, JSON.stringify(state))
    } catch (e) {
      console.warn(`Failed to persist state for key "${key}":`, e)
    }
  }, [key, state])

  return [state, setState]
}
