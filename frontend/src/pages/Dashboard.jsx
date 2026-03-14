import { useEffect, useState } from 'react'
import Navbar from '../components/Navbar'
import StatsCard from '../components/StatsCard'
import { dashboardApi } from '../api/client'
import { useNotifications } from '../context/NotificationContext'
import toast from 'react-hot-toast'
import {
  Package, AlertTriangle, XCircle, ArrowDownCircle,
  ArrowUpCircle, ArrowLeftRight, Bell, BoxesIcon
} from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts'

const COLORS = ['#4f8ef7', '#36d399', '#f87272', '#fbbd23', '#a855f7', '#22d3ee']
const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    return (
      <div style={{
        background: '#1a2035',
        border: '1px solid rgba(255,255,255,0.1)',
        padding: '8px 12px',
        borderRadius: '8px',
        fontSize: '13px',
        color: '#ffffff',
        boxShadow: '0 4px 20px rgba(0,0,0,0.4)',
        display: 'flex',
        gap: '6px'
      }}>
        <span style={{ fontWeight: 600 }}>{payload[0].name}:</span>
        <span>{payload[0].value}</span>
      </div>
    )
  }
  return null
}

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const { setAlerts } = useNotifications()

  useEffect(() => {
    dashboardApi.get()
      .then(res => {
        setData(res.data)
        setAlerts(res.data.active_alerts)
      })
      .catch(err => toast.error(err.message))
      .finally(() => setLoading(false))
  }, [])

  const barData = data ? [
    { name: 'Receipts',   pending: data.pending_receipts },
    { name: 'Deliveries', pending: data.pending_deliveries },
    { name: 'Transfers',  pending: data.pending_transfers },
  ] : []

  const pieData = data ? [
    { name: 'In Stock',      value: data.total_products - data.out_of_stock_count },
    { name: 'Low Stock',     value: data.low_stock_count },
    { name: 'Out of Stock',  value: data.out_of_stock_count },
  ] : []

  return (
    <>
      <Navbar title="Dashboard" subtitle="Welcome back — here's your inventory overview" />
      <div className="page-body">
        {loading ? (
          <div className="loading-center"><div className="spinner" /></div>
        ) : (
          <>
            <div className="stats-grid">
              <StatsCard label="Total Products"     value={data?.total_products}      icon={Package}          color="blue" />
              <StatsCard label="Total Stock Units"  value={data?.total_stock_value}   icon={BoxesIcon}        color="cyan" />
              <StatsCard label="Low Stock Items"    value={data?.low_stock_count}     icon={AlertTriangle}    color="yellow" />
              <StatsCard label="Out of Stock"       value={data?.out_of_stock_count}  icon={XCircle}          color="red" />
              <StatsCard label="Pending Receipts"   value={data?.pending_receipts}    icon={ArrowDownCircle}  color="green" />
              <StatsCard label="Pending Deliveries" value={data?.pending_deliveries}  icon={ArrowUpCircle}    color="purple" />
              <StatsCard label="Pending Transfers"  value={data?.pending_transfers}   icon={ArrowLeftRight}   color="blue" />
              <StatsCard label="Active Alerts"      value={data?.active_alerts}       icon={Bell}             color="red" />
            </div>

            <div className="charts-grid">
              <div className="chart-container">
                <div className="section-title">Pending Operations</div>
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={barData} barCategoryGap="40%">
                    <defs>
                      <linearGradient id="blueGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#4f8ef7" />
                        <stop offset="100%" stopColor="#2563eb" />
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="name" tick={{ fill: 'var(--text-muted)', fontSize: 12 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 12 }} axisLine={false} tickLine={false} />
                    <Tooltip
                      contentStyle={{ background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 10, fontSize: 13 }}
                      cursor={{ fill: 'rgba(255,255,255,0.03)' }}
                    />
                    <Bar dataKey="pending" fill="#4f8ef7" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="chart-container">
                <div className="section-title">Stock Health</div>
                <ResponsiveContainer width="100%" height={240}>
                  <PieChart>
                    <Pie 
                      data={pieData} 
                      cx="50%" 
                      cy="50%" 
                      innerRadius={60} 
                      outerRadius={90} 
                      paddingAngle={4} 
                      dataKey="value"
                      label={{ fill: 'var(--text-primary)', fontSize: 11 }}
                    >
                      {pieData.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}
                    </Pie>
                    <Tooltip content={<CustomTooltip />} />
                    <Legend iconType="circle" wrapperStyle={{ fontSize: 12, color: 'var(--text-primary)' }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </>
        )}
      </div>
    </>
  )
}
