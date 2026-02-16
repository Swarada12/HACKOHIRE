'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Sidebar() {
    const pathname = usePathname();

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
                { href: '/alerts', label: 'Intervention Hub', icon: AlertIcon },
            ]
        },

    ];

    return (
        <aside className="sidebar">
            <div className="sidebar-header">
                <div className="sidebar-logo">B</div>
                <div className="sidebar-brand">
                    <h2>Barclays EWS</h2>
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
                            >
                                <item.icon />
                                <span>{item.label}</span>
                                {item.badge && <span className="nav-badge">{item.badge}</span>}
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


