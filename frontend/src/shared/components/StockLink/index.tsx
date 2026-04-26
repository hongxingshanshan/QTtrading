import { useNavigate } from 'react-router-dom'

interface StockLinkProps {
  code: string | undefined
  children: React.ReactNode
}

function StockLink({ code, children }: StockLinkProps) {
  const navigate = useNavigate()

  if (!code) {
    return <>{children}</>
  }

  return (
    <a
      className="text-blue-600 hover:text-blue-800 cursor-pointer"
      onClick={() => navigate(`/stock/trend/${code}`)}
    >
      {children}
    </a>
  )
}

export default StockLink
