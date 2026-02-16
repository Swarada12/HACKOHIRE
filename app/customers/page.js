'use client';

import { useState, useMemo, useEffect } from 'react';
import { getCustomers } from '../lib/api';
import Link from 'next/link';

export default function CustomersPage() {
    const [customers, setCustomers] = useState([]);
    const [totalCount, setTotalCount] = useState(0);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [filter, setFilter] = useState('All');

    useEffect(() => {
        async function fetchData() {
            setLoading(true);
            const response = await getCustomers(); // { customers: [...], total: 10000 }
            const data = response.customers || [];

            // Map CSV data to UI model
            const mapped = data.map(c => {
                const delay = c.current_salary_delay_days || 0;

                return {
                    id: c.customer_id,
                    name: c.name,
                    productType: c.product_type || (c.loan_amount > 1000000 ? 'Home Loan' : 'Personal Loan'),
                    city: c.city || 'Mumbai',
                    riskScore: c.risk_score, // Provided by backend unified scoring
                    riskLevel: c.risk_level, // Provided by backend unified scoring
                    signals: delay > 0 ? [`Salary Delay (${delay}d)`] : [],
                    riskTrend: delay > 5 ? 'increasing' : 'stable',
                    lastActivity: '2 hours ago' // Mock
                };
            });
            setCustomers(mapped);
            setTotalCount(response.total || 0);
            setLoading(false);
        }
        fetchData();
    }, []);

    const filtered = useMemo(() => {
        return customers.filter(c => {
            const matchesSearch = !search ||
                c.name.toLowerCase().includes(search.toLowerCase()) ||
                c.id.toLowerCase().includes(search.toLowerCase()) ||
                c.city.toLowerCase().includes(search.toLowerCase());
            const matchesFilter = filter === 'All' || c.riskLevel === filter;
            return matchesSearch && matchesFilter;
        });
    }, [search, filter, customers]);

    const riskColor = (level) => {
        switch (level) {
            case 'Critical': return '#dc2626';
            case 'High': return '#ea580c';
            case 'Medium': return '#d97706';
            default: return '#059669';
        }
    };

    if (loading) {
        return <div className="page-container"><div style={{ padding: '50px', textAlign: 'center' }}>Syncing with Central Risk Data Lake...</div></div>;
    }

    return (
        <div className="page-container">
            <div className="page-header">
                <h1>Customer Risk Monitor</h1>
                <p>View and manage all monitored customers (Total: <b>{totalCount.toLocaleString()}</b>)</p>
            </div>

            {/* Summary Stats */}
            <div className="metrics-grid animate-stagger" style={{ marginBottom: '24px' }}>
                {[
                    { label: 'Total Monitored', value: totalCount.toLocaleString(), color: 'blue', icon: '👥' },
                    { label: 'Critical', value: customers.filter(c => c.riskLevel === 'Critical').length, color: 'red', icon: '🚨' },
                    { label: 'High Risk', value: customers.filter(c => c.riskLevel === 'High').length, color: 'amber', icon: '⚠️' },
                    { label: 'Low Risk', value: customers.filter(c => c.riskLevel === 'Low').length, color: 'green', icon: '✅' },
                ].map((s, i) => (
                    <div key={i} className={`metric-card ${s.color}`}>
                        <div className={`metric-icon ${s.color}`}><span style={{ fontSize: '20px' }}>{s.icon}</span></div>
                        <div className="metric-label">{s.label}</div>
                        <div className="metric-value">{s.value}</div>
                    </div>
                ))}
            </div>

            {/* Filters */}
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

            {/* Table */}
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
                                        <span className={`risk-badge ${c.riskLevel.toLowerCase()}`}>
                                            <span className="risk-dot" />
                                            {c.riskLevel}
                                        </span>
                                    </td>
                                    <td>
                                        <span style={{
                                            background: c.signals.length > 0 ? '#fee2e2' : '#d1fae5',
                                            color: c.signals.length > 0 ? '#dc2626' : '#059669',
                                            padding: '3px 10px', borderRadius: '12px', fontSize: '12px', fontWeight: '700'
                                        }}>
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
