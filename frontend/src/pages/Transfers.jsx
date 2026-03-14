import { useState, useEffect, useCallback, useMemo } from 'react'
import { useLocation } from 'react-router-dom'
import Navbar from '../components/Navbar'
import DataTable from '../components/DataTable'
import Modal from '../components/Modal'
import { transfersApi, productsApi, warehousesApi } from '../api/client'
import toast from 'react-hot-toast'
import { Plus } from 'lucide-react'

export default function Transfers() {
  const [data, setData] = useState([])
  const [products, setProducts] = useState([])
  const [warehouses, setWarehouses] = useState([])
  const [loading, setLoading] = useState(true)
  const [modal, setModal] = useState(false)
  const [form, setForm] = useState({ product_id: '', from_warehouse_id: '', to_warehouse_id: '', quantity: 1 })
  const [saving, setSaving] = useState(false)

  const { search } = useLocation()
  const statusFilter = useMemo(() => new URLSearchParams(search).get('status'), [search])

  const fetch = useCallback(() => {
    setLoading(true)
    const params = { limit: 50 };
    if (statusFilter) params.status = statusFilter;
    Promise.all([transfersApi.list(params), productsApi.list({ limit: 200 }), warehousesApi.list({ limit: 100 })])
      .then(([t, p, w]) => { setData(t.data); setProducts(p.data); setWarehouses(w.data) })
      .catch(e => toast.error(e.message))
      .finally(() => setLoading(false))
  }, [statusFilter])
  useEffect(fetch, [fetch])

  const save = async (e) => {
    e.preventDefault(); setSaving(true)
    try {
      await transfersApi.create(form); toast.success('Transfer completed')
      setModal(false); fetch()
    } catch (err) { toast.error(err.message) } finally { setSaving(false) }
  }

  const whName = (id) => warehouses.find(w => w.id === id)?.name || '—'
  const prodName = (id) => products.find(p => p.id === id)?.name || '—'

  const cols = [
    { key: 'product_id',        label: 'Product',   render: v => prodName(v) },
    { key: 'from_warehouse_id', label: 'From',      render: v => whName(v) },
    { key: 'to_warehouse_id',   label: 'To',        render: v => whName(v) },
    { key: 'quantity',          label: 'Qty' },
    { key: 'status',            label: 'Status',    render: v => <span className="badge badge-green">{v}</span> },
    { key: 'created_at',        label: 'Date',      render: v => new Date(v).toLocaleDateString() },
  ]

  return (
    <>
      <Navbar title="Transfers" subtitle="Move stock between warehouses" />
      <div className="page-body">
        <div className="page-header">
          <div className="page-header-left"><h2>Internal Transfers</h2></div>
          <button className="btn btn-primary" onClick={() => setModal(true)}><Plus size={16} /> New Transfer</button>
        </div>
        <DataTable columns={cols} data={data} loading={loading} />

        {modal && (
          <Modal title="New Transfer" onClose={() => setModal(false)}>
            <form onSubmit={save}>
              {[['Product', 'product_id', products], ['From Warehouse', 'from_warehouse_id', warehouses], ['To Warehouse', 'to_warehouse_id', warehouses]].map(([label, key, opts]) => (
                <div className="form-group" key={key}>
                  <label className="form-label">{label}</label>
                  <select className="form-control" required value={form[key]} onChange={e => setForm({ ...form, [key]: e.target.value })}>
                    <option value="">Select…</option>
                    {opts.map(o => <option key={o.id} value={o.id}>{o.name}</option>)}
                  </select>
                </div>
              ))}
              <div className="form-group">
                <label className="form-label">Quantity</label>
                <input className="form-control" type="number" min={1} required value={form.quantity} onChange={e => setForm({ ...form, quantity: +e.target.value })} />
              </div>
              <div className="flex gap-2 justify-between mt-4">
                <button type="button" className="btn btn-ghost" onClick={() => setModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? 'Transferring…' : 'Execute Transfer'}</button>
              </div>
            </form>
          </Modal>
        )}
      </div>
    </>
  )
}
