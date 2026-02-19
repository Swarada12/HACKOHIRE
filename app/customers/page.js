'use client';

import { useState, useMemo, useEffect } from 'react';
import { getCustomers } from '../lib/api';
import Link from 'next/link';
import Loader from '../components/Loader';

export default function CustomersPage() {
    const [customers, setCustomers] = useState([]);
    const [totalCount, setTotalCount] = useState(0);
    const [stats, setStats] = useState({ total: 0, critical: 0, high: 0, medium: 0, low: 0 });
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [filter, setFilter] = useState('All');
    const [inspectSignals, setInspectSignals] = useState(null);

    useEffect(() => {
        async function fetchData() {
            setLoading(true);
            const response = await getCustomers(filter);
            const data = response.customers || [];

            let mapped = (data || []).map(c => {
                const delay = c.current_salary_delay_days || 0;

                // Signals now come from the ML model's agent_reasoning
                const sigs = c.signals || [];

                return {
                    id: c.customer_id,
                    name: c.name,
                    productType: c.product_type || (c.loan_amount > 1000000 ? 'Home Loan' : 'Personal Loan'),
                    city: c.city || 'Mumbai',
                    riskScore: Math.round(c.risk_score || 0),
                    riskLevel: c.risk_level || 'Unclassified',
                    signals: sigs,
                    agentScores: c.agent_scores || null,
                    riskTrend: delay > 5 ? 'increasing' : 'stable',
                    lastActivity: 'STABLE'
                };
            });

            if (filter === 'All') {
                mapped.sort((a, b) => a.id.localeCompare(b.id, undefined, { numeric: true, sensitivity: 'base' }));
            }

            setCustomers(mapped);
            setTotalCount(response.total || 0);

            if (response.stats) {
                setStats({
                    total: response.stats.total,
                    critical: response.stats.critical,
                    high: response.stats.high,
                    medium: response.stats.medium,
                    low: response.stats.low
                });
            }

            setLoading(false);
        }
        fetchData();
    }, [filter]);

    const filtered = useMemo(() => {
        return customers.filter(c => {
            const matchesSearch = !search ||
                (c.name || "").toLowerCase().includes(search.toLowerCase()) ||
                (c.id || "").toLowerCase().includes(search.toLowerCase()) ||
                (c.city || "").toLowerCase().includes(search.toLowerCase());
            return matchesSearch;
        });
    }, [search, customers]);

    const riskColor = (level) => {
        switch (level) {
            case 'Critical': return '#dc2626';
            case 'High': return '#ea580c';
            case 'Medium': return '#d97706';
            default: return '#059669';
        }
    };

    if (loading) return <Loader type="monitor" text="Syncing Portfolio Data..." />;

    return (
        <div className="page-container">
            {/* Signal Details Modal */}
            {inspectSignals && (
                <div style={{
                    position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
                    backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 2000,
                    display: 'flex', alignItems: 'center', justifyContent: 'center'
                }} onClick={() => setInspectSignals(null)}>
                    <div style={{
                        backgroundColor: 'white', padding: '24px', borderRadius: '12px',
                        width: '380px', boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
                        border: '1px solid var(--border-light)'
                    }} onClick={e => e.stopPropagation()}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                            <h3 style={{ margin: 0, fontSize: '16px', fontWeight: '800' }}>🧠 ML Model Signals</h3>
                            <button onClick={() => setInspectSignals(null)} style={{ border: 'none', background: 'none', cursor: 'pointer', fontSize: '18px' }}>✕</button>
                        </div>
                        <div style={{ marginBottom: '12px', padding: '8px 12px', background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '6px', fontSize: '11px', color: '#166534', fontWeight: '600' }}>
                            Source: XGBoost + LightGBM + LSTM Ensemble
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                            {inspectSignals.map((s, i) => (
                                <div key={i} style={{
                                    padding: '10px', background: '#fef2f2', border: '1px solid #fee2e2',
                                    borderRadius: '6px', color: '#991b1b', fontSize: '12px', fontWeight: '600'
                                }}>
                                    {s}
                                </div>
                            ))}
                            {inspectSignals.length === 0 && (
                                <div style={{ padding: '10px', background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '6px', color: '#166534', fontSize: '12px', fontWeight: '600' }}>
                                    ✅ All models indicate stable profile
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}

            <div className="page-header">
                <h1>Customer Risk Monitor</h1>
                <p>View and manage all monitored customers (Total: <b>{totalCount.toLocaleString()}</b>)</p>
            </div>
            {/* ... Summary Stats and Filters ... */}
            <div className="metrics-grid animate-stagger" style={{ marginBottom: '24px' }}>
                {[
                    { label: 'Total Monitored', value: stats.total.toLocaleString(), color: 'blue', icon: '👥' },
                    { label: 'Critical', value: stats.critical.toLocaleString(), color: 'red', icon: '🚨' },
                    { label: 'High Risk', value: stats.high.toLocaleString(), color: 'amber', icon: '⚠️' },
                    { label: 'Medium Risk', value: stats.medium.toLocaleString(), color: 'orange', icon: '📊' },
                    { label: 'Low Risk', value: stats.low.toLocaleString(), color: 'green', icon: '✅' },
                ].map((s, i) => (
                    <div key={i} className={`metric-card ${s.color}`}>
                        <div className={`metric-icon ${s.color}`}><span style={{ fontSize: '20px' }}>{s.icon}</span></div>
                        <div className="metric-label">{s.label}</div>
                        <div className="metric-value">{s.value}</div>
                    </div>
                ))}
            </div>

            <div className="filter-bar">
                <div className="search-wrapper">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
                    </svg>
                    <input
                        type="text"
                        className="search-input"
                        placeholder="Search by name, ID..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                </div>
                {['All', 'Critical', 'High', 'Medium', 'Low'].map(f => (
                    <button key={f} className={`filter-pill ${filter === f ? 'active' : ''}`} onClick={() => setFilter(f)}>
                        {f}
                    </button>
                ))}
            </div>

            <div className="card" style={{ padding: 0 }}>
                <div className="table-container">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Customer</th>
                                <th>ID</th>
                                <th>Product</th>
                                <th>City</th>
                                <th>Risk Score</th>
                                <th>Risk Level</th>
                                <th>Signals</th>
                                <th>Trend</th>
                                <th>Last Activity</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filtered.map((c) => (
                                <tr key={c.id}>
                                    <td>
                                        <Link href={`/customers/${c.id}`} style={{ textDecoration: 'none', color: 'var(--text-primary)', fontWeight: '600', fontSize: '14px' }}>
                                            {c.name}
                                        </Link>
                                    </td>
                                    <td style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '12px', color: 'var(--text-muted)' }}>{c.id}</td>
                                    <td>{c.productType}</td>
                                    <td>{c.city}</td>
                                    <td>
                                        <div className="risk-score-bar">
                                            <span className="risk-score-number" style={{ color: riskColor(c.riskLevel) }}>{c.riskScore}</span>
                                            <div className="risk-bar-track">
                                                <div className="risk-bar-fill" style={{
                                                    width: `${c.riskScore}%`,
                                                    background: riskColor(c.riskLevel)
                                                }} />
                                            </div>
                                        </div>
                                    </td>
                                    <td>
                                        <span className={`risk-badge ${(c.riskLevel || 'unclassified').toLowerCase()}`}>
                                            <span className="risk-dot" />
                                            {c.riskLevel || 'Unclassified'}
                                        </span>
                                    </td>
                                    <td>
                                        <span
                                            onClick={() => c.signals.length > 0 && setInspectSignals(c.signals)}
                                            style={{
                                                background: c.signals.length > 0 ? '#fee2e2' : '#d1fae5',
                                                color: c.signals.length > 0 ? '#dc2626' : '#059669',
                                                padding: '3px 10px', borderRadius: '12px', fontSize: '12px', fontWeight: '700',
                                                cursor: c.signals.length > 0 ? 'help' : 'default',
                                                border: c.signals.length > 0 ? '1px solid #fecaca' : 'none'
                                            }}
                                        >
                                            {c.signals.length} signals
                                        </span>
                                    </td>
                                    <td>
                                        <span style={{
                                            fontSize: '12px', fontWeight: '600',
                                            color: c.riskTrend === 'increasing' ? '#dc2626' : c.riskTrend === 'decreasing' ? '#059669' : '#9498b0'
                                        }}>
                                            {c.riskTrend === 'increasing' ? '↑ Rising' : c.riskTrend === 'decreasing' ? '↓ Falling' : '→ Stable'}
                                        </span>
                                    </td>
                                    <td style={{ fontSize: '13px', color: 'var(--text-muted)' }}>{c.lastActivity}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            <div style={{ textAlign: 'center', padding: '16px', fontSize: '13px', color: 'var(--text-muted)' }}>
                Showing {filtered.length} of {totalCount.toLocaleString()} customers
            </div>
        </div>
    );
}
