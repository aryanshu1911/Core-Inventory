import { useState, useEffect, useMemo } from 'react'
import { useLocation } from 'react-router-dom'
import Navbar from '../components/Navbar'
import DataTable from '../components/DataTable'
import { stockApi, productsApi, warehousesApi } from '../api/client'
import toast from 'react-hot-toast'
import { AlertTriangle } from 'lucide-react'

export default function StockView() {
  const [data, setData] = useState([])
  const [products, setProducts] = useState([])
  const [warehouses, setWarehouses] = useState([])
  const [loading, setLoading] = useState(true)
  const { search } = useLocation()
  const queryParams = useMemo(() => new URLSearchParams(search), [search])
  const statusFilter = queryParams.get('status')

  const fetch = () => {
    setLoading(true)
    const stockParams = { limit: 200 }
    if (statusFilter) stockParams.stock_status = statusFilter

    Promise.all([
      stockApi.list(stockParams),
      productsApi.list({ limit: 200 }),
      warehousesApi.list({ limit: 100 })
    ])
      .then(([s, p, w]) => { setData(s.data); setProducts(p.data); setWarehouses(w.data) })
      .catch(e => toast.error(e.message))
      .finally(() => setLoading(false))
  }
  useEffect(fetch, [statusFilter])

  const whName   = (id) => warehouses.find(w => w.id === id)?.name  || '—'
  const prodName = (id) => products.find(p => p.id === id)?.name    || '—'
  const reorder  = (pid) => products.find(p => p.id === pid)?.reorder_level || 0


  const qtyCell = (qty, row) => {
    const rl = reorder(row.product_id)
    const isLow = qty <= rl && qty > 0
    const isOut = qty === 0
    return (
      <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <span style={{ fontWeight: 700, color: isOut ? 'var(--accent-red)' : isLow ? 'var(--accent-yellow)' : 'var(--text-primary)' }}>
          {qty}
        </span>
        {(isLow || isOut) && <AlertTriangle size={13} color={isOut ? 'var(--accent-red)' : 'var(--accent-yellow)'} />}
      </span>
    )
  }

  const cols = [
    { key: 'product_id',   label: 'Product',       render: v => prodName(v) },
    { key: 'warehouse_id', label: 'Warehouse & Loc', render: v => whName(v) },
    { key: 'cost',         label: 'per unit cost', render: () => '3000 Rs' },
    { key: 'quantity',     label: 'On hand',       render: (v, row) => qtyCell(v, row) },
    { key: 'free',         label: 'free to Use',   render: (v, row) => row.quantity }
  ]

  return (
    <>
      <Navbar title="Stock" subtitle="This page contains the warehouse details & location." />
      <div className="page-body">
        <div className="page-header">
          <div className="page-header-left">
            <h2>Current Stock</h2>
            <p>
              {statusFilter ? (
                <>Filtering by: <span className="badge badge-blue">{statusFilter.toUpperCase()} STOCK</span></>
              ) : (
                "This page contains the warehouse details & location."
              )}
            </p>
          </div>
        </div>
        <DataTable columns={cols} data={data} loading={loading} />


      </div>
    </>
  )
}
