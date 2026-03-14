import { useState, useEffect, useCallback, useMemo } from 'react'
import { useLocation } from 'react-router-dom'
import Navbar from '../components/Navbar'
import DataTable from '../components/DataTable'
import Modal from '../components/Modal'
import { deliveriesApi, productsApi, warehousesApi } from '../api/client'
import toast from 'react-hot-toast'
import { Plus, CheckCircle, Trash2 } from 'lucide-react'

export default function Deliveries() {
  const [data, setData] = useState([])
  const [products, setProducts] = useState([])
  const [warehouses, setWarehouses] = useState([])
  const [loading, setLoading] = useState(true)
  const [modal, setModal] = useState(false)
  const [form, setForm] = useState({ customer: '', items: [{ product_id: '', warehouse_id: '', quantity: 1 }] })
  const [saving, setSaving] = useState(false)

  const { search } = useLocation()
  const statusFilter = useMemo(() => new URLSearchParams(search).get('status'), [search])

  const fetch = useCallback(() => {
    setLoading(true)
    const params = { limit: 50 };
    if (statusFilter) params.status = statusFilter;
    Promise.all([deliveriesApi.list(params), productsApi.list({ limit: 200 }), warehousesApi.list({ limit: 100 })])
      .then(([d, p, w]) => { setData(d.data); setProducts(p.data); setWarehouses(w.data) })
      .catch(e => toast.error(e.message))
      .finally(() => setLoading(false))
  }, [statusFilter])
  useEffect(fetch, [fetch])

  const addLine = () => setForm({ ...form, items: [...form.items, { product_id: '', warehouse_id: '', quantity: 1 }] })
  const remLine = (i) => setForm({ ...form, items: form.items.filter((_, idx) => idx !== i) })
  const setLine = (i, k, v) => setForm({ ...form, items: form.items.map((it, idx) => idx === i ? { ...it, [k]: v } : it) })

  const save = async (e) => {
    e.preventDefault(); setSaving(true)
    try {
      await deliveriesApi.create(form); toast.success('Delivery order created')
      setModal(false); fetch()
    } catch (err) { toast.error(err.message) } finally { setSaving(false) }
  }

  const validate = async (id) => {
    try { await deliveriesApi.validate(id); toast.success('Delivery validated — stock deducted'); fetch() }
    catch (err) { toast.error(err.message) }
  }

  const statusColor = { draft: 'badge-yellow', packed: 'badge-blue', validated: 'badge-green' }

  const cols = [
    { key: 'customer',   label: 'Customer' },
    { key: 'status',     label: 'Status',  render: v => <span className={`badge ${statusColor[v]}`}>{v}</span> },
    { key: 'created_at', label: 'Created', render: v => new Date(v).toLocaleDateString() },
    { key: 'actions',    label: '',
      render: (_, row) => row.status !== 'validated' && (
        <button className="btn btn-success btn-sm" onClick={() => validate(row.id)}>
          <CheckCircle size={13} /> Validate
        </button>
      )
    },
  ]

  return (
    <>
      <Navbar title="Deliveries" subtitle="Outgoing shipments to customers" />
      <div className="page-body">
        <div className="page-header">
          <div className="page-header-left"><h2>Delivery Orders</h2></div>
          <button className="btn btn-primary" onClick={() => setModal(true)}><Plus size={16} /> New Delivery</button>
        </div>
        <DataTable columns={cols} data={data} loading={loading} />

        {modal && (
          <Modal title="New Delivery Order" onClose={() => setModal(false)} maxWidth="640px">
            <form onSubmit={save}>
              <div className="form-group">
                <label className="form-label">Customer Name</label>
                <input className="form-control" required value={form.customer} onChange={e => setForm({ ...form, customer: e.target.value })} />
              </div>
              <div className="section-title" style={{ marginBottom: 10 }}>Line Items</div>
              {form.items.map((item, i) => (
                <div key={i} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 80px 32px', gap: 8, marginBottom: 10, alignItems: 'end' }}>
                  <div>
                    <label className="form-label">Product</label>
                    <select className="form-control" required value={item.product_id} onChange={e => setLine(i, 'product_id', e.target.value)}>
                      <option value="">Select…</option>
                      {products.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="form-label">Warehouse</label>
                    <select className="form-control" required value={item.warehouse_id} onChange={e => setLine(i, 'warehouse_id', e.target.value)}>
                      <option value="">Select…</option>
                      {warehouses.map(w => <option key={w.id} value={w.id}>{w.name}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="form-label">Qty</label>
                    <input className="form-control" type="number" min={1} required value={item.quantity} onChange={e => setLine(i, 'quantity', +e.target.value)} />
                  </div>
                  <button type="button" className="btn btn-danger btn-icon" onClick={() => remLine(i)}><Trash2 size={13} /></button>
                </div>
              ))}
              <button type="button" className="btn btn-ghost btn-sm" onClick={addLine}><Plus size={13} /> Add Line</button>
              <hr className="divider" />
              <div className="flex gap-2 justify-between mt-4">
                <button type="button" className="btn btn-ghost" onClick={() => setModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? 'Creating…' : 'Create Delivery'}</button>
              </div>
            </form>
          </Modal>
        )}
      </div>
    </>
  )
}
