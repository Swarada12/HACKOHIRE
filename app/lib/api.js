export async function predictRisk(customer) {
    try {
        // Map frontend customer object to backend RAW schema (Aadhar, PAN, etc.)
        const payload = {
            customer_id: customer.id,
            aadhar_no: customer.aadhar || `1234-5678-${Math.floor(Math.random() * 9000) + 1000}`, // Simulated mapping if missing
            pan_no: customer.pan || `ABCDE${Math.floor(Math.random() * 9000) + 1000}F`,
            name: customer.name,
            monthly_salary: customer.monthlyIncome || 50000,
            loan_amount: customer.loanAmount || 500000,
            current_salary_delay_days: customer.salaryDelay || 0
        };

        const res = await fetch('/api/ml/predict_risk', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ input_data: payload }),
        });

        if (!res.ok) throw new Error('API fetch failed');
        return await res.json();
    } catch (err) {
        console.error("ML Service Error:", err);
        return null; // Return null to fallback to mock/loading state
    }
}

export async function analyzePattern(transactions) {
    try {
        const payload = {
            amounts: transactions.map(t => t.amount)
        };

        const res = await fetch('/api/ml/analyze_pattern', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ input_data: payload }),
        });

        if (!res.ok) throw new Error('API fetch failed');
        return await res.json();
    } catch (err) {
        console.error("Pattern Service Error:", err);
        return null;
    }
}

export async function getCustomers(filter = "All", search = "") {
    try {
        const res = await fetch('/api/ml/list_customers', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ input_data: { risk_filter: filter, search: search } })
        });
        if (!res.ok) throw new Error('Failed to fetch customers');
        return await res.json();
    } catch (err) {
        console.error("API Error getCustomers:", err);
        return [];
    }
}

export async function getCustomer(id) {
    try {
        const res = await fetch('/api/ml/get_customer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ input_data: { customer_id: id } })
        });
        if (!res.ok) throw new Error('Failed to fetch customer');
        return await res.json();
    } catch (err) {
        console.error("API Error getCustomer:", err);
        return null;
    }
}

export async function analyzeCustomerRisk(customerId) {
    try {
        const res = await fetch('/api/ml/analyze_customer_risk', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ input_data: { customer_id: customerId } })
        });
        if (!res.ok) return null;
        return await res.json();
    } catch (err) {
        console.error('Error analyzing customer risk:', err);
        return null;
    }
}

export async function generateAIInsights(customerId) {
    try {
        const res = await fetch('/api/ml/generate_ai_insights', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ input_data: { customer_id: customerId } })
        });
        if (!res.ok) throw new Error('Failed to generate AI insights');
        return await res.json();
    } catch (err) {
        console.error("API Error generateAIInsights:", err);
        return null;
    }
}

export async function getDashboardStats() {
    try {
        const res = await fetch('/api/ml/get_dashboard_stats', { method: 'POST' });
        if (!res.ok) throw new Error('Failed to fetch dashboard stats');
        return await res.json();
    } catch (err) {
        console.error("API Error getDashboardStats:", err);
        return null;
    }
}

export async function executeIntervention(customerId, offerId) {
    try {
        const res = await fetch('/api/ml/execute_intervention', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ input_data: { customer_id: customerId, offer_id: offerId } })
        });
        if (!res.ok) throw new Error('Failed to execute intervention');
        return await res.json();
    } catch (err) {
        console.error("API Error executeIntervention:", err);
        return null;
    }
}
