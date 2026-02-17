'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState, useEffect } from 'react';
import { getDashboardStats } from '../lib/api';

export default function Sidebar() {
    const pathname = usePathname();
    const [stats, setStats] = useState({ critical: 0, high: 0 });

    useEffect(() => {
        async function fetchStats() {
            try {
                const data = await getDashboardStats();
                if (data && data.summary) {
                    // Find High Risk count from distribution
                    const highRisk = data.riskDistribution?.find(d => d.name === 'High')?.value || 0;
                    setStats({
                        critical: data.summary.criticalRisk,
                        high: highRisk // Use raw High Risk count for Pending
                    });
                }
            } catch (e) {
                console.error("Sidebar Stats Error", e);
            }
        }
        fetchStats();
        const interval = setInterval(fetchStats, 30000); // Poll every 30s
        return () => clearInterval(interval);
    }, []);

    const navItems = [
        {
            section: 'Overview',
            items: [
                { href: '/', label: 'Overview', icon: HomeIcon },
                { href: '/dashboard', label: 'Enterprise Dashboard', icon: DashboardIcon },
            ]
        },
        {
            section: 'Operations',
            items: [
                { href: '/customers', label: 'Customer Risk Monitor', icon: UsersIcon },
                {
                    href: '/alerts',
                    label: 'Intervention Hub',
                    icon: AlertIcon,
                    customBadge: stats.critical > 0 ? (
                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', lineHeight: '1.2' }}>
                            <span style={{ fontSize: '10px', color: '#dc2626', fontWeight: '700' }}>Active: {stats.critical}</span>
                            <span style={{ fontSize: '10px', color: '#d97706', fontWeight: '600' }}>Pending: {stats.high}</span>
                        </div>
                    ) : null
                },
            ]
        },

    ];

    return (
        <aside className="sidebar">
            <div className="sidebar-header">
                <div className="sidebar-logo">P</div>
                <div className="sidebar-brand">
                    <h2>Praeventix EWS</h2>
                    <span>Early Warning System</span>
                </div>
            </div>
            <nav className="sidebar-nav">
                {navItems.map((section) => (
                    <div key={section.section}>
                        <div className="nav-section-label">{section.section}</div>
                        {section.items.map((item) => (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={`nav-link ${pathname === item.href ? 'active' : ''}`}
                                style={{ justifyContent: 'space-between' }}
                            >
                                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                    <item.icon />
                                    <span>{item.label}</span>
                                </div>
                                {item.customBadge && item.customBadge}
                                {item.badge && <span className="nav-badge" style={{
                                    background: 'var(--bg-tertiary)',
                                    color: 'var(--text-primary)',
                                    border: '1px solid var(--border-light)',
                                    fontSize: '11px',
                                    fontWeight: '700'
                                }}>{item.badge}</span>}
                            </Link>
                        ))}
                    </div>
                ))}
            </nav>
            <div style={{ padding: '16px 20px', borderTop: '1px solid var(--border-light)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div style={{
                        width: '34px', height: '34px', borderRadius: '50%',
                        background: 'linear-gradient(135deg, #2563eb, #7c3aed)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        color: 'white', fontSize: '13px', fontWeight: '700'
                    }}>RM</div>
                    <div>
                        <div style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-primary)' }}>Risk Manager</div>
                        <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Collections Team</div>
                    </div>
                </div>
            </div>
        </aside>
    );
}

function HomeIcon() {
    return (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
            <polyline points="9 22 9 12 15 12 15 22" />
        </svg>
    );
}

function DashboardIcon() {
    return (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="3" width="7" height="7" />
            <rect x="14" y="3" width="7" height="7" />
            <rect x="14" y="14" width="7" height="7" />
            <rect x="3" y="14" width="7" height="7" />
        </svg>
    );
}

function UsersIcon() {
    return (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
            <circle cx="9" cy="7" r="4" />
            <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
            <path d="M16 3.13a4 4 0 0 1 0 7.75" />
        </svg>
    );
}

function AlertIcon() {
    return (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
            <path d="M13.73 21a2 2 0 0 1-3.46 0" />
        </svg>
    );
}


