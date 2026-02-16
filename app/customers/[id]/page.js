'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { analyzeCustomerRisk } from '../../lib/api';
import Link from 'next/link';

export default function CustomerDetailPage() {
    const { id } = useParams();
    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchAnalysis() {
            setLoading(true);
            const data = await analyzeCustomerRisk(id);
            if (data) setAnalysis(data);
            setLoading(false);
        }
        fetchAnalysis();
    }, [id]);

    if (loading) return <div className="page-container"><div style={{ padding: '100px', textAlign: 'center' }}>🧠 Running Multi-Agent Risk Ensemble...</div></div>;
    if (!analysis || analysis.error) return <div className="page-container">Error: {analysis?.error || 'Failed to load analysis'}</div>;

    const { customer_info, risk_analysis, decision_intelligence, intervention, explained_features } = analysis;

    return (
        <div className="page-container">
            <div className="page-header">
                <Link href="/customers" style={{ color: 'var(--brand-primary)', textDecoration: 'none', fontSize: '14px', fontWeight: '600' }}>← Back to Monitor</Link>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginTop: '12px' }}>
                    <div>
                        <h1>{customer_info.name}</h1>
                        <p style={{ color: 'var(--text-muted)' }}>Enterprise EWS ID: {customer_info.customer_id} | {customer_info.city} | {customer_info.product_type}</p>
                    </div>
                    <div className={`risk-badge ${risk_analysis.level.toLowerCase()}`} style={{ padding: '8px 16px', fontSize: '15px' }}>
                        {risk_analysis.level} RISK ({risk_analysis.score})
                    </div>
                </div>
            </div>

            <div className="charts-grid">
                {/* 1. Multi-Agent Ensemble Fusion */}
                <div className="card">
                    <div className="card-header">
                        <div className="card-title">🤖 Multi-Agent Ensemble Risk</div>
                        <div className="card-subtitle">Fusion of specialized risk agents</div>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                        <AgentScore label="Financial Risk Agent (XGBoost)" score={risk_analysis.agent_contributions.financial} color="#3b82f6" />
                        <AgentScore label="Behavioral Risk Agent" score={risk_analysis.agent_contributions.behavioral} color="#7c3aed" />
                        <AgentScore label="Trend & Velocity Agent (LSTM)" score={risk_analysis.agent_contributions.velocity} color="#ec4899" />

                        <div style={{ marginTop: '12px', padding: '12px', background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-light)' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                                <span style={{ fontSize: '12px', fontWeight: '700', color: 'var(--text-muted)' }}>ENSEMBLE CONFIDENCE</span>
                                <span style={{ fontSize: '12px', fontWeight: '800', color: 'var(--accent-emerald)' }}>{(risk_analysis.confidence * 100).toFixed(0)}%</span>
                            </div>
                            <div style={{ height: '6px', width: '100%', background: 'var(--border-light)', borderRadius: '3px', overflow: 'hidden' }}>
                                <div style={{ height: '100%', width: `${risk_analysis.confidence * 100}%`, background: 'var(--accent-emerald)' }}></div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* 2. Personalized Intervention Hub */}
                <div className="card">
                    <div className="card-header">
                        <div className="card-title">⚡ Personalized Intervention Engine</div>
                        <div className="card-subtitle">Channel-optimized relief actions</div>
                    </div>
                    <div style={{ padding: '16px', background: 'var(--brand-light)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--brand-primary-light)', marginBottom: '16px' }}>
                        <div style={{ fontWeight: '800', color: 'var(--brand-primary)', marginBottom: '4px' }}>RECOMMENDED OFFER:</div>
                        <div style={{ fontSize: '18px', fontWeight: '700', color: 'var(--text-primary)' }}>{intervention.recommended_offer}</div>
                    </div>
                    <div style={{ fontSize: '14px', color: 'var(--text-secondary)', fontStyle: 'italic', marginBottom: '20px', padding: '12px', background: 'var(--bg-secondary)', borderLeft: '4px solid var(--brand-primary)' }}>
                        "{intervention.message}"
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                        <div className="hero-stat" style={{ padding: '12px' }}>
                            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>CHANNEL</div>
                            <div style={{ fontSize: '13px', fontWeight: '700' }}>{intervention.channel}</div>
                        </div>
                        <div className="hero-stat" style={{ padding: '12px' }}>
                            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>TIMING</div>
                            <div style={{ fontSize: '13px', fontWeight: '700' }}>{intervention.timing_optimizer}</div>
                        </div>
                    </div>
                </div>

                {/* 3. Decision Intelligence & Context */}
                <div className="card">
                    <div className="card-header">
                        <div className="card-title">⚖️ Context & Decision Intelligence</div>
                        <div className="card-subtitle">Ability vs Willingness framework</div>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', textAlign: 'center' }}>
                        <div>
                            <div style={{ fontSize: '28px', fontWeight: '800', color: 'var(--brand-primary)' }}>{decision_intelligence.ability_score}%</div>
                            <div style={{ fontSize: '12px', fontWeight: '600', color: 'var(--text-muted)' }}>ABILITY TO PAY</div>
                        </div>
                        <div>
                            <div style={{ fontSize: '28px', fontWeight: '800', color: '#10b981' }}>{decision_intelligence.willingness_score}%</div>
                            <div style={{ fontSize: '12px', fontWeight: '600', color: 'var(--text-muted)' }}>WILLINGNESS TO PAY</div>
                        </div>
                    </div>
                    <div style={{ marginTop: '24px', padding: '16px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-light)', background: decision_intelligence.rare_case_detected ? '#fff7ed' : 'var(--bg-tertiary)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div>
                                <div style={{ fontSize: '13px', fontWeight: '700', color: decision_intelligence.rare_case_detected ? '#c2410c' : 'var(--text-primary)' }}>RARE CASE SOLVER</div>
                                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Outlier & exception handling</div>
                            </div>
                            <span style={{ fontSize: '12px', fontWeight: '800', color: decision_intelligence.rare_case_detected ? '#ea580c' : '#059669' }}>
                                {decision_intelligence.rare_case_detected ? '🚨 DETECTED' : '✅ NORMAL'}
                            </span>
                        </div>
                    </div>
                </div>

                {/* 4. Feature Engineering Deep Dive (Sample of 150+) */}
                <div className="card">
                    <div className="card-header">
                        <div className="card-title">🔬 Feature Intelligence (150+ Engineered)</div>
                        <div className="card-subtitle">Real-time indicators across F/B/T domains</div>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', maxHeight: '250px', overflowY: 'auto', paddingRight: '8px' }}>
                        {Object.entries(explained_features).map(([key, value]) => (
                            <div key={key} style={{ padding: '8px', background: 'var(--bg-tertiary)', borderRadius: '6px', border: '1px solid var(--border-light)' }}>
                                <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{key.replace(/_/g, ' ')}</div>
                                <div style={{ fontSize: '13px', fontWeight: '700', color: 'var(--text-primary)' }}>
                                    {typeof value === 'number' ?
                                        (value > 1000 ? `₹${(value / 1000).toFixed(1)}K` : value.toFixed(2))
                                        : value}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

            </div>
        </div>
    );
}

function AgentScore({ label, score, color }) {
    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-primary)' }}>{label}</span>
                <span style={{ fontSize: '13px', fontWeight: '800', color }}>{score}</span>
            </div>
            <div style={{ height: '8px', width: '100%', background: 'var(--border-light)', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${score}%`, background: color }}></div>
            </div>
        </div>
    );
}
