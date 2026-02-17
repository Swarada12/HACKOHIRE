import bentoml
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
load_dotenv() # Load environment variables from .env BEFORE other imports
from feature_store import FeatureStore
from ml_engine import MLRiskEngine, RareCaseSolver
from intervention_engine import InterventionEngine
from typing import Dict, Any, List

# Initialize Core Components
feature_store = FeatureStore()
risk_engine = MLRiskEngine()
context_solver = RareCaseSolver()
intervention_engine = InterventionEngine()

from pydantic import BaseModel

# Input Schemas
class RiskInput(BaseModel):
    customer_id: str

class PredictInput(BaseModel):
    customer_id: str
    aadhar_no: str | None = None
    pan_no: str | None = None
    name: str | None = None
    monthly_salary: float | None = None
    loan_amount: float | None = None
    current_salary_delay_days: int | None = None

class PatternInput(BaseModel):
    amounts: List[float]

class CustomerListInput(BaseModel):
    risk_filter: str | None = "All"

class ExecuteInput(BaseModel):
    customer_id: str
    offer_id: str

@bentoml.service(
    name="bank_risk_service",
    traffic={"timeout": 60}
)
class BankRiskService:
    
    @bentoml.api
    async def execute_intervention(self, input_data: ExecuteInput) -> Dict[str, Any]:
        """
        Executes a recommended intervention for a customer.
        In a real scenario, this would trigger SMS, Email, or Webhook.
        """
        return {
            "status": "success",
            "message": f"Intervention {input_data.offer_id} triggered for {input_data.customer_id}",
            "timestamp": datetime.now().isoformat()
        }

    @bentoml.api
    async def list_customers(self, input_data: CustomerListInput) -> Dict[str, Any]:
        """
        Returns a sample of customers enriched with ensemble risk scores.
        Supports server-side filtering by Risk Level.
        """
        return feature_store.get_customers(limit=1000, risk_filter=input_data.risk_filter)

    @bentoml.api
    async def get_customer(self, input_data: RiskInput) -> Dict[str, Any]:
        """
        Restored Legacy endpoint for direct customer lookup.
        """
        if not input_data.customer_id: return {"error": "customer_id required"}
        customer = feature_store.get_customer_by_id(input_data.customer_id)
        return customer if customer else {"error": "Customer not found"}

    @bentoml.api
    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        Aggregated stats from the enterprise data lake.
        """
        return feature_store.get_dashboard_stats()

    @bentoml.api
    async def predict_risk(self, input_data: PredictInput) -> Dict[str, Any]:
        """
        Restored Legacy endpoint for individual prediction.
        Now uses the unified risk scoring logic.
        """
        # Convert Pydantic to dict for feature store compatibility
        data_dict = input_data.dict()
        risk = feature_store.calculate_risk_score(data_dict)
        return {
            "risk_score": risk['score'],
            "risk_level": risk['level'],
            "details": "Real-time sync with Enterprise Scoring Engine"
        }

    @bentoml.api
    async def analyze_pattern(self, input_data: PatternInput) -> Dict[str, Any]:
        """
        Restored Legacy endpoint for transaction pattern analysis.
        """
        amounts = input_data.amounts
        if not amounts: return {"pattern": "insufficient_data"}
        
        # Simple pattern logic preserved from earlier stable version
        std = np.std(amounts)
        mean = np.mean(amounts)
        is_volatile = std > (mean * 0.5)
        
        return {
            "pattern": "high_volatility" if is_volatile else "stable",
            "volatility_index": round(float(std / mean) if mean > 0 else 0, 2)
        }

    @bentoml.api
    async def analyze_customer_risk(self, input_data: RiskInput) -> Dict[str, Any]:
        """
        The Master Orchestrator for the Complete EWS Flow.
        - Fetches 150+ Features
        - Runs Multi-Agent ML Ensemble
        - Resolves Context & Rare Cases
        - Generates Personalised Interventions
        """
        if not input_data.customer_id:
            return {"error": "customer_id required"}
            
        detailed_data = feature_store.get_customer_detailed(input_data.customer_id)
        if not detailed_data:
            return {"error": "Customer not found"}
        
        features = detailed_data['features']
        core = detailed_data['core']
        
        # Multi-Agent ML
        ml_result = risk_engine.predict_ensemble(features)
        
        # Decision Context
        context = context_solver.resolve_context(features, ml_result)
        
        # Unify Risk Thresholds: High >= 45, Critical >= 85
        score = ml_result['fusion_score']
        legacy_score = detailed_data.get('legacy_score', 0)
        display_score = max(score, legacy_score)
        
        # Interventions (Now aware of the final Unified Score)
        intervention = intervention_engine.generate_intervention(input_data.customer_id, features, ml_result, context, display_score)
        
        risk_level = "Critical" if display_score >= 85 else "High" if display_score >= 45 else "Medium" if display_score >= 30 else "Low"

        return {
            "customer_info": core,
            "risk_analysis": {
                "score": display_score,
                "fusion_score": score,
                "legacy_score": legacy_score,
                "level": risk_level,
                "confidence": ml_result['confidence_score'],
                "agent_contributions": ml_result['agent_scores'],
                "agent_reasoning": ml_result['agent_reasoning']
            },
            "decision_intelligence": context,
            "intervention": intervention,
            "repayment_stats": detailed_data.get('repayment_stats', {}),
            "explained_features": {k: v for i, (k, v) in enumerate(features.items()) if i < 50}
        }
# Restarting...

