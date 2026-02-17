'use client';

import { useState, useEffect } from 'react';
import { getCustomers, getDashboardStats } from '../lib/api';
import Link from 'next/link';
import Loader from '../components/Loader';

export default function AlertsPage() {
    const [alerts, setAlerts] = useState([]);
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('All');
    const [statusFilter, setStatusFilter] = useState('All');

    useEffect(() => {
        async function fetchData() {
            setLoading(true);

            // 1. Get Dashboard Stats for summary numbers
            const dashboardData = await getDashboardStats();
            setStats(dashboardData);

            // 2. Get Real Critical Customers to populate the Alerts List
            // We fetch Critical (and maybe High) to show as "Active Alerts"
            const criticalCustomers = await getCustomers('Critical');
            const highCustomers = await getCustomers('High');

            const rawAlerts = [
                ...(criticalCustomers.customers || []).map(c => ({
                    id: `ALT-${c.customer_id}`,
                    type: 'Risk Escalation',
                    severity: 'Critical',
                    status: 'active',
                    message: `Customer risk score escalated to ${c.risk_score} (Critical). Immediate intervention required.`,
                    timestamp: new Date().toISOString(),
                    customerId: c.customer_id,
                    customerName: c.name,
                    suggestedAction: c.suggested_action || 'Initiate Debt Restructuring / Call Customer'
                })),
                ...(highCustomers.customers || []).map(c => ({
                    id: `ALT-${c.customer_id}`,
                    type: 'Early Warning',
                    severity: 'High',
                    status: 'pending',
                    message: `Risk score increased to ${c.risk_score}. Monitor closely.`,
                    timestamp: new Date(Date.now() - 86400000).toISOString(),
                    customerId: c.customer_id,
                    customerName: c.name,
                    suggestedAction: c.suggested_action || 'Send Warning Notification / Temporary Limit Freeze'
                }))
            ];

            setAlerts(rawAlerts);
            setLoading(false);
        }
        fetchData();
    }, []);

    if (loading) {
        return <Loader type="alerts" text="Syncing Enterprise Alert System..." />;
    }

    // fallback if stats failed
    const summary = stats?.summary || { interventionsTriggered: 0 };

    // Calculate local stats from the fetched alerts
    const totalAlerts = alerts.length;
    const activeAlerts = alerts.filter(a => a.severity === 'Critical').length;
    const pendingAlerts = alerts.filter(a => a.severity === 'High').length;

    const filtered = alerts.filter(a => {
        const matchSeverity = filter === 'All' || a.severity === filter;
        // Map 'active' to Critical for simplicity in this view if needed, or just use status string
        // Actually, let's just filter by the status field we assigned
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
                    { label: 'Total Alerts', value: totalAlerts.toLocaleString(), color: 'blue', icon: '🔔' },
                    { label: 'Active (Critical)', value: activeAlerts.toLocaleString(), color: 'red', icon: '🚨' },
                    { label: 'Pending (High)', value: pendingAlerts.toLocaleString(), color: 'amber', icon: '⏳' },
                    { label: 'Resolved', value: 0, color: 'green', icon: '✅' },
                    { label: 'Auto-Triggered', value: (activeAlerts + pendingAlerts).toLocaleString(), color: 'purple', icon: '🤖' },
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
                    <div key={alert.id} className={`alert-card ${alert.severity.toLowerCase()} ${alert.status === 'resolved' ? 'resolved' : ''}`}>
                        <div className={`alert-severity-icon ${alert.severity.toLowerCase()}`}>
                            {alert.status === 'resolved' ? '✅' : severityIcon(alert.severity)}
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

                            {alert.status === 'resolved' ? (
                                <div style={{ marginTop: '10px', padding: '10px', background: '#ecfdf5', borderRadius: '4px', border: '1px solid #10b981', color: '#065f46', fontSize: '13px' }}>
                                    <strong>Successfully Intervened:</strong> {alert.suggestedAction} has been executed.
                                </div>
                            ) : (
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
                            )}
                        </div>
                        <div className="alert-actions">
                            {alert.status !== 'resolved' && (
                                <>
                                    <button
                                        className="btn btn-primary btn-sm"
                                        onClick={() => {
                                            const updated = alerts.map(a => a.id === alert.id ? { ...a, status: 'resolved' } : a);
                                            setAlerts(updated);
                                        }}
                                    >
                                        Take Action
                                    </button>
                                    <button
                                        className="btn btn-secondary btn-sm"
                                        onClick={() => {
                                            const updated = alerts.filter(a => a.id !== alert.id);
                                            setAlerts(updated);
                                        }}
                                    >
                                        Dismiss
                                    </button>
                                </>
                            )}
                            {alert.status === 'resolved' && (
                                <button
                                    className="btn btn-secondary btn-sm"
                                    onClick={() => {
                                        const updated = alerts.map(a => a.id === alert.id ? { ...a, status: a.severity === 'Critical' ? 'active' : 'pending' } : a);
                                        setAlerts(updated);
                                    }}
                                >
                                    Undo
                                </button>
                            )}
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
