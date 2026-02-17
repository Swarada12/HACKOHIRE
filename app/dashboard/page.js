'use client';

import { useState, useEffect } from 'react';
import {
    PieChart, Pie, Cell, ResponsiveContainer,
    XAxis, YAxis, Tooltip, CartesianGrid, BarChart, Bar, Area, AreaChart
} from 'recharts';
import { getDashboardStats } from '../lib/api';
import Link from 'next/link';

import Loader from '../components/Loader';

export default function DashboardPage() {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchStats() {
            setLoading(true);
            const data = await getDashboardStats();
            if (data) setStats(data);
            setLoading(false);
        }
        fetchStats();
    }, []);

    if (loading) return <Loader type="dashboard" text="Aggregating Enterprise Data..." />;
    if (!stats) return <div className="page-container"><div style={{ padding: '100px', textAlign: 'center', color: 'red' }}>Error: Could not fetch dashboard statistics. Please ensure the backend is running.</div></div>;

    const { summary, riskDistribution, geoRisk, productHealth, riskTrend } = stats;

    return (
        <div className="page-container">
            <div className="page-header">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                    <div>
                        <h1>Enterprise Risk Dashboard</h1>
                        <p>Multi-Agent Ensemble Monitoring (Sources: <b>Multi-Source Data Lake</b>)</p>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: '12px', fontWeight: '700', color: 'var(--accent-emerald)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                            <span className="pulsing-dot"></span> LIVE STREAM
                        </div>
                        <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Last Updated: {summary.lastUpdated}</div>
                    </div>
                </div>
            </div>

            {/* Metric Cards - Shifted to Ensemble Logic */}
            <div className="metrics-grid animate-stagger">
                <MetricCard color="blue" icon="👥" label="Portfolio Registry" value={summary.totalCustomers.toLocaleString()} change="Enterprise" positive />
                <MetricCard color="red" icon="🤖" label="Ensemble High-Risk" value={summary.criticalRisk} change="+5%" positive={false} />
                <MetricCard color="purple" icon="🧠" label="Decision Interventions" value={summary.interventionsTriggered.toLocaleString()} change="Automated" positive />
                <MetricCard color="amber" icon="🚨" label="Governance Alerts" value={summary.activeAlerts.toLocaleString()} change="Low Conf" positive={false} />
                <MetricCard color="green" icon="💰" label="Est. Avoided Loss" value={summary.costSavings} change="Q1 Target" positive />
            </div>

            <div className="charts-grid">
                {/* 1. Risk Distribution (Global Ensemble) */}
                <div className="card">
                    <div className="card-header">
                        <div className="card-title">📊 Global Risk Distribution</div>
                        <div className="card-subtitle">Ensemble Fusion Results</div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '32px' }}>
                        <ResponsiveContainer width="50%" height={220}>
                            <PieChart>
                                <Pie data={riskDistribution} cx="50%" cy="50%" innerRadius={55} outerRadius={85} paddingAngle={4} dataKey="value">
                                    {riskDistribution.map((entry, i) => (
                                        <Cell key={i} fill={entry.color} />
                                    ))}
                                </Pie>
                                <Tooltip />
                            </PieChart>
                        </ResponsiveContainer>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                            {riskDistribution.map((item, i) => (
                                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                    <div style={{ width: '12px', height: '12px', borderRadius: '3px', background: item.color }} />
                                    <span style={{ fontSize: '12px', color: 'var(--text-secondary)', minWidth: '60px' }}>{item.name}</span>
                                    <span style={{ fontSize: '14px', fontWeight: '800', color: 'var(--text-primary)' }}>{item.value.toLocaleString()}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* 2. Model Accuracy/Trend */}
                <div className="card">
                    <div className="card-header">
                        <div className="card-title">📈 Risk Velocity Trend</div>
                        <div className="card-subtitle">Aggregated Portfolio Stress</div>
                    </div>
                    <ResponsiveContainer width="100%" height={220}>
                        <AreaChart data={riskTrend}>
                            <defs>
                                <linearGradient id="riskGrad" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.15} />
                                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#e2e5f0" />
                            <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#9498b0' }} tickLine={false} axisLine={{ stroke: '#e2e5f0' }} />
                            <YAxis tick={{ fontSize: 11, fill: '#9498b0' }} tickLine={false} axisLine={false} domain={[0, 100]} />
                            <Tooltip />
                            <Area type="monotone" dataKey="avgRiskScore" stroke="#3b82f6" strokeWidth={2.5} fill="url(#riskGrad)" />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>

                {/* 3. Product Delinquency Exposure */}
                <div className="card">
                    <div className="card-header">
                        <div className="card-title">🏦 Portfolio Exposure by Product</div>
                        <div className="card-subtitle">Active risk concentration %</div>
                    </div>
                    <ResponsiveContainer width="100%" height={240}>
                        <BarChart data={productHealth} barCategoryGap="20%">
                            <CartesianGrid strokeDasharray="3 3" stroke="#e2e5f0" />
                            <XAxis dataKey="productFull" tick={{ fontSize: 10, fill: '#9498b0' }} tickLine={false} axisLine={{ stroke: '#e2e5f0' }} />
                            <YAxis tick={{ fontSize: 11, fill: '#9498b0' }} tickLine={false} axisLine={false} />
                            <Tooltip />
                            <Bar dataKey="delinquencyRate" name="Exposure %" fill="#7c3aed" radius={[6, 6, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>

                {/* 4. Geographic Risk Concentration */}
                <div className="card full-width">
                    <div className="card-header">
                        <div className="card-title">🗺️ Regional Risk Concentration</div>
                        <div className="card-subtitle">Multi-source geographic telemetry</div>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '14px' }}>
                        {geoRisk.map((g, i) => {
                            const color = g.riskIndex >= 65 ? '#dc2626' : g.riskIndex >= 50 ? '#ea580c' : g.riskIndex >= 40 ? '#d97706' : '#059669';
                            return (
                                <div key={i} style={{ padding: '16px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-light)', background: 'var(--bg-secondary)', textAlign: 'center' }}>
                                    <div style={{ fontSize: '24px', fontWeight: '800', color, marginBottom: '2px' }}>{g.riskIndex}</div>
                                    <div style={{ fontSize: '13px', fontWeight: '700', color: 'var(--text-primary)' }}>{g.region}</div>
                                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{g.critical} critical cases</div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
}

function MetricCard({ color, icon, label, value, change, positive }) {
    return (
        <div className={`metric-card ${color}`}>
            <div className={`metric-icon ${color}`}>
                <span style={{ fontSize: '20px' }}>{icon}</span>
            </div>
            <div className="metric-label">{label}</div>
            <div className="metric-value">{value}</div>
            <div className={`metric-change ${positive ? 'positive' : 'negative'}`}>
                {change}
            </div>
        </div>
    );
}
