import { Table, Pagination } from 'antd'
import type { TableProps, PaginationProps } from 'antd'

interface PaginationTableProps<T> extends TableProps<T> {
  total: number
  current: number
  pageSize: number
  onChange: (page: number, pageSize: number) => void
}

function PaginationTable<T extends object>({
  total,
  current,
  pageSize,
  onChange,
  ...tableProps
}: PaginationTableProps<T>) {
  return (
    <div>
      <Table {...tableProps} pagination={false} />
      <div className="mt-4 flex justify-end">
        <Pagination
          current={current}
          pageSize={pageSize}
          total={total}
          onChange={onChange}
          showSizeChanger
          showTotal={(total) => `共 ${total} 条`}
        />
      </div>
    </div>
  )
}

export default PaginationTable
