'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getDashboardStats } from './lib/api';

export default function HomePage() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    async function fetchStats() {
      const data = await getDashboardStats();
      if (data) setStats(data);
    }
    fetchStats();
  }, []);

  const features = [
    { icon: '🛰️', title: 'Multi-Source Telemetry', desc: 'Ingestion from Core Banking, App Activity, Payment History, and Salary Credit streams into a unified feature store.', color: '#dbeafe' },
    { icon: '🧬', title: '150+ Engineered Features', desc: 'Continuous computation of Financial, Behavioral, and Temporal features for a 360-degree customer view.', color: '#ede9fe' },
    { icon: '🤖', title: 'Multi-Agent ML Ensemble', desc: 'Specialized XGBoost, Behavioral Agents, and Velocity LSTMs fused with confidence-weighted decision scoring.', color: '#fef3c7' },
    { icon: '⚖️', title: 'Decision Intelligence', desc: 'Rare Case solvers and Ability-vs-Willingness scoring ensure governance and precise risk classification.', color: '#d1fae5' },
    { icon: '🤝', title: 'Intervention Engine', desc: 'Channel-optimized proactive outreach and personalized relief recommendations generated in real-time.', color: '#fee2e2' },
    { icon: '🔐', title: 'Enterprise Explainability', desc: 'SHAP-based root cause analysis and NLP-driven explanations for auditable, transparent decision-making.', color: '#e0e7ff' },
  ];

  return (
    <div className="page-container">
      {/* Hero Section */}
      <section className="hero-section animate-fade-in">
        <div style={{
          display: 'inline-block', padding: '6px 16px', borderRadius: '20px',
          background: 'var(--brand-light)', color: 'var(--brand-primary)',
          fontSize: '13px', fontWeight: '700', marginBottom: '20px',
          letterSpacing: '0.5px'
        }}>
          🛡️ ENTERPRISE EARLY WARNING SYSTEM (EWS-360)
        </div>
        <h1>
          Next-Gen Proactive<br />
          <span className="highlight">Risk Intelligence Platform</span>
        </h1>
        <p className="subtitle">
          A production-grade multi-agent ML infrastructure that monitors billions of data points across
          core banking and behavioral streams to prevent delinquency and preserve customer trust.
        </p>
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', marginBottom: '40px' }}>
          <Link href="/dashboard" className="btn btn-primary" style={{ padding: '12px 28px', fontSize: '15px' }}>
            Enterprise Dashboard →
          </Link>
          <Link href="/customers" className="btn btn-secondary" style={{ padding: '12px 28px', fontSize: '15px' }}>
            Customer Risk Monitor
          </Link>
        </div>
      </section>

      {/* Key Metrics */}
      <div className="hero-stats animate-stagger">
        <div className="hero-stat">
          <div className="hero-stat-value blue">150+</div>
          <div className="hero-stat-label">Engineered Features</div>
        </div>
        <div className="hero-stat">
          <div className="hero-stat-value green">Ensemble</div>
          <div className="hero-stat-label">ML Architecture</div>
        </div>
        <div className="hero-stat">
          <div className="hero-stat-value amber">{stats ? stats.summary.costSavings : <span style={{ fontSize: '18px', opacity: 0.7 }}>Loading...</span>}</div>
          <div className="hero-stat-label">Estimated Avoided Loss</div>
        </div>
        <div className="hero-stat">
          <div className="hero-stat-value purple">{stats ? stats.summary.totalCustomers.toLocaleString() : <span style={{ fontSize: '18px', opacity: 0.7 }}>Loading...</span>}</div>
          <div className="hero-stat-label">Accounts Monitored</div>
        </div>
      </div>

      {/* Features */}
      <div style={{ textAlign: 'center', marginTop: '48px', marginBottom: '16px' }}>
        <h2 style={{ fontSize: '28px', fontWeight: '800', color: 'var(--text-primary)' }}>
          System Capabilities
        </h2>
        <p style={{ color: 'var(--text-tertiary)', maxWidth: '500px', margin: '8px auto 0' }}>
          End-to-end autonomous pipeline from raw data to proactive intervention
        </p>
      </div>
      <div className="features-grid animate-stagger">
        {features.map((f, i) => (
          <div key={i} className="feature-card">
            <div className="feature-icon" style={{ background: f.color }}>{f.icon}</div>
            <h3>{f.title}</h3>
            <p>{f.desc}</p>
          </div>
        ))}
      </div>

      {/* CTA */}
      <div style={{
        textAlign: 'center', padding: '48px 0', marginTop: '48px',
        background: 'linear-gradient(135deg, var(--brand-light), var(--accent-purple-light))',
        borderRadius: 'var(--radius-xl)', border: '1px solid var(--border-light)'
      }}>
        <h2 style={{ fontSize: '24px', fontWeight: '800', marginBottom: '8px', color: 'var(--text-primary)' }}>
          Advance to Proactive Collections
        </h2>
        <p style={{ color: 'var(--text-tertiary)', marginBottom: '24px', maxWidth: '400px', margin: '0 auto 24px' }}>
          Launch the dashboard to monitor live portfolio stress and autonomous interventions.
        </p>
        <Link href="/dashboard" className="btn btn-primary" style={{ padding: '14px 36px', fontSize: '15px' }}>
          Explore Enterprise Dashboard →
        </Link>
      </div>
    </div>
  );
}
