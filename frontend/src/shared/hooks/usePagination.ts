import { useState, useCallback } from 'react'

interface UsePaginationProps {
  defaultPage?: number
  defaultPageSize?: number
}

interface UsePaginationReturn {
  page: number
  pageSize: number
  onChange: (page: number, pageSize: number) => void
  reset: () => void
}

export const usePagination = (
  props: UsePaginationProps = {}
): UsePaginationReturn => {
  const { defaultPage = 1, defaultPageSize = 10 } = props
  const [page, setPage] = useState(defaultPage)
  const [pageSize, setPageSize] = useState(defaultPageSize)

  const onChange = useCallback((newPage: number, newPageSize: number) => {
    setPage(newPage)
    setPageSize(newPageSize)
  }, [])

  const reset = useCallback(() => {
    setPage(defaultPage)
    setPageSize(defaultPageSize)
  }, [defaultPage, defaultPageSize])

  return { page, pageSize, onChange, reset }
}
