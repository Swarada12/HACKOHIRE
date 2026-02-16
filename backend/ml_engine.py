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
        financial_score = self._agent_financial_risk(features)
        
        # 2. Behavioral Risk Agent (Focus: App activity, usage patterns)
        behavioral_score = self._agent_behavioral_risk(features)
        
        # 3. Trend & Velocity Agent (Focus: Salary delays, spend drift)
        velocity_score = self._agent_velocity_trend(features)
        
        # ENSEMBLE FUSION
        # We use a weighted average based on feature reliability
        weights = {
            'financial': 0.5,
            'behavioral': 0.25,
            'velocity': 0.25
        }
        
        fusion_score = (financial_score * weights['financial'] + 
                        behavioral_score * weights['behavioral'] + 
                        velocity_score * weights['velocity'])
        
        # Confidence Score calculation (Agreement between models)
        scores = [financial_score, behavioral_score, velocity_score]
        std_dev = np.std(scores)
        confidence = max(0.6, 1.0 - (std_dev / 50)) # Higher variance = lower confidence
        
        return {
            "fusion_score": round(fusion_score, 2),
            "confidence_score": round(confidence, 2),
            "agent_scores": {
                "financial": round(financial_score, 2),
                "behavioral": round(behavioral_score, 2),
                "velocity": round(velocity_score, 2)
            }
        }

    def _agent_financial_risk(self, f: Dict[str, float]) -> float:
        # Simplified XGBoost-like logic
        base = 20
        # High DTI increases risk
        if f.get('f_dti_ratio', 0) > 0.4: base += 30
        # Low credit score increases risk
        if f.get('f_credit_score', 750) < 650: base += 25
        # High utilization
        if f.get('f_lending_intensity', 0) > 0.3: base += 20
        return min(99, max(5, base))

    def _agent_behavioral_risk(self, f: Dict[str, float]) -> float:
        # Behavioral patterns (Sudden logins, gambling)
        base = 15
        if f.get('f_gambling_to_income', 0) > 0.1: base += 40
        if f.get('b_night_login_ratio', 0) > 0.4: base += 20
        if f.get('b_loan_inquiry_count', 0) > 3: base += 25
        return min(99, max(5, base))

    def _agent_velocity_trend(self, f: Dict[str, float]) -> float:
        # Time-series drift logic
        base = 10
        if f.get('t_avg_salary_delay', 0) > 5: base += 40
        if f.get('t_salary_delay_trend', 0) > 2: base += 30
        if f.get('b_activity_velocity', 1) > 2.0: base += 15 # Sudden spike in app activity
        return min(99, max(5, base))

class RareCaseSolver:
    """
    Context & Decision Intelligence Agent.
    Handles outliers and specific business contexts.
    """
    def resolve_context(self, features: dict, ml_result: dict) -> dict:
        ability = 100 - features.get('f_dti_ratio', 0)*100
        willingness = 100 - (features.get('f_gambling_to_income', 0)*200 + features.get('t_max_salary_delay', 0)*5)
        
        # Rare Case: High risk score but high willingness/ability (Simulated)
        is_rare = (ml_result['fusion_score'] > 70) and (ability > 60 and willingness > 80)
        
        return {
            "rare_case_detected": is_rare,
            "ability_score": round(max(0, ability), 2),
            "willingness_score": round(max(0, willingness), 2),
            "governance_status": "Green" if not is_rare else "Yellow (Review Required)"
        }
