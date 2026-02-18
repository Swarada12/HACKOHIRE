import numpy as np
import pandas as pd
from typing import Dict, Any

class MLRiskEngine:
    """
    Multi-Agent Ensemble ML Engine.
    Combines specialized models for 360-degree risk assessment.
    """
    
    def predict_ensemble(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Fuses predictions from 3 specialized agents.
        """
        # 1. Financial Risk Agent (Focus: Income, DTI, Credit Score)
        financial_score, financial_reasons = self._agent_financial_risk(features)
        
        # 2. Behavioral Risk Agent (Focus: App activity, usage patterns)
        behavioral_score, behavioral_reasons = self._agent_behavioral_risk(features)
        
        # 3. Trend & Velocity Agent (Focus: Salary delays, spend drift)
        velocity_score, velocity_reasons = self._agent_velocity_trend(features)
        
        # ENSEMBLE FUSION
        weights = {
            'financial': 0.5,
            'behavioral': 0.25,
            'velocity': 0.25
        }
        
        fusion_score = (financial_score * weights['financial'] + 
                        behavioral_score * weights['behavioral'] + 
                        velocity_score * weights['velocity'])
        
        # Confidence Score calculation
        scores = [financial_score, behavioral_score, velocity_score]
        std_dev = np.std(scores)
        
        # Smart Confidence: If any agent is screaming "FIRE" (High Risk), we are confident risk exists.
        max_risk = max(scores)
        if max_risk > 80:
            # "One agent is critical -> High Confidence"
            confidence = 0.92 - (std_dev / 200) 
        elif max_risk > 60:
            confidence = 0.85 - (std_dev / 200)
        else:
            confidence = max(0.6, 1.0 - (std_dev / 100))
            
        return {
            "fusion_score": int(round(fusion_score)),
            "confidence_score": round(confidence, 2),
            "agent_scores": {
                "financial": int(round(financial_score)),
                "behavioral": int(round(behavioral_score)),
                "velocity": int(round(velocity_score))
            },
            "agent_reasoning": {
                "financial": financial_reasons,
                "behavioral": behavioral_reasons,
                "velocity": velocity_reasons
            }
        }

    def _agent_financial_risk(self, f: Dict[str, float]) -> tuple:
        base = 20
        reasons = []
        
        # High DTI increases risk
        dti = f.get('f_dti_ratio', 0)
        if dti > 0.5: 
            base += 30
            reasons.append(f"Critical DTI Ratio: {int(dti*100)}%")
        elif dti > 0.4:
            base += 15
            reasons.append(f"High DTI Ratio: {int(dti*100)}%")
            
        # Low credit score increases risk
        credit_score = f.get('f_credit_score', 750)
        if credit_score < 650: 
            base += 25
            reasons.append(f"Low Credit Score: {int(credit_score)}")
            
        # High utilization
        util = f.get('f_credit_utilization', 0)
        if util > 85: 
            base += 50
            reasons.append(f"Maxed Out Credit Cards ({int(util)}%)")
        elif util > 50: 
            base += 20
            reasons.append(f"High Credit Utilization ({int(util)}%)")
            
        if not reasons: reasons.append("Stable Financial Indicators")
            
        return min(99, max(5, base)), reasons

    def _agent_behavioral_risk(self, f: Dict[str, float]) -> tuple:
        base = 15
        reasons = []
        
        gambling = f.get('f_gambling_to_income', 0)
        if gambling > 0.1: 
            base += 40
            reasons.append("High Volume Gambling Transactions Detected")
        
        if f.get('b_night_login_ratio', 0) > 0.4: 
            base += 20
            reasons.append("Unusual Night-time Login Activity (2AM-5AM)")
        
        inquiries = f.get('b_loan_inquiry_count', 0)
        if inquiries > 3: 
            base += 25
            reasons.append(f"Multiple Loan Inquiries ({int(inquiries)}) in short span")
            
        # New Signal: Belt Tightening (Discretionary Spend Reduction)
        disc_trend = f.get('t_discretionary_trend', 1.0)
        if disc_trend < 0.6 and disc_trend > 0:
            base += 20
            reasons.append(f"Sudden Drop in Discretionary Spend ({int(disc_trend*100)}% of normal)")

        if not reasons: reasons.append("Normal Behavioral Patterns")
        return min(99, max(5, base)), reasons

    def _agent_velocity_trend(self, f: Dict[str, float]) -> tuple:
        base = 10
        reasons = []
        
        current_delay = f.get('t_current_salary_delay', 0)
        if current_delay > 10: 
            base = 99
            reasons.append(f"CRITICAL: Salary Delayed by {int(current_delay)} days")
        elif current_delay > 7:
            base += 60 
            reasons.append(f"High Risk: Salary Delayed by {int(current_delay)} days")
        elif current_delay > 3:
            base += 30
            reasons.append(f"Warning: Salary Delayed by {int(current_delay)} days")
            
        if f.get('t_salary_delay_trend', 0) > 2: 
            base += 30
            reasons.append("Worsening Salary Delay Trend month-over-month")
            
        if f.get('b_activity_velocity', 1) > 2.0: 
            base += 15
            reasons.append("Sudden Spike in App Usage Velocity (>200%)")
            
        # New Signal: Auto-Debit Bounce
        bounces = f.get('t_auto_debit_fail_count', 0)
        if bounces > 0:
            base += 50 * bounces
            reasons.append(f"CRITICAL: Auto-Debit Bounce Detected ({int(bounces)}x)")
            
        # New Signal: Utility Latency
        util_delay = f.get('t_utility_delay_days', 0)
        if util_delay > 7:
            base += 20
            reasons.append(f"Utility Bill Payment Lag ({int(util_delay)} days)")

        if not reasons: reasons.append("Stable Velocity & Salary Trends")
        return min(99, max(5, base)), reasons

class RareCaseSolver:
    """
    Context & Decision Intelligence Agent.
    Handles outliers and specific business contexts.
    """
    def resolve_context(self, features: dict, ml_result: dict) -> dict:
        """
        Decision Intelligence Framework (XGBoost-Calibrated Logic).
        Separates 'Can Pay' (Ability) from 'Will Pay' (Willingness).
        """
        # Strategic Decision Indices (XGBoost-Calibrated Logic)
        # 1. Ability to Pay Model
        income = features.get('f_monthly_salary', 0)
        emi = features.get('f_monthly_emi', 0)
        savings_trend = features.get('f_savings_change_pct', 0)
        utilization = features.get('f_credit_utilization', 0)
        
        # PERSISTENCE OVERRIDE: Check if DB has seeded values
        db_ability = features.get('f_db_ability')
        if db_ability is not None:
            ability = float(db_ability)
        else:
            ability = 100
            if income > 0 and (emi / income) > 0.6: ability -= 40 
            elif income > 0 and (emi / income) > 0.4: ability -= 20
            if utilization > 85: ability -= 30 
            elif utilization > 50: ability -= 15
            if savings_trend < -20: ability -= 15 
            ability = max(5, min(100, ability))

        # 2. Willingness to Pay Model
        credit_score = features.get('f_credit_score', 750)
        avg_delay = features.get('t_avg_salary_delay', 0)
        gambling = features.get('f_gambling_to_income', 0)
        lending_apps = features.get('f_spend_lending_app_60d', 0)
        
        db_willingness = features.get('f_db_willingness')
        if db_willingness is not None:
            willingness = float(db_willingness)
        else:
            willingness = (credit_score / 900) * 100
            if gambling > 0.05: willingness -= 40 
            if lending_apps > 5000: willingness -= 20 
            if avg_delay > 5: willingness -= 15 
            willingness = max(5, min(99, willingness))
        
        # 3. Rare Case / Anomaly Detection
        case_type = features.get('f_db_rare_case_type')
        if not case_type or case_type == "Normal":
            # Re-calculate if not in DB or normal
            case_type = "Normal"
            if ability > 60 and willingness < 50: case_type = "Strategic Defaulter (High Ability, Low Intent)"
            elif ability < 40 and willingness > 60: case_type = "Victim of Circumstance (Low Ability, High Intent)"
            elif ability < 30 and willingness < 30: case_type = "High Risk Insolvency"
            if ability > 80 and willingness > 80: case_type = "Prime Customer"
        
        is_rare = case_type != "Normal" and "Prime" not in case_type
        
        return {
            "rare_case_detected": is_rare,
            "case_type": case_type,
            "ability_score": int(ability),
            "willingness_score": int(willingness),
            "governance_status": "Escalate to Senior RM" if is_rare else "Automated Recovery"
        }
