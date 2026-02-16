import bentoml
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
    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        Aggregated stats from the enterprise data lake.
        """
        return feature_store.get_dashboard_stats()

    @bentoml.api
    async def analyze_customer_risk(self, input_data: Dict[str, str]) -> Dict[str, Any]:
        """
        The Master Orchestrator for the Complete EWS Flow.
        - Fetches 150+ Features
        - Runs Multi-Agent ML Ensemble
        - Resolves Context & Rare Cases
        - Generates Personalised Interventions
        - Provides explainability context
        """
        customer_id = input_data.get('customer_id')
        if not customer_id:
            return {"error": "customer_id required"}
            
        # 1. Feature Engineering (Phase 2)
        detailed_data = feature_store.get_customer_detailed(customer_id)
        if not detailed_data:
            return {"error": "Customer not found"}
        
        features = detailed_data['features']
        core = detailed_data['core']
        
        # 2. Multi-Agent ML Execution (Phase 3)
        ml_result = risk_engine.predict_ensemble(features)
        
        # 3. Decision Intelligence & Context (Phase 4)
        context = context_solver.resolve_context(features, ml_result)
        
        # 4. Intervention Generation (Phase 5)
        intervention = intervention_engine.generate_intervention(customer_id, features, ml_result, context)
        
        # 5. Integration & Explainability
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
            "explained_features": {k: v for i, (k, v) in enumerate(features.items()) if i < 15} # Top 15 for UI
        }
