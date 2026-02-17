'use client';

import { useState, useEffect } from 'react';

export default function Loader({ type = "default", text = "Loading Secured Data..." }) {
    const [stepIndex, setStepIndex] = useState(0);

    const stepMap = {
        dashboard: [
            "Syncing all Loan Records...",
            "Refreshing Geolocation Risk Map...",
            "Computing Portfolio Stress Metrics...",
            "Finalizing Executive Summary..."
        ],
        profile: [
            "Fetching Transaction Log...",
            "Analyzing Spending Velocity...",
            "Assessing Repayment Probability...",
            "Synthesizing AI Intervention..."
        ],
        alerts: [
            "Polishing Active Risk Triggers...",
            "Mapping Autonomous Interventions...",
            "Filtering Critical Stress Signals...",
            "Finalizing Command Center View..."
        ],
        monitor: [
            "Fetching Portfolio Distribution...",
            "Cross-Referencing Credit Files...",
            "Sorting by Risk Intensity...",
            "Updating Real-Time Feature Set..."
        ],
        default: [
            "Scanning Behavioral Patterns...",
            "Evaluating Financial Signals...",
            "Running Multi-Agent Ensemble...",
            "Generating Explainable Output..."
        ]
    };

    const steps = stepMap[type] || stepMap.default;

    useEffect(() => {
        const interval = setInterval(() => {
            setStepIndex((prev) => (prev + 1) % steps.length);
        }, 1200);
        return () => clearInterval(interval);
    }, [steps.length]);

    return (
        <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%',
            minHeight: '400px',
            color: 'var(--text-primary)',
            gap: '24px',
            background: 'rgba(255,255,255,0.02)',
            borderRadius: 'var(--radius-lg)',
            backdropFilter: 'blur(10px)'
        }}>
            {/* Title */}
            <h2 style={{
                margin: 0,
                fontSize: '22px',
                fontWeight: '800',
                letterSpacing: '-0.5px',
                color: 'var(--brand-primary)',
                textTransform: 'uppercase'
            }}>
                Pre-Delinquency Risk Engine
            </h2>

            {/* Spinner Container (Removed Rings & B) */}
            <div className="premium-loader" style={{ height: '20px' }}>
                {/* Logo removed */}
            </div>

            {/* Steps Container */}
            <div style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '8px',
                width: '300px'
            }}>
                {steps.map((step, idx) => (
                    <div key={idx} style={{
                        fontSize: '14px',
                        fontWeight: idx === stepIndex ? '700' : '400',
                        color: idx === stepIndex ? 'var(--text-primary)' : 'var(--text-muted)',
                        opacity: idx === stepIndex ? 1 : 0.4,
                        transition: 'all 0.4s ease',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '10px'
                    }}>
                        <div style={{
                            width: '6px',
                            height: '6px',
                            borderRadius: '50%',
                            background: idx === stepIndex ? 'var(--brand-primary)' : 'var(--border-light)',
                            boxShadow: idx === stepIndex ? '0 0 10px var(--brand-primary)' : 'none'
                        }}></div>
                        {step}
                    </div>
                ))}
            </div>

            {/* Bottom Status */}
            <div style={{
                fontSize: '11px',
                color: 'var(--brand-secondary)',
                fontWeight: '600',
                letterSpacing: '1px',
                textTransform: 'uppercase',
                animation: 'pulse 2s infinite'
            }}>
                Syncing Enterprise Data Lake
            </div>

            <style jsx>{`
                .premium-loader {
                    position: relative;
                    width: 70px;
                    display: flex;
                    alignItems: center;
                    justifyContent: center;
                }
                @keyframes spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
                @keyframes pulse {
                    0% { opacity: 0.4; }
                    50% { opacity: 1; }
                    100% { opacity: 0.4; }
                }
            `}</style>
        </div>
    );
}

