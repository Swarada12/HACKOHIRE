/**
 * Server-Sent Events (SSE) endpoint for realtime dashboard stats only.
 * Streams dashboard_stats every 3s so dashboard/sidebar/landing stay live.
 */
const BENTO_URL = process.env.BENTO_URL || 'http://127.0.0.1:8000';
const DASHBOARD_INTERVAL_MS = 3000;

async function fetchDashboardStats() {
    try {
        const res = await fetch(`${BENTO_URL}/get_dashboard_stats`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({}),
            signal: AbortSignal.timeout(10000),
        });
        if (res.ok) return await res.json();
    } catch (e) {
        console.error('[realtime] get_dashboard_stats failed:', e.message);
    }
    return null;
}

function sendSSE(controller, event, data) {
    const payload = typeof data === 'string' ? data : JSON.stringify(data);
    controller.enqueue(
        new TextEncoder().encode(`event: ${event}\ndata: ${payload}\n\n`)
    );
}

export async function GET() {
    let cleanup = () => { };
    const stream = new ReadableStream({
        async start(controller) {
            const sendDashboard = async () => {
                const stats = await fetchDashboardStats();
                if (stats) sendSSE(controller, 'dashboard_stats', stats);
            };

            await sendDashboard();
            const dashboardInterval = setInterval(sendDashboard, DASHBOARD_INTERVAL_MS);
            const keepAlive = setInterval(() => {
                try {
                    sendSSE(controller, 'ping', {});
                } catch (_) { }
            }, 15000);

            cleanup = () => {
                clearInterval(dashboardInterval);
                clearInterval(keepAlive);
            };
        },
        cancel() {
            cleanup();
        },
    });

    return new Response(stream, {
        headers: {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-store, no-cache, must-revalidate',
            Connection: 'keep-alive',
        },
    });
}
