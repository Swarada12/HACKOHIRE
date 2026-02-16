'use client';

import { useState, useEffect } from 'react';
import { getDashboardStats } from '../lib/api';
import Link from 'next/link';

export default function AlertsPage() {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('All');
    const [statusFilter, setStatusFilter] = useState('All');

    useEffect(() => {
        async function fetchStats() {
            setLoading(true);
            const data = await getDashboardStats();
            if (data) {
                setStats(data);
            }
            setLoading(false);
        }
        fetchStats();
    }, []);

    if (loading) {
        return <div className="page-container"><div style={{ padding: '50px', textAlign: 'center' }}>Loading Live Alerts...</div></div>;
    }

    if (!stats) return <div className="page-container">Error loading real-time data. Check backend service.</div>;

    const { alerts, summary } = stats;

    const filtered = alerts.filter(a => {
        const matchSeverity = filter === 'All' || a.severity === filter;
        const matchStatus = statusFilter === 'All' || a.status === statusFilter;
        return matchSeverity && matchStatus;
    });

    const severityIcon = (sev) => {
        switch (sev) {
            case 'Critical': return '🚨';
            case 'High': return '⚠️';
            case 'Medium': return '📋';
            default: return 'ℹ️';
        }
    };

    return (
        <div className="page-container">
            <div className="page-header">
                <h1>Alerts & Interventions</h1>
                <p>Monitor risk signals and manage autonomous customer interventions (Enterprise Data Lake Monitoring)</p>
            </div>

            {/* Alert Stats */}
            <div className="metrics-grid animate-stagger">
                {[
                    { label: 'Total Alerts', value: alerts.length, color: 'blue', icon: '🔔' },
                    { label: 'Active', value: alerts.filter(a => a.status === 'active').length, color: 'red', icon: '🚨' },
                    { label: 'Pending', value: alerts.filter(a => a.status === 'pending').length, color: 'amber', icon: '⏳' },
                    { label: 'Resolved', value: 0, color: 'green', icon: '✅' },
                    { label: 'Auto-Triggered', value: summary.interventionsTriggered, color: 'purple', icon: '🤖' },
                ].map((s, i) => (
                    <div key={i} className={`metric-card ${s.color}`}>
                        <div className={`metric-icon ${s.color}`}><span style={{ fontSize: '20px' }}>{s.icon}</span></div>
                        <div className="metric-label">{s.label}</div>
                        <div className="metric-value">{s.value}</div>
                    </div>
                ))}
            </div>

            {/* Filters */}
            <div className="filter-bar" style={{ marginBottom: '8px' }}>
                <span style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-muted)', marginRight: '4px' }}>Severity:</span>
                {['All', 'Critical', 'High', 'Medium'].map(f => (
                    <button key={f} className={`filter-pill ${filter === f ? 'active' : ''}`} onClick={() => setFilter(f)}>
                        {f}
                    </button>
                ))}
            </div>
            <div className="filter-bar">
                <span style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-muted)', marginRight: '4px' }}>Status:</span>
                {['All', 'active', 'pending', 'resolved'].map(f => (
                    <button key={f} className={`filter-pill ${statusFilter === f ? 'active' : ''}`} onClick={() => setStatusFilter(f)}
                        style={{ textTransform: 'capitalize' }}>
                        {f}
                    </button>
                ))}
            </div>

            {/* Alert List */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }} className="animate-stagger">
                {filtered.map((alert) => (
                    <div key={alert.id} className={`alert-card ${alert.severity.toLowerCase()}`}>
                        <div className={`alert-severity-icon ${alert.severity.toLowerCase()}`}>
                            {severityIcon(alert.severity)}
                        </div>
                        <div className="alert-content">
                            <div className="alert-title">
                                {alert.type}
                                <span className={`alert-status-badge ${alert.status}`} style={{ marginLeft: '10px' }}>
                                    {alert.status}
                                </span>
                            </div>
                            <div className="alert-message">{alert.message}</div>
                            <div className="alert-meta">
                                <span>
                                    <Link href={`/customers/${alert.customerId}`} style={{ color: 'var(--brand-primary)', textDecoration: 'none', fontWeight: '600' }}>
                                        {alert.customerName}
                                    </Link>
                                    {' '}({alert.customerId})
                                </span>
                                <span>🕐 {new Date(alert.timestamp).toLocaleString()}</span>
                            </div>
                            <div style={{
                                marginTop: '10px', padding: '10px 14px',
                                background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-sm)',
                                fontSize: '13px', color: 'var(--text-secondary)',
                                border: '1px solid var(--border-light)',
                                display: 'flex', alignItems: 'center', gap: '8px'
                            }}>
                                <span style={{ fontWeight: '700', color: 'var(--brand-primary)', fontSize: '12px' }}>💡 SUGGESTED:</span>
                                {alert.suggestedAction}
                            </div>
                        </div>
                        <div className="alert-actions">
                            <button className="btn btn-primary btn-sm">Take Action</button>
                            <button className="btn btn-secondary btn-sm">Dismiss</button>
                        </div>
                    </div>
                ))}
            </div>

            {filtered.length === 0 && (
                <div className="card" style={{ textAlign: 'center', padding: '48px', marginTop: '16px' }}>
                    <div style={{ fontSize: '40px', marginBottom: '12px' }}>🎉</div>
                    <h3 style={{ color: 'var(--text-primary)', marginBottom: '4px' }}>No Alerts Found</h3>
                    <p style={{ color: 'var(--text-tertiary)', fontSize: '14px' }}>No alerts match the current filter criteria</p>
                </div>
            )}
        </div>
    );
}
