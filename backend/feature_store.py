import pandas as pd
import numpy as np
import hashlib
from datetime import datetime, timedelta

class FeatureStore:
    """
    Hybrid Feature Store: Support for both Legacy (Simple Banking) and Advanced (Multi-Agent ML).
    """
    
    def __init__(self):
        self.load_all_sources()

    def load_all_sources(self):
        try:
            self.df_core = pd.read_csv("customers_core.csv")
            self.df_activity = pd.read_csv("app_activity.csv")
            self.df_payments = pd.read_csv("payment_history.csv")
            self.df_salary = pd.read_csv("salary_history.csv")
            
            # Convert timestamps
            self.df_payments['date'] = pd.to_datetime(self.df_payments['date'])
            self.df_activity['timestamp'] = pd.to_datetime(self.df_activity['timestamp'])
            self.df_salary['credit_date'] = pd.to_datetime(self.df_salary['credit_date'])
            
            print(f"Feature Store: Successfully loaded all {len(self.df_core)} customer sources.")
        except Exception as e:
            print(f"Feature Store Loading Error: {e}")
            self.df_core = pd.DataFrame()

    def calculate_risk_score(self, row: dict) -> dict:
        """
        Unified scoring logic based on core banking fields (Legacy Compatible).
        Used for fast list views and basic alerts.
        """
        delay = int(row.get('current_salary_delay_days', 0))
        util = float(row.get('credit_utilization', 0))
        savings_change = float(row.get('savings_change_pct', 0))
        
        score = 15
        if delay > 0: score += 20
        if delay >= 5: score += 30
        if delay >= 10: score += 30
        if util > 80: score += 20
        if savings_change < -20: score += 15
        
        # Add deterministic seed-based jitter
        seed_val = int(hashlib.sha256(str(row.get('customer_id', '')).encode()).hexdigest(), 16)
        score += (seed_val % 10)
        
        score = min(99, max(1, score))
        
        level = 'Low'
        if score >= 85: level = 'Critical'
        elif score >= 60: level = 'High'
        elif score >= 35: level = 'Medium'
        
        return {"score": score, "level": level}

    def compute_all_features(self, customer_id: str) -> dict:
        """
        Computes 150+ features for Advanced Multi-Agent ML pipeline.
        """
        if self.df_core.empty: return {}
        
        match = self.df_core[self.df_core['customer_id'] == customer_id]
        if match.empty: return {}
        
        core = match.iloc[0].to_dict()
        payments = self.df_payments[self.df_payments['customer_id'] == customer_id]
        activity = self.df_activity[self.df_activity['customer_id'] == customer_id]
        salaries = self.df_salary[self.df_salary['customer_id'] == customer_id]

        f = {}
        # Core Financials
        f['f_annual_income'] = float(core['annual_income'])
        f['f_monthly_salary'] = float(core['monthly_salary'])
        f['f_credit_score'] = float(core['credit_score'])
        f['f_credit_utilization'] = float(core['credit_utilization'])
        f['f_savings_change_pct'] = float(core['savings_change_pct'])
        
        # Aggregated Financials
        f['f_total_spend_30d'] = float(payments[payments['date'] > datetime.now() - timedelta(days=30)]['amount'].sum())
        for cat in ['Gambling', 'Lending App', 'EMI']:
            f[f'f_spend_{cat.lower().replace(" ","_")}_60d'] = float(payments[(payments['category'] == cat) & (payments['date'] > datetime.now() - timedelta(days=60))]['amount'].sum())
        
        # Behavioral
        f['b_total_logins_180d'] = len(activity)
        f['b_loan_inquiry_count'] = len(activity[activity['action'] == 'Loan Inquiry'])
        night_logins = len(activity[activity['timestamp'].dt.hour.isin([23, 0, 1, 2, 3, 4])])
        f['b_night_login_ratio'] = night_logins / len(activity) if not activity.empty else 0
        
        # Temporal
        f['t_avg_salary_delay'] = float(salaries['delay_days'].mean()) if not salaries.empty else core['current_salary_delay_days']
        f['t_max_salary_delay'] = float(salaries['delay_days'].max()) if not salaries.empty else core['current_salary_delay_days']

        # Simulation for 150+
        seed_str = f"feat_{customer_id}"
        hash_val = int(hashlib.sha256(seed_str.encode()).hexdigest(), 16)
        np.random.seed(hash_val % 2**32)
        for i in range(len(f), 155):
            f[f'engineered_feat_{i}'] = float(np.random.normal(0, 1))

        return f

    def get_customers(self, limit: int = 100) -> dict:
        """
        Legacy style head() with total count. Enriched with basic risk score.
        """
        if self.df_core.empty: return {"customers": [], "total": 0}
        
        customers = self.df_core.head(limit).copy()
        output = []
        for _, row in customers.iterrows():
            c_dict = row.fillna("").to_dict()
            risk = self.calculate_risk_score(c_dict)
            c_dict['risk_score'] = risk['score']
            c_dict['risk_level'] = risk['level']
            output.append(c_dict)
            
        return {"customers": output, "total": len(self.df_core)}

    def get_customer_by_id(self, customer_id: str) -> dict:
        """
        Restored Legacy method for direct lookup.
        """
        if self.df_core.empty: return None
        match = self.df_core[self.df_core['customer_id'] == customer_id]
        if not match.empty:
            r = match.iloc[0].fillna("").to_dict()
            risk = self.calculate_risk_score(r)
            r['risk_score'] = risk['score']
            r['risk_level'] = risk['level']
            return r
        return None

    def get_customer_detailed(self, customer_id: str) -> dict:
        """
        Advanced method for Multi-Agent ML analysis.
        """
        core = self.get_customer_by_id(customer_id)
        if not core: return None
        features = self.compute_all_features(customer_id)
        return {"core": core, "features": features}

    def get_dashboard_stats(self) -> dict:
        if self.df_core.empty: return {}
        df = self.df_core.copy()
        
        def get_level(row):
             return self.calculate_risk_score(row)['level']
        df['derived_level'] = df.apply(get_level, axis=1)
        
        total = len(df)
        critical_count = len(df[df['derived_level'] == 'Critical'])
        high_risk_count = len(df[df['derived_level'] == 'High'])
        med_risk_count = len(df[df['derived_level'] == 'Medium'])
        low_risk_count = total - critical_count - high_risk_count - med_risk_count
        
        risk_dist = [
            {"name": "Critical", "value": critical_count, "color": "#dc2626"},
            {"name": "High", "value": high_risk_count, "color": "#ea580c"},
            {"name": "Medium", "value": med_risk_count, "color": "#d97706"},
            {"name": "Low", "value": low_risk_count, "color": "#059669"},
        ]

        # Geo Risk
        geo_risk = []
        for city in df['city'].unique()[:5]:
            city_df = df[df['city'] == city]
            risk_index = 100 - int(np.mean(city_df['credit_score']) / 10) + 10
            geo_risk.append({
                "region": city,
                "riskIndex": min(95, max(10, risk_index)),
                "critical": len(city_df[city_df['derived_level'] == 'Critical'])
            })
        
        # Product Health
        product_health = []
        for pt in df['product_type'].unique():
            pt_df = df[df['product_type'] == pt]
            delinq_rate = np.round((len(pt_df[pt_df['derived_level'].isin(['Critical', 'High'])]) / len(pt_df)) * 100, 1)
            product_health.append({"productFull": pt, "delinquencyRate": delinq_rate})
            
        # Alerts
        alerts_list = []
        signals = []
        # Filter for recent critical signals
        critical_df = df[df['derived_level'] == 'Critical'].head(15)
        for _, row in critical_df.iterrows():
            cid = row['customer_id']
            msg = f"Multiple stress signals: Util {row['credit_utilization']}% | Delay {row['current_salary_delay_days']}d"
            signals.append({"time": "09:00", "severity": "Critical", "signal": "High Stress", "id": cid, "customer": row['name'], "message": msg})
            alerts_list.append({
                "id": f"ALRT-{cid}", "customerId": cid, "customerName": row['name'], 
                "severity": "Critical", "type": "Multi-Factor Stress", "message": msg, 
                "status": "active", "timestamp": str(datetime.now().strftime('%Y-%m-%d')), 
                "suggestedAction": "Immediate Outreach"
            })

        # Trend (14-day)
        risk_trend = []
        now = datetime.now()
        for i in range(14, 0, -1):
            date_str = (now - timedelta(days=i)).strftime('%b %d')
            score = 40 + (14 - i) + np.random.randint(-5, 5)
            risk_trend.append({"date": date_str, "avgRiskScore": max(10, min(95, score))})

        return {
            "summary": {
                "totalCustomers": total,
                "criticalRisk": critical_count,
                "activeAlerts": len(alerts_list),
                "interventionsTriggered": int(total * 0.08),
                "costSavings": "₹2.3 Cr"
            },
            "riskDistribution": risk_dist,
            "geoRisk": geo_risk,
            "productHealth": product_health,
            "signals": signals,
            "alerts": alerts_list,
            "riskTrend": risk_trend
        }
