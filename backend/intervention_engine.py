import numpy as np
from typing import Dict, Any
from datetime import datetime, timedelta

class InterventionEngine:
    """
    Intervention Engine (IE).
    Selects the best proactive action for at-risk customers.
    """
    
    
    def _calculate_impact(self, loan_amount: float, risk_score: int, offer_id: str) -> dict:
        """
        Profit Engine: Quantifies the financial impact of the intervention.
        """
        # 1. Default Probability (Calibrated to Risk Score)
        default_prob_current = min(0.99, (risk_score / 140)) # e.g. 70 score -> 50% risk
        
        # 2. Effectiveness of Intervention (Modifier)
        modifiers = {
            "OFF-MORATORIUM": 0.4,    # High impact
            "OFF-SALARY-ADV": 0.3,    # Good impact
            "OFF-TENURE": 0.25,       # Moderate
            "OFF-LIMIT-CAP": 0.15,    # Prevention
            "OFF-CONSOLIDATION": 0.35, 
            "OFF-GOVERNANCE": 0.5,    # Very high impact (human touch)
            "OFF-GAMBLING-BLOCK": 0.3,
            "OFF-WELLNESS": 0.1,
            "OFF-STD": 0.0
        }
        improvement = modifiers.get(offer_id, 0.0)
        default_prob_new = default_prob_current * (1.0 - improvement)
        
        # 3. Financials
        recovery_gain = loan_amount * (default_prob_current - default_prob_new)
        coll_cost_saved = recovery_gain * 0.18 # Avg 18% collection cost
        
        return {
            "default_prob_current": round(default_prob_current * 100, 1),
            "default_prob_projected": round(default_prob_new * 100, 1),
            "recovery_gain": int(recovery_gain),
            "cost_savings": int(coll_cost_saved)
        }

    def generate_intervention(self, customer_id: str, features: dict, ml_result: dict, context: dict, unified_score: int = None) -> dict:
        """
        Hyper-Personalized Intervention Logic.
        Prioritizes the heaviest stressor identified by the Multi-Agent Brain.
        """
        score = unified_score if unified_score is not None else ml_result['fusion_score']
        agent_scores = ml_result.get('agent_scores', { 'financial': 0, 'behavioral': 0, 'velocity': 0 })
        
        # Identity Context
        name = features.get('name', features.get('f_name', 'Customer'))
        if name == 'Customer': 
            # Try to extract from customer_id or other fields if possible, or keep as fallback
            pass

        monthly_salary = features.get('f_monthly_salary', 50000)
        monthly_emi = features.get('f_monthly_emi', 0)
        
        # Fix: Spending Gap fallback calculation (Hackathon Demo Optimization)
        raw_gap = abs(int(features.get('f_savings_account_balance', 0) * (features.get('f_savings_change_pct', 0) / 100))) if features.get('f_savings_change_pct', 0) < 0 else 0
        if raw_gap == 0 and score > 40:
             spending_gap = int(max(monthly_emi * 0.5, monthly_salary * 0.15))
        else:
             spending_gap = raw_gap if raw_gap > 0 else 4500
        
        # 1. Stressor Analysis
        lead_agent = max(agent_scores, key=agent_scores.get) if agent_scores else "financial"
        lead_val = agent_scores.get(lead_agent, 0)

        # 2. Decision Intelligence Layer
        case_type = context.get('case_type', 'Normal')
        is_strategic = "Strategic Defaulter" in case_type
        is_victim = "Victim of Circumstance" in case_type

        # 3. Dynamic Offer Selection Logic (REFACTORED FOR DIVERSITY)
        offer = "Standard Monitoring"
        offer_id = "OFF-STD"

        # PRIORITY 1: CONTEXT OVERRIDES (Rare Case Intelligence)
        if is_victim and score > 40:
            offer = f"Moratorium: Pause EMI until { (datetime.now() + timedelta(days=30)).strftime('%d %b') }"
            offer_id = "OFF-MORATORIUM"
        elif is_strategic:
            offer = "Risk Governance: RM Advisory Call Required"
            offer_id = "OFF-GOVERNANCE"

        # PRIORITY 2: CRITICAL VELOCITY (Salary/Liquidity CRASH)
        elif lead_agent == "velocity" and (lead_val > 60 or score > 75):
            delay = int(features.get('t_current_salary_delay', 0))
            if delay > 7:
                offer = f"Salary Advance: Rs.{int(monthly_salary*0.4)} (Detected {delay}d delay)"
                offer_id = "OFF-SALARY-ADV"
            else:
                offer = "Tenure Extension: +3 Months Relief"
                offer_id = "OFF-TENURE"

        # PRIORITY 3: FINANCIAL STRESS (DTI/Utilization)
        elif lead_agent == "financial" and (lead_val > 50 or score > 45):
            util = int(features.get('f_credit_utilization', 0))
            if util > 85:
                offer = f"Limit Freeze Logic: Cap at {util}%"
                offer_id = "OFF-LIMIT-CAP"
            else:
                offer = "Debt Consolidation: High-Interest App Swap"
                offer_id = "OFF-CONSOLIDATION"

        # PRIORITY 4: BEHAVIORAL DRIFT (Gambling/Night Activity)
        elif lead_agent == "behavioral" and (lead_val > 40 or score > 40):
            if features.get('f_gambling_to_income', 0) > 0.05:
                offer = "Selective Merchant Block: 48hr Cool-Off"
                offer_id = "OFF-GAMBLING-BLOCK"
            else:
                offer = "Financial Wellness: Smart Saver Dashboard"
                offer_id = "OFF-WELLNESS"
        
        # CRITICAL FALLBACK: If Score is high but no specific agent triggered (e.g. legacy mismatch)
        if score >= 85 and offer_id == "OFF-STD":
            offer = "Priority Review: Senior RM Intervention"
            offer_id = "OFF-GOVERNANCE"

        # 4. Message Vault (Context-Engineered)
        messages = {
            "OFF-SALARY-ADV": f"Hi {name}, our Velocity Agent detected a {int(features.get('t_current_salary_delay', 0))}d salary delay. To keep your credit score safe, we've pre-approved a Rs.{int(monthly_salary*0.4)} advance. Reply YES to credit instantly.",
            "OFF-TENURE": f"Hi {name}, we detected a sudden spike in your expense velocity. To give you some breathing room, we can extend your loan tenure by 3 months, lowering your monthly burden immediately. Reply YES to review.",
            "OFF-LIMIT-CAP": f"Hi {name}, your Credit Utilization has hit {int(features.get('f_credit_utilization', 0))}%. To prevent over-leverage and protect your score, we recommend a temporary limit freeze at current levels. Reply YES to activate guard.",
            "OFF-CONSOLIDATION": f"Hi {name}, we've identified several high-interest outflows of approx Rs.{spending_gap}. We can consolidate these into your existing loan at a lower rate, saving you money monthly. Click for detail.",
            "OFF-GAMBLING-BLOCK": f"Hi {name}, Behavioral Analysis shows unusual merchant patterns. For your budget safety, we can enable a 48-hour cool-off period on specific categories. This is a temporary shield. Reply YES to enable.",
            "OFF-WELLNESS": f"Hi {name}, our AI noticed a Rs.{spending_gap} spending gap this month. Activate your 'Smart Saver' Dashboard to get personalized budget alerts and avoid late fees.",
            "OFF-MORATORIUM": f"Hi {name}, we understand you're facing unexpected liquidity stress. As a valued customer, we've approved a 30-day EMI moratorium with zero penalties to help you recover. Reply YES to activate.",
            "OFF-GOVERNANCE": f"Hi {name}, the bank has flagged a divergence in your repayment capacity vs behavior. Your Relationship Manager will call you within 4 hours to discuss a customized repayment roadmap.",
            "OFF-STD": f"Hi {name}, your account is in good standing. We're monitoring your finances to ensure everything stays on track. No action needed today."
        }

        # 5. Delivery Logic
        channel = "In-App Notification"
        if is_strategic or score >= 80: channel = "Relationship Manager Call"
        elif score > 50: channel = "WhatsApp Business API"
        
        timing = "Immediate" if score > 75 else "Next 24 Business Hours"

        # Refined Lead Stressor Label (Avoid generic "Enterprise Governance" if possible)
        if offer_id == "OFF-GOVERNANCE" and lead_val < 30:
            stressor = "Multi-Factor Governance"
        else:
            stressor = lead_agent.title()

        return {
            "intervention_score": score,
            "recommended_offer": offer,
            "offer_id": offer_id,
            "message": messages.get(offer_id, messages["OFF-STD"]),
            "channel": channel,
            "timing_optimizer": timing,
            "lead_stressor": stressor,
            "status": "Recommendation Sent",
            "meta": {
                "case_context": case_type,
                "risk_reduction": "High" if score > 60 else "Medium"
            }
        }
