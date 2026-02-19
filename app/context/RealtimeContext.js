'use client';

import { createContext, useContext, useEffect, useState } from 'react';

const RealtimeContext = createContext(null);

export function RealtimeProvider({ children }) {
    const [dashboardStats, setDashboardStats] = useState(null);
    const [isConnected, setIsConnected] = useState(false);

    useEffect(() => {
        if (typeof window === 'undefined') return;
        const url = '/api/realtime';
        const es = new EventSource(url);

        es.addEventListener('dashboard_stats', (e) => {
            try {
                const data = JSON.parse(e.data);
                setDashboardStats(data);
            } catch (_) { }
        });
        es.onopen = () => setIsConnected(true);
        es.onerror = () => setIsConnected(false);

        return () => {
            es.close();
            setIsConnected(false);
        };
    }, []);

    const value = {
        dashboardStats,
        isConnected,
        setDashboardStats,
    };

    return (
        <RealtimeContext.Provider value={value}>
            {children}
        </RealtimeContext.Provider>
    );
}

export function useRealtime() {
    const ctx = useContext(RealtimeContext);
    if (!ctx) throw new Error('useRealtime must be used within RealtimeProvider');
    return ctx;
}

/** Dashboard + Sidebar: live stats from SSE, with optional initial fetch fallback */
export function useRealtimeDashboardStats() {
    const { dashboardStats, isConnected, setDashboardStats } = useRealtime();
    return { dashboardStats, isConnected, setDashboardStats };
}

