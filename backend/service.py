import bentoml
import numpy as np
from feature_store import FeatureStore
from ml_engine import MLRiskEngine, RareCaseSolver
from intervention_engine import InterventionEngine
from typing import Dict, Any, List

# Initialize Core Components
feature_store = FeatureStore()
risk_engine = MLRiskEngine()
context_solver = RareCaseSolver()
intervention_engine = InterventionEngine()

@bentoml.service(
    name="bank_risk_service",
    traffic={"timeout": 60}
)
class BankRiskService:
    
    @bentoml.api
    async def list_customers(self) -> Dict[str, Any]:
        """
        Returns a sample of customers enriched with ensemble risk scores.
        """
        return feature_store.get_customers(limit=100)

    @bentoml.api
    async def get_customer(self, input_data: Dict[str, str]) -> Dict[str, Any]:
        """
        Restored Legacy endpoint for direct customer lookup.
        """
        customer_id = input_data.get('customer_id')
        if not customer_id: return {"error": "customer_id required"}
        customer = feature_store.get_customer_by_id(customer_id)
        return customer if customer else {"error": "Customer not found"}

    @bentoml.api
    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        Aggregated stats from the enterprise data lake.
        """
        return feature_store.get_dashboard_stats()

    @bentoml.api
    async def predict_risk(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Restored Legacy endpoint for individual prediction.
        Now uses the unified risk scoring logic.
        """
        risk = feature_store.calculate_risk_score(input_data)
        return {
            "risk_score": risk['score'],
            "risk_level": risk['level'],
            "details": "Real-time sync with Enterprise Scoring Engine"
        }

    @bentoml.api
    async def analyze_pattern(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Restored Legacy endpoint for transaction pattern analysis.
        """
        amounts = input_data.get('amounts', [])
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
    async def analyze_customer_risk(self, input_data: Dict[str, str]) -> Dict[str, Any]:
        """
        The Master Orchestrator for the Complete EWS Flow.
        - Fetches 150+ Features
        - Runs Multi-Agent ML Ensemble
        - Resolves Context & Rare Cases
        - Generates Personalised Interventions
        """
        customer_id = input_data.get('customer_id')
        if not customer_id:
            return {"error": "customer_id required"}
            
        detailed_data = feature_store.get_customer_detailed(customer_id)
        if not detailed_data:
            return {"error": "Customer not found"}
        
        features = detailed_data['features']
        core = detailed_data['core']
        
        # Multi-Agent ML
        ml_result = risk_engine.predict_ensemble(features)
        
        # Decision Context
        context = context_solver.resolve_context(features, ml_result)
        
        # Interventions
        intervention = intervention_engine.generate_intervention(customer_id, features, ml_result, context)
        
        return {
            "customer_info": core,
            "risk_analysis": {
                "score": ml_result['fusion_score'],
                "level": "Critical" if ml_result['fusion_score'] >= 85 else "High" if ml_result['fusion_score'] >= 60 else "Medium" if ml_result['fusion_score'] >= 35 else "Low",
                "confidence": ml_result['confidence_score'],
                "agent_contributions": ml_result['agent_scores']
            },
            "decision_intelligence": context,
            "intervention": intervention,
            "explained_features": {k: v for i, (k, v) in enumerate(features.items()) if i < 15}
        }
