import { useState, useEffect, useCallback, useMemo } from 'react'
import { useLocation } from 'react-router-dom'
import Navbar from '../components/Navbar'
import DataTable from '../components/DataTable'
import Modal from '../components/Modal'
import { receiptsApi, productsApi, warehousesApi } from '../api/client'
import toast from 'react-hot-toast'
import { Plus, CheckCircle, Trash2 } from 'lucide-react'

export default function Receipts() {
  const [data, setData] = useState([])
  const [products, setProducts] = useState([])
  const [warehouses, setWarehouses] = useState([])
  const [loading, setLoading] = useState(true)
  const [modal, setModal] = useState(false)
  const [form, setForm] = useState({ supplier: '', items: [{ product_id: '', warehouse_id: '', quantity: 1 }] })
  const [saving, setSaving] = useState(false)
  
  const { search } = useLocation()
  const statusFilter = useMemo(() => new URLSearchParams(search).get('status'), [search])

  const fetch = useCallback(() => {
    setLoading(true)
    const params = { limit: 50 };
    if (statusFilter) params.status = statusFilter;
    Promise.all([receiptsApi.list(params), productsApi.list({ limit: 200 }), warehousesApi.list({ limit: 100 })])
      .then(([r, p, w]) => { setData(r.data); setProducts(p.data); setWarehouses(w.data) })
      .catch(e => toast.error(e.message))
      .finally(() => setLoading(false))
  }, [statusFilter])
  useEffect(fetch, [fetch])

  const addLine  = () => setForm({ ...form, items: [...form.items, { product_id: '', warehouse_id: '', quantity: 1 }] })
  const remLine  = (i) => setForm({ ...form, items: form.items.filter((_, idx) => idx !== i) })
  const setLine  = (i, k, v) => setForm({ ...form, items: form.items.map((it, idx) => idx === i ? { ...it, [k]: v } : it) })

  const save = async (e) => {
    e.preventDefault(); setSaving(true)
    try {
      await receiptsApi.create(form); toast.success('Receipt created')
      setModal(false); fetch()
    } catch (err) { toast.error(err.message) } finally { setSaving(false) }
  }

  const validate = async (id) => {
    try { await receiptsApi.validate(id); toast.success('Receipt validated — stock updated'); fetch() }
    catch (err) { toast.error(err.message) }
  }

  const statusBadge = (s) => (
    <span className={`badge ${s === 'validated' ? 'badge-green' : 'badge-yellow'}`}>{s}</span>
  )

  const cols = [
    { key: 'supplier',   label: 'Supplier' },
    { key: 'status',     label: 'Status',     render: v => statusBadge(v) },
    { key: 'created_at', label: 'Created',    render: v => new Date(v).toLocaleDateString() },
    { key: 'actions',    label: '',
      render: (_, row) => row.status === 'draft' && (
        <button className="btn btn-success btn-sm" onClick={() => validate(row.id)}>
          <CheckCircle size={13} /> Validate
        </button>
      )
    },
  ]

  return (
    <>
      <Navbar title="Receipts" subtitle="Incoming stock from suppliers" />
      <div className="page-body">
        <div className="page-header">
          <div className="page-header-left"><h2>Receipts</h2></div>
          <button className="btn btn-primary" onClick={() => setModal(true)}><Plus size={16} /> New Receipt</button>
        </div>
        <DataTable columns={cols} data={data} loading={loading} />

        {modal && (
          <Modal title="New Receipt" onClose={() => setModal(false)} maxWidth="640px">
            <form onSubmit={save}>
              <div className="form-group">
                <label className="form-label">Supplier Name</label>
                <input className="form-control" required value={form.supplier} onChange={e => setForm({ ...form, supplier: e.target.value })} />
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
                  <button type="button" className="btn btn-danger btn-icon" onClick={() => remLine(i)} style={{ marginBottom: 0 }}><Trash2 size={13} /></button>
                </div>
              ))}
              <button type="button" className="btn btn-ghost btn-sm" onClick={addLine}><Plus size={13} /> Add Line</button>
              <hr className="divider" />
              <div className="flex gap-2 justify-between mt-4">
                <button type="button" className="btn btn-ghost" onClick={() => setModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? 'Creating…' : 'Create Receipt'}</button>
              </div>
            </form>
          </Modal>
        )}
      </div>
    </>
  )
}
