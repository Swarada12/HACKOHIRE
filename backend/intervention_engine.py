import numpy as np
from typing import Dict, Any

class InterventionEngine:
    """
    Intervention Engine (IE).
    Selects the best proactive action for at-risk customers.
    """
    
    def generate_intervention(self, customer_id: str, features: dict, ml_result: dict, context: dict) -> dict:
        """
        Determines message, channel, and specific relief offer.
        """
        score = ml_result['fusion_score']
        
        # 1. Offer Selection
        offer = "Standard Monitoring"
        offer_id = "OFF-STD"
        
        if score > 85:
            offer = "Debt Restructuring & EMI Holiday"
            offer_id = "OFF-HOLIDAY-3M"
        elif score > 65:
            offer = "Temporary overdraft limit increase (Liquidity Support)"
            offer_id = "OFF-OD-LIMIT"
        elif score > 40:
            offer = "Financial Wellness Webinar & Tips"
            offer_id = "OFF-WELLNESS"

        # 2. Message Generation (Template based LLM-style)
        name = features.get('f_annual_income', 0) # Mapping name from core usually, here placeholder
        messages = {
            "OFF-HOLIDAY-3M": "Hi, we noticed some changes in your recent cash flow. To support you, we're offering a 3-month EMI holiday. Reply YES to discuss.",
            "OFF-OD-LIMIT": "Hi, we've pre-approved a temporary limit increase on your account to help with upcoming bills. View in-app.",
            "OFF-WELLNESS": "Hi, your financial health is important to us. Check out our new 'Smart Budgeting' tools in the Barclays App.",
            "OFF-STD": "Your account is currently under routine monitoring. No action required."
        }
        
        # 3. Channel & Timing
        channel = "In-App Notification"
        if score > 80: channel = "Personal Relationship Manager Call"
        elif score > 60: channel = "Direct WhatsApp"
        
        timing = "Immediate (Within 4 hours)" if score > 80 else "Next 24-48 hours"

        return {
            "intervention_score": score,
            "recommended_offer": offer,
            "offer_id": offer_id,
            "message": messages.get(offer_id, messages["OFF-STD"]),
            "channel": channel,
            "timing_optimizer": timing,
            "status": "Recommendation Generated"
        }
