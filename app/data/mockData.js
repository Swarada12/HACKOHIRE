// ============================================================
// MOCK DATA — Early Warning Delinquency Prediction Platform
// ============================================================

const firstNames = [
  'Aarav', 'Vivaan', 'Aditya', 'Vihaan', 'Arjun', 'Reyansh', 'Sai', 'Arnav', 'Dhruv', 'Kabir',
  'Ananya', 'Diya', 'Myra', 'Sara', 'Aanya', 'Isha', 'Navya', 'Anika', 'Kavya', 'Riya',
  'Rohan', 'Karan', 'Nikhil', 'Amit', 'Priya', 'Neha', 'Sneha', 'Pooja', 'Rajeev', 'Suresh',
  'Meera', 'Lakshmi', 'Deepa', 'Suman', 'Vikram', 'Rahul', 'Gaurav', 'Manish', 'Ajay', 'Sunita',
  'Ramesh', 'Sunil', 'Manoj', 'Ashok', 'Rajesh', 'Vijay', 'Harish', 'Ganesh', 'Pankaj', 'Mohan',
  'Sanjay', 'Tushar', 'Akash', 'Dev', 'Nisha'
];

const lastNames = [
  'Sharma', 'Patel', 'Singh', 'Kumar', 'Reddy', 'Gupta', 'Joshi', 'Mehta', 'Shah', 'Nair',
  'Verma', 'Rao', 'Das', 'Chopra', 'Malhotra', 'Banerjee', 'Iyer', 'Kapoor', 'Sinha', 'Mishra',
  'Agarwal', 'Chauhan', 'Thakur', 'Pillai', 'Desai', 'Bhatia', 'Saxena', 'Kulkarni', 'Pandey', 'Tiwari'
];

const cities = [
  'Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Hyderabad', 'Pune', 'Kolkata', 'Ahmedabad',
  'Jaipur', 'Lucknow', 'Chandigarh', 'Bhopal', 'Indore', 'Nagpur', 'Kochi'
];

const productTypes = ['Home Loan', 'Personal Loan', 'Credit Card', 'Auto Loan', 'Business Loan', 'Education Loan'];

const signalTypes = [
  { type: 'Salary Delay', icon: '⏰', description: 'Salary credited later than usual pattern' },
  { type: 'Savings Drawdown', icon: '📉', description: 'Savings balance declined week-over-week' },
  { type: 'Lending App Transfers', icon: '💸', description: 'Increased UPI transactions to lending apps' },
  { type: 'Late Utility Payment', icon: '🔌', description: 'Utility payments happening later in billing cycle' },
  { type: 'Reduced Discretionary Spend', icon: '🍽️', description: 'Drop in dining and entertainment spending' },
  { type: 'Increased ATM Withdrawals', icon: '🏧', description: 'Cash hoarding behavior detected' },
  { type: 'Failed Auto-Debit', icon: '❌', description: 'Failed auto-debit attempt on scheduled payment' },
  { type: 'Gambling/Lottery Spend', icon: '🎰', description: 'Increased gambling or lottery transactions' },
  { type: 'Balance Decline', icon: '📊', description: 'Current account balance below 30-day average' },
  { type: 'Credit Utilization Spike', icon: '💳', description: 'Credit card utilization crossed 80%' },
];

function seededRandom(seed) {
  let s = seed;
  return function () {
    s = (s * 16807 + 0) % 2147483647;
    return (s - 1) / 2147483646;
  };
}

const rand = seededRandom(42);

function pick(arr) { return arr[Math.floor(rand() * arr.length)]; }
function randBetween(a, b) { return Math.floor(rand() * (b - a + 1)) + a; }
function randFloat(a, b) { return +(a + rand() * (b - a)).toFixed(2); }

// Generate 55 customers
export const customers = Array.from({ length: 55 }, (_, i) => {
  const riskScore = i < 8 ? randBetween(75, 98) :
    i < 20 ? randBetween(50, 74) :
      i < 38 ? randBetween(25, 49) :
        randBetween(2, 24);
  const riskLevel = riskScore >= 75 ? 'Critical' :
    riskScore >= 50 ? 'High' :
      riskScore >= 25 ? 'Medium' : 'Low';

  const numSignals = riskScore >= 75 ? randBetween(4, 7) :
    riskScore >= 50 ? randBetween(2, 4) :
      riskScore >= 25 ? randBetween(1, 2) : randBetween(0, 1);

  const selectedSignals = [];
  const shuffled = [...signalTypes].sort(() => rand() - 0.5);
  for (let j = 0; j < numSignals; j++) {
    selectedSignals.push({
      ...shuffled[j],
      detectedDate: `2026-02-${String(randBetween(1, 15)).padStart(2, '0')}`,
      severity: riskScore >= 75 ? 'Critical' : riskScore >= 50 ? 'High' : 'Medium',
    });
  }

  const product = pick(productTypes);
  const loanAmount = product === 'Credit Card' ? randBetween(50000, 500000) :
    product === 'Home Loan' ? randBetween(2000000, 15000000) :
      randBetween(100000, 3000000);

  return {
    id: `CUST${String(i + 1001).padStart(6, '0')}`,
    name: `${pick(firstNames)} ${pick(lastNames)}`,
    age: randBetween(24, 62),
    city: pick(cities),
    phone: `+91 ${randBetween(70000, 99999)} ${randBetween(10000, 99999)}`,
    email: `customer${i + 1}@email.com`,
    productType: product,
    accountNumber: `XXXX-XXXX-${randBetween(1000, 9999)}`,
    loanAmount,
    outstandingBalance: Math.floor(loanAmount * randFloat(0.3, 0.95)),
    emiAmount: Math.floor(loanAmount / randBetween(24, 120)),
    creditUtilization: product === 'Credit Card' ? randBetween(15, 98) : null,
    riskScore,
    riskLevel,
    riskTrend: riskScore >= 50 ? 'increasing' : rand() > 0.5 ? 'stable' : 'decreasing',
    signals: selectedSignals,
    lastActivity: `2026-02-${String(randBetween(10, 16)).padStart(2, '0')}`,
    customerSince: `${randBetween(2015, 2024)}-${String(randBetween(1, 12)).padStart(2, '0')}`,
    monthlyIncome: randBetween(25000, 500000),
    dti: randBetween(20, 65),
    paymentHistory: Array.from({ length: 6 }, () => rand() > (riskScore / 150) ? 'on-time' : 'late'),
  };
});

// 30-day risk score trend data
export const riskTrendData = Array.from({ length: 30 }, (_, i) => {
  const day = i + 1;
  return {
    date: `Feb ${day}`,
    day,
    avgRiskScore: randBetween(32, 48),
    criticalCount: randBetween(5, 12),
    highCount: randBetween(10, 18),
    mediumCount: randBetween(14, 22),
    newAlerts: randBetween(2, 15),
  };
});

// Risk distribution
export const riskDistribution = [
  { name: 'Critical', value: customers.filter(c => c.riskLevel === 'Critical').length, color: '#ef4444' },
  { name: 'High', value: customers.filter(c => c.riskLevel === 'High').length, color: '#f97316' },
  { name: 'Medium', value: customers.filter(c => c.riskLevel === 'Medium').length, color: '#eab308' },
  { name: 'Low', value: customers.filter(c => c.riskLevel === 'Low').length, color: '#22c55e' },
];

// Portfolio health by product
export const portfolioHealth = productTypes.map(p => ({
  product: p.replace(' ', '\n'),
  productFull: p,
  totalCustomers: customers.filter(c => c.productType === p).length,
  atRisk: customers.filter(c => c.productType === p && c.riskScore >= 50).length,
  delinquencyRate: randFloat(1.2, 8.5),
  recoveryRate: randFloat(55, 92),
}));

// Alerts
export const alerts = [
  { id: 'ALT001', customerId: 'CUST001001', customerName: customers[0]?.name, type: 'Failed Auto-Debit', severity: 'Critical', message: 'EMI auto-debit failed for the 2nd consecutive month', timestamp: '2026-02-16 09:15', status: 'active', suggestedAction: 'Immediate outreach - offer payment restructuring' },
  { id: 'ALT002', customerId: 'CUST001002', customerName: customers[1]?.name, type: 'Salary Delay', severity: 'Critical', message: 'Salary not credited by expected date, delayed by 12 days', timestamp: '2026-02-16 08:30', status: 'active', suggestedAction: 'Send empathetic SMS + schedule agent callback' },
  { id: 'ALT003', customerId: 'CUST001003', customerName: customers[2]?.name, type: 'Savings Drawdown', severity: 'Critical', message: 'Savings account balance dropped 68% in 2 weeks', timestamp: '2026-02-15 22:10', status: 'active', suggestedAction: 'Offer payment holiday for next EMI cycle' },
  { id: 'ALT004', customerId: 'CUST001004', customerName: customers[3]?.name, type: 'Gambling/Lottery Spend', severity: 'High', message: 'Unusual increase in gambling platform transactions (₹45,000)', timestamp: '2026-02-15 19:45', status: 'active', suggestedAction: 'Financial counseling outreach' },
  { id: 'ALT005', customerId: 'CUST001005', customerName: customers[4]?.name, type: 'Credit Utilization Spike', severity: 'High', message: 'Credit utilization spiked from 45% to 92% in 10 days', timestamp: '2026-02-15 16:20', status: 'pending', suggestedAction: 'Credit limit adjustment + spending alert' },
  { id: 'ALT006', customerId: 'CUST001006', customerName: customers[5]?.name, type: 'Lending App Transfers', severity: 'High', message: 'Multiple transfers to 3 different lending apps detected', timestamp: '2026-02-15 14:00', status: 'active', suggestedAction: 'Consolidation loan offer' },
  { id: 'ALT007', customerId: 'CUST001010', customerName: customers[9]?.name, type: 'Late Utility Payment', severity: 'Medium', message: 'Electricity and gas payments delayed by 15+ days', timestamp: '2026-02-15 11:30', status: 'resolved', suggestedAction: 'Monitor - no immediate action needed' },
  { id: 'ALT008', customerId: 'CUST001012', customerName: customers[11]?.name, type: 'Balance Decline', severity: 'Medium', message: 'Current account balance 40% below 30-day average', timestamp: '2026-02-14 20:15', status: 'resolved', suggestedAction: 'Send budgeting tips notification' },
  { id: 'ALT009', customerId: 'CUST001008', customerName: customers[7]?.name, type: 'Increased ATM Withdrawals', severity: 'High', message: 'ATM withdrawals up 300% vs monthly average', timestamp: '2026-02-14 17:50', status: 'active', suggestedAction: 'Schedule relationship manager call' },
  { id: 'ALT010', customerId: 'CUST001015', customerName: customers[14]?.name, type: 'Reduced Discretionary Spend', severity: 'Medium', message: 'Dining and entertainment spend dropped 75%', timestamp: '2026-02-14 10:00', status: 'pending', suggestedAction: 'Monitor for 1 more week' },
  { id: 'ALT011', customerId: 'CUST001020', customerName: customers[19]?.name, type: 'Salary Delay', severity: 'High', message: 'Salary delayed by 8 days from expected pattern', timestamp: '2026-02-13 09:00', status: 'resolved', suggestedAction: 'Proactive outreach completed' },
  { id: 'ALT012', customerId: 'CUST001025', customerName: customers[24]?.name, type: 'Failed Auto-Debit', severity: 'Critical', message: 'Insurance premium auto-debit failed - insufficient balance', timestamp: '2026-02-13 07:30', status: 'active', suggestedAction: 'Immediate outreach for balance top-up' },
];

// Model metrics
export const modelMetrics = {
  xgboost: {
    name: 'XGBoost',
    accuracy: 0.943,
    precision: 0.912,
    recall: 0.887,
    f1: 0.899,
    aucRoc: 0.961,
    trainTime: '12.3 min',
    predictionLatency: '2.1 ms',
    description: 'Gradient boosted trees — best overall accuracy',
  },
  lightgbm: {
    name: 'LightGBM',
    accuracy: 0.938,
    precision: 0.905,
    recall: 0.892,
    f1: 0.898,
    aucRoc: 0.957,
    trainTime: '8.7 min',
    predictionLatency: '1.4 ms',
    description: 'Fast gradient boosting — best latency',
  },
  lstm: {
    name: 'LSTM (PyTorch)',
    accuracy: 0.929,
    precision: 0.895,
    recall: 0.901,
    f1: 0.898,
    aucRoc: 0.952,
    trainTime: '45.2 min',
    predictionLatency: '8.6 ms',
    description: 'Sequence model — best at temporal patterns',
  },
};

// Feature importance
export const featureImportance = [
  { feature: 'Salary Delay (days)', importance: 0.182, category: 'Cash Flow' },
  { feature: 'Savings Balance Change %', importance: 0.156, category: 'Cash Flow' },
  { feature: 'Credit Utilization Ratio', importance: 0.134, category: 'Credit' },
  { feature: 'Failed Auto-Debit Count', importance: 0.121, category: 'Payment' },
  { feature: 'Lending App Transfer Freq', importance: 0.098, category: 'Behavioral' },
  { feature: 'Utility Payment Delay', importance: 0.087, category: 'Payment' },
  { feature: 'Discretionary Spend Change', importance: 0.076, category: 'Spending' },
  { feature: 'ATM Withdrawal Frequency', importance: 0.065, category: 'Behavioral' },
  { feature: 'Debt-to-Income Ratio', importance: 0.058, category: 'Credit' },
  { feature: 'Account Balance Volatility', importance: 0.052, category: 'Cash Flow' },
  { feature: 'Transaction Count Change', importance: 0.041, category: 'Behavioral' },
  { feature: 'Gambling Transaction Amount', importance: 0.038, category: 'Behavioral' },
  { feature: 'Late Payment History', importance: 0.035, category: 'Payment' },
  { feature: 'Monthly Income Stability', importance: 0.032, category: 'Cash Flow' },
  { feature: 'Loan Tenure Remaining', importance: 0.025, category: 'Credit' },
];

// SHAP values for a sample customer
export const shapValues = [
  { feature: 'Salary Delay', value: 0.23, direction: 'positive', baseValue: 0.35 },
  { feature: 'Savings Drawdown', value: 0.18, direction: 'positive', baseValue: 0.35 },
  { feature: 'Credit Utilization', value: 0.12, direction: 'positive', baseValue: 0.35 },
  { feature: 'Failed Auto-Debit', value: 0.09, direction: 'positive', baseValue: 0.35 },
  { feature: 'Lending App Transfers', value: 0.07, direction: 'positive', baseValue: 0.35 },
  { feature: 'Income Stability', value: -0.05, direction: 'negative', baseValue: 0.35 },
  { feature: 'Account Age', value: -0.08, direction: 'negative', baseValue: 0.35 },
  { feature: 'Payment History', value: -0.04, direction: 'negative', baseValue: 0.35 },
];

// AUC-ROC curve points
export const rocCurveData = Array.from({ length: 21 }, (_, i) => {
  const fpr = i / 20;
  return {
    fpr,
    tpr_xgboost: Math.min(1, Math.pow(fpr, 0.15)),
    tpr_lightgbm: Math.min(1, Math.pow(fpr, 0.17)),
    tpr_lstm: Math.min(1, Math.pow(fpr, 0.19)),
    random: fpr,
  };
});

// Dashboard stats
export const dashboardStats = {
  totalCustomers: 124500,
  monitoredCustomers: 55,
  criticalRisk: customers.filter(c => c.riskLevel === 'Critical').length,
  highRisk: customers.filter(c => c.riskLevel === 'High').length,
  activeAlerts: alerts.filter(a => a.status === 'active').length,
  interventionsTriggered: 847,
  costSavings: '₹2.3 Cr',
  recoveryImprovement: '34%',
  avgPredictionLead: '18 days',
  modelAccuracy: '94.3%',
};

// Signal detection timeline for dashboard
export const signalTimeline = [
  { time: '09:15 AM', customer: customers[0]?.name, signal: 'Failed Auto-Debit', severity: 'Critical', id: customers[0]?.id },
  { time: '08:30 AM', customer: customers[1]?.name, signal: 'Salary credited 12 days late', severity: 'Critical', id: customers[1]?.id },
  { time: '08:00 AM', customer: customers[5]?.name, signal: 'Lending app transfers detected', severity: 'High', id: customers[5]?.id },
  { time: '07:45 AM', customer: customers[9]?.name, signal: 'Utility payment delayed 15+ days', severity: 'Medium', id: customers[9]?.id },
  { time: '07:30 AM', customer: customers[3]?.name, signal: 'Gambling spend ₹45,000+', severity: 'High', id: customers[3]?.id },
  { time: '07:00 AM', customer: customers[14]?.name, signal: 'Discretionary spend -75%', severity: 'Medium', id: customers[14]?.id },
  { time: '06:45 AM', customer: customers[7]?.name, signal: 'ATM withdrawals +300%', severity: 'High', id: customers[7]?.id },
  { time: '06:30 AM', customer: customers[2]?.name, signal: 'Savings dropped 68%', severity: 'Critical', id: customers[2]?.id },
];

// Geographic risk data
export const geoRiskData = [
  { region: 'Mumbai', riskIndex: 72, customers: 12500, critical: 340 },
  { region: 'Delhi', riskIndex: 68, customers: 11200, critical: 290 },
  { region: 'Bangalore', riskIndex: 45, customers: 9800, critical: 120 },
  { region: 'Chennai', riskIndex: 52, customers: 8400, critical: 180 },
  { region: 'Hyderabad', riskIndex: 48, customers: 7600, critical: 145 },
  { region: 'Pune', riskIndex: 38, customers: 6200, critical: 85 },
  { region: 'Kolkata', riskIndex: 65, customers: 8900, critical: 260 },
  { region: 'Ahmedabad', riskIndex: 42, customers: 5400, critical: 95 },
  { region: 'Jaipur', riskIndex: 55, customers: 4800, critical: 125 },
  { region: 'Lucknow', riskIndex: 61, customers: 5200, critical: 165 },
];

// Fairness metrics
export const fairnessMetrics = [
  { group: 'Age 18-30', precision: 0.91, recall: 0.88, fpRate: 0.04, count: 15200 },
  { group: 'Age 31-45', precision: 0.94, recall: 0.89, fpRate: 0.03, count: 28400 },
  { group: 'Age 46-60', precision: 0.93, recall: 0.87, fpRate: 0.04, count: 18600 },
  { group: 'Age 60+', precision: 0.92, recall: 0.86, fpRate: 0.05, count: 8200 },
  { group: 'Urban', precision: 0.94, recall: 0.89, fpRate: 0.03, count: 42000 },
  { group: 'Semi-Urban', precision: 0.93, recall: 0.88, fpRate: 0.04, count: 18500 },
  { group: 'Rural', precision: 0.91, recall: 0.86, fpRate: 0.05, count: 9900 },
];

export const architectureData = {
  openSource: [
    { name: 'Data Sources', role: 'Input', desc: 'Aadhar, PAN, KYC, Income, Loan Amount, Salary, etc.', category: 'Data Source' },
    { name: 'Apache Kafka', role: 'Stream Processing', desc: 'Real-time ingestion for fraud detection and immediate signal processing', category: 'Ingestion' },
    { name: 'Apache Airflow', role: 'ETL Orchestrator', desc: 'Batch processing and pipeline scheduling', category: 'Orchestration' },
    { name: 'Postgres / Data Lake', role: 'Storage Layer', desc: 'Raw data lake and structured data warehouse', category: 'Storage' },
    { name: 'Feast', role: 'Feature Store', desc: 'Online (Redis) and Offline (Parquet) feature management', category: 'Feature Engineering' },
    { name: 'XGBoost / LightGBM', role: 'Risk Detection', desc: 'Gradient boosting for classification and risk scoring', category: 'ML Models' },
    { name: 'PyTorch LSTM', role: 'Pattern Analysis', desc: 'Deep learning for sequence/temporal pattern recognition', category: 'ML Models' },
    { name: 'M2 Model Registry', role: 'Registry', desc: 'Versioning and management of trained models', category: 'ML Ops' },
    { name: 'SHAP', role: 'Explainability', desc: 'Feature importance and prediction explanation', category: 'ML Ops' },
    { name: 'BentoML', role: 'Model Serving', desc: 'REST API generation for model inference', category: 'Deployment' },
    { name: 'Risk Engine', role: 'Decisioning', desc: 'Intervention logic and final decision making', category: 'Logic' },
    { name: 'Dash / React', role: 'Dashboard', desc: 'Analytics and visualization interface', category: 'Frontend' },
  ],
  aws: [
    { name: 'Data Sources', role: 'Input', desc: 'Aadhar, PAN, KYC, Income, Loan Amount, Salary, etc.', category: 'Data Source' },
    { name: 'Amazon Kinesis', role: 'Stream Processing', desc: 'Real-time data streaming and ingestion', category: 'Ingestion' },
    { name: 'AWS Glue / Step Functions', role: 'ETL Orchestrator', desc: 'Serverless data integration and workflow orchestration', category: 'Orchestration' },
    { name: 'S3 / Redshift', role: 'Storage Layer', desc: 'Data lake object storage and data warehouse', category: 'Storage' },
    { name: 'SageMaker Feature Store', role: 'Feature Store', desc: 'Fully managed online/offline feature store', category: 'Feature Engineering' },
    { name: 'XGBoost (SageMaker)', role: 'Risk Detection', desc: 'Optimized gradient boosting on SageMaker', category: 'ML Models' },
    { name: 'DeepAR (SageMaker)', role: 'Pattern Analysis', desc: 'Forecasting for time-series data', category: 'ML Models' },
    { name: 'SageMaker Model Registry', role: 'Registry', desc: 'Central repository for model versions', category: 'ML Ops' },
    { name: 'SageMaker Clarify', role: 'Explainability', desc: 'Bias detection and explainability', category: 'ML Ops' },
    { name: 'SageMaker Endpoints', role: 'Model Serving', desc: 'Real-time inference endpoints', category: 'Deployment' },
    { name: 'AWS Lambda', role: 'Decisioning', desc: 'Serverless risk decision logic', category: 'Logic' },
    { name: 'Amazon QuickSight', role: 'Dashboard', desc: 'Business intelligence and visualization', category: 'Frontend' },
  ],
};
