'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { analyzeCustomerRisk, executeIntervention } from '../../lib/api';
import Link from 'next/link';
import Loader from '../../components/Loader';

// Explainability Modal Component
function ExplainerModal({ onClose, reasoning }) {
    // Fallback if reasoning is missing/loading
    const safeReasoning = reasoning || { financial: [], behavioral: [], velocity: [] };

    return (
        <div style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.7)', zIndex: 1000,
            display: 'flex', alignItems: 'center', justifyContent: 'center'
        }} onClick={onClose}>
            <div style={{
                backgroundColor: 'var(--bg-secondary)', width: '600px', maxWidth: '90%',
                borderRadius: 'var(--radius-md)', padding: '24px', position: 'relative',
                border: '1px solid var(--border-light)', boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)'
            }} onClick={e => e.stopPropagation()}>

                <h2 style={{ marginBottom: '16px', color: 'var(--text-primary)', borderBottom: '1px solid var(--border-light)', paddingBottom: '12px' }}>
                    🧠 Inside the Multi-Agent Brain
                </h2>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>

                    {/* Agent 1 */}
                    <div style={{ display: 'flex', gap: '12px' }}>
                        <div style={{ fontSize: '24px' }}>🏦</div>
                        <div style={{ flex: 1 }}>
                            <h3 style={{ fontSize: '15px', fontWeight: '700', color: '#3b82f6', marginBottom: '4px' }}>Financial Risk Agent (XGBoost)</h3>
                            <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '13px', color: 'var(--text-secondary)' }}>
                                {safeReasoning.financial && safeReasoning.financial.length > 0 ? (
                                    safeReasoning.financial.map((reason, i) => <li key={i}>{reason}</li>)
                                ) : (
                                    <li>Analysis pending...</li>
                                )}
                            </ul>
                        </div>
                    </div>

                    {/* Agent 2 */}
                    <div style={{ display: 'flex', gap: '12px' }}>
                        <div style={{ fontSize: '24px' }}>🃏</div>
                        <div style={{ flex: 1 }}>
                            <h3 style={{ fontSize: '15px', fontWeight: '700', color: '#7c3aed', marginBottom: '4px' }}>Behavioral Risk Agent</h3>
                            <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '13px', color: 'var(--text-secondary)' }}>
                                {safeReasoning.behavioral && safeReasoning.behavioral.length > 0 ? (
                                    safeReasoning.behavioral.map((reason, i) => <li key={i}>{reason}</li>)
                                ) : (
                                    <li>Analysis pending...</li>
                                )}
                            </ul>
                        </div>
                    </div>

                    {/* Agent 3 */}
                    <div style={{ display: 'flex', gap: '12px' }}>
                        <div style={{ fontSize: '24px' }}>📉</div>
                        <div style={{ flex: 1 }}>
                            <h3 style={{ fontSize: '15px', fontWeight: '700', color: '#ec4899', marginBottom: '4px' }}>Trend & Velocity Agent (LSTM)</h3>
                            <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '13px', color: 'var(--text-secondary)' }}>
                                {safeReasoning.velocity && safeReasoning.velocity.length > 0 ? (
                                    safeReasoning.velocity.map((reason, i) => <li key={i}>{reason}</li>)
                                ) : (
                                    <li>Analysis pending...</li>
                                )}
                            </ul>
                        </div>
                    </div>

                    <div style={{ padding: '12px', background: 'var(--bg-tertiary)', borderRadius: '6px', fontSize: '12px', color: 'var(--text-muted)' }}>
                        <strong>Ensemble Consensus:</strong> The final score is a weighted fusion: 50% Financial + 25% Behavioral + 25% Velocity.
                    </div>

                </div>

                <div style={{ marginTop: '24px', textAlign: 'right' }}>
                    <button
                        onClick={onClose}
                        style={{
                            padding: '8px 16px', borderRadius: '6px', border: 'none',
                            background: 'var(--brand-primary)', color: 'white', fontWeight: '600', cursor: 'pointer'
                        }}
                    >
                        Close Explanation
                    </button>
                </div>
            </div>
        </div>
    );
}

export default function CustomerDetailPage() {
    const { id } = useParams();
    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(true);
    const [showExplainer, setShowExplainer] = useState(false);

    useEffect(() => {
        async function fetchAnalysis() {
            setLoading(true);
            const data = await analyzeCustomerRisk(id);
            if (data) setAnalysis(data);
            setLoading(false);
        }
        fetchAnalysis();
    }, [id]);

    if (loading) return <Loader type="profile" text="Syncing Customer Data..." />;
    if (!analysis || analysis.error) return <div className="page-container"><div style={{ padding: '100px', textAlign: 'center', color: 'red' }}>Error: {analysis?.error || 'Failed to load analysis. Check backend service.'}</div></div>;

    const { customer_info, risk_analysis, decision_intelligence, intervention, explained_features } = analysis;

    return (
        <div className="page-container">
            {showExplainer && <ExplainerModal onClose={() => setShowExplainer(false)} reasoning={risk_analysis.agent_reasoning} />}

            <div className="page-header">
                <Link href="/customers" style={{ color: 'var(--brand-primary)', textDecoration: 'none', fontSize: '14px', fontWeight: '600' }}>← Back to Monitor</Link>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginTop: '12px' }}>
                    <div>
                        <h1>{customer_info.name}</h1>
                        <p style={{ color: 'var(--text-muted)' }}>Enterprise EWS ID: {customer_info.customer_id} | {customer_info.city} | {customer_info.product_type}</p>
                    </div>
                    <div className={`risk-badge ${risk_analysis.level.toLowerCase()}`} style={{ padding: '10px 20px', fontSize: '16px', borderRadius: '50px', boxShadow: '0 4px 12px rgba(0,0,0,0.1)', border: '2px solid white' }}>
                        ⚡ {risk_analysis.level.toUpperCase()} RISK SCORE: {risk_analysis.score}
                    </div>
                </div>
            </div>

            <div className="charts-grid">
                {/* 1. Multi-Agent Ensemble Fusion */}
                <div className="card" onClick={() => setShowExplainer(true)} style={{ cursor: 'pointer', transition: 'transform 0.2s', position: 'relative' }}>
                    <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                            <div className="card-title">🤖 Multi-Agent Ensemble Risk</div>
                            <div className="card-subtitle">Fusion of specialized risk agents</div>
                        </div>
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
                    {/* Hover effect hint */}
                    <div style={{ position: 'absolute', top: '10px', right: '10px', fontSize: '20px', opacity: 0.5 }}>👉</div>
                </div>

                {/* 2. Personalized Intervention Hub logic similar to before... */}
                {/* Keeping the rest of the cards structure identical but only showing up to Multi Agency for brevity in this replace block, need to ensure I don't delete others. */}
                {/* Re-writing the full return to be safe since I'm replacing the whole component logic */}

                {/* 2. Personalized Intervention Hub */}
                <div className="card">
                    <div className="card-header">
                        <div className="card-title">⚡ Personalized Intervention Engine</div>
                        <div className="card-subtitle">Channel-optimized relief actions</div>
                    </div>
                    {analysis.intervention_executed ? (
                        <div style={{
                            padding: '30px', textAlign: 'center', background: '#ecfdf5',
                            borderRadius: 'var(--radius-sm)', border: '1px solid #10b981'
                        }}>
                            <div style={{ fontSize: '40px', marginBottom: '12px' }}>✅</div>
                            <div style={{ fontSize: '18px', fontWeight: '800', color: '#065f46' }}>Action Executed</div>
                            <p style={{ fontSize: '14px', color: '#047857' }}>{intervention.recommended_offer} has been triggered via {intervention.channel}.</p>
                            <button
                                onClick={() => {
                                    const newAnalysis = { ...analysis };
                                    delete newAnalysis.intervention_executed;
                                    setAnalysis(newAnalysis);
                                }}
                                style={{ marginTop: '16px', padding: '6px 12px', background: 'transparent', border: '1px solid #10b981', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}
                            >
                                Undo Action (Mock)
                            </button>
                        </div>
                    ) : (
                        <>
                            <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '12px', marginBottom: '16px' }}>
                                <div style={{ padding: '16px', background: 'var(--brand-light)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--brand-primary-light)' }}>
                                    <div style={{ fontSize: '10px', fontWeight: '800', color: 'var(--brand-primary)', marginBottom: '4px', textTransform: 'uppercase' }}>Recommended Offer</div>
                                    <div style={{ fontSize: '16px', fontWeight: '700', color: 'var(--text-primary)' }}>{intervention.recommended_offer}</div>
                                </div>
                                <div style={{ padding: '16px', background: '#fef2f2', borderRadius: 'var(--radius-sm)', border: '1px solid #fee2e2' }}>
                                    <div style={{ fontSize: '10px', fontWeight: '800', color: '#991b1b', marginBottom: '4px', textTransform: 'uppercase' }}>Lead Stressor</div>
                                    <div style={{ fontSize: '16px', fontWeight: '700', color: '#dc2626' }}>🧠 {intervention.lead_stressor}</div>
                                </div>
                            </div>
                            <div style={{ fontSize: '14px', color: 'var(--text-secondary)', fontStyle: 'italic', marginBottom: '20px', padding: '16px', background: 'var(--bg-secondary)', borderLeft: '4px solid var(--brand-primary)', borderRadius: '0 4px 4px 0' }}>
                                "{intervention.message}"
                            </div>

                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '20px' }}>
                                <div className="hero-stat" style={{ padding: '12px' }}>
                                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>CHANNEL</div>
                                    <div style={{ fontSize: '13px', fontWeight: '700' }}>{intervention.channel}</div>
                                </div>
                                <div className="hero-stat" style={{ padding: '12px' }}>
                                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>TIMING</div>
                                    <div style={{ fontSize: '13px', fontWeight: '700' }}>{intervention.timing_optimizer}</div>
                                </div>
                            </div>

                            <div style={{ display: 'flex', gap: '12px' }}>
                                <button
                                    onClick={async () => {
                                        const result = await executeIntervention(id, intervention.offer_id);
                                        if (result && result.status === 'success') {
                                            setAnalysis({ ...analysis, intervention_executed: true });
                                        } else {
                                            alert("Failed to execute intervention. Please try again.");
                                        }
                                    }}
                                    style={{
                                        flex: 2, padding: '12px', background: 'var(--brand-primary)',
                                        color: 'white', border: 'none', borderRadius: 'var(--radius-sm)',
                                        fontWeight: '700', cursor: 'pointer', transition: 'filter 0.2s'
                                    }}
                                    onMouseOver={e => e.target.style.filter = 'brightness(1.1)'}
                                    onMouseOut={e => e.target.style.filter = 'none'}
                                >
                                    🚀 Execute Intervention
                                </button>
                                <button style={{
                                    flex: 1, padding: '12px', background: 'var(--bg-tertiary)',
                                    color: 'var(--text-muted)', border: '1px solid var(--border-light)',
                                    borderRadius: 'var(--radius-sm)', fontWeight: '600', cursor: 'pointer'
                                }}
                                    onClick={() => alert("Intervention declined.")}
                                >
                                    Decline
                                </button>
                            </div>
                        </>
                    )}
                </div>

                {/* 3. Decision Intelligence & Context */}
                <div className="card">
                    <div className="card-header">
                        <div className="card-title">⚖️ Context & Decision Intel</div>
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
                                <div style={{ fontSize: '13px', fontWeight: '700', color: decision_intelligence.rare_case_detected ? '#c2410c' : 'var(--text-primary)' }}>
                                    {decision_intelligence.case_type || 'RARE CASE SOLVER'}
                                </div>
                                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Outlier & exception handling</div>
                            </div>
                            <span style={{ fontSize: '12px', fontWeight: '800', color: decision_intelligence.rare_case_detected ? '#ea580c' : '#059669' }}>
                                {decision_intelligence.rare_case_detected ? '🚨 DETECTED' : '✅ NORMAL'}
                            </span>
                        </div>
                    </div>
                </div>

                {/* 4. Loan & Repayment Insights */}
                <div className="card">
                    <div className="card-header">
                        <div className="card-title">💸 Loan & Repayment Insights</div>
                        <div className="card-subtitle">AI-Predicted Repayment Behavior</div>
                    </div>
                    {analysis.repayment_stats ? (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                            {/* Loan Progress */}
                            <div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                                    <span style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-primary)' }}>Total Repaid vs Loan</span>
                                    <span style={{ fontSize: '13px', fontWeight: '800', color: 'var(--brand-primary)' }}>
                                        {analysis.repayment_stats.repayment_progress}%
                                    </span>
                                </div>
                                <div style={{ height: '8px', width: '100%', background: 'var(--border-light)', borderRadius: '4px', overflow: 'hidden' }}>
                                    <div style={{ height: '100%', width: `${analysis.repayment_stats.repayment_progress}%`, background: 'var(--brand-primary)' }}></div>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4px', fontSize: '11px', color: 'var(--text-muted)' }}>
                                    <span>Paid: ₹{(analysis.repayment_stats.total_repaid / 100000).toFixed(2)}L</span>
                                    <span>Total: ₹{(analysis.repayment_stats.total_loan_amount / 100000).toFixed(2)}L</span>
                                </div>
                            </div>

                            {/* AI Prediction */}
                            <div style={{ padding: '12px', background: 'var(--bg-tertiary)', borderRadius: '6px', border: '1px solid var(--border-light)' }}>
                                <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Next EMI Prediction</div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '4px' }}>
                                    <div style={{ fontSize: '20px', fontWeight: '800', color: analysis.repayment_stats.emi_probability > 80 ? '#059669' : '#dc2626' }}>
                                        {analysis.repayment_stats.emi_probability}%
                                    </div>
                                    <div style={{ textAlign: 'right' }}>
                                        <div style={{ fontSize: '13px', fontWeight: '700', color: 'var(--text-primary)' }}>{analysis.repayment_stats.status}</div>
                                        <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Due: {analysis.repayment_stats.next_emi_date}</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-muted)' }}>Loading Repayment Data...</div>
                    )}
                </div>

                {/* 4. Feature Engineering Deep Dive (Sample of 150+) */}
                <div className="card">
                    <div className="card-header">
                        <div className="card-title">🔬 Feature Intelligence</div>
                        <div className="card-subtitle">Real-time indicators across F/B/T domains</div>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', maxHeight: '250px', overflowY: 'auto', paddingRight: '8px' }}>
                        {Object.entries(explained_features).map(([key, value]) => {
                            const isRT = key.startsWith('rt_') || key.startsWith('b_');
                            return (
                                <div key={key} style={{
                                    padding: '8px',
                                    background: isRT ? '#eff6ff' : 'var(--bg-tertiary)',
                                    borderRadius: '6px',
                                    border: isRT ? '1px solid #bfdbfe' : '1px solid var(--border-light)'
                                }}>
                                    <div style={{ fontSize: '10px', color: isRT ? '#1e40af' : 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: isRT ? '700' : '400' }}>
                                        {isRT && '⚡ '}{key.replace(/_/g, ' ')}
                                    </div>
                                    <div style={{ fontSize: '13px', fontWeight: '700', color: 'var(--text-primary)' }}>
                                        {typeof value === 'number' ?
                                            (value > 1000 ? `₹${(value / 1000).toFixed(1)}K` : value.toFixed(2))
                                            : value}
                                    </div>
                                </div>
                            );
                        })}
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
