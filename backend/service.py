import bentoml
import asyncio
import numpy as np
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
load_dotenv() # Load environment variables from .env BEFORE other imports
from feature_store import FeatureStore
from ml_engine import MLRiskEngine, RareCaseSolver
from intervention_engine import InterventionEngine
from genai import GenAI
from typing import Dict, Any, List

# Initialize Core Components
feature_store = FeatureStore()
risk_engine = MLRiskEngine()
context_solver = RareCaseSolver()
intervention_engine = InterventionEngine()
# GenAI can be slow / network-bound. Keep it strictly on-demand.
genai_engine = None

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
    search: str | None = ""
    enrich_ml: bool = False
    limit: int = 500

class ExecuteInput(BaseModel):
    customer_id: str
    offer_id: str

@bentoml.service(
    name="bank_risk_service",
    traffic={"timeout": 60}
)
class BankRiskService:
    def sync_pending_customers(self):
        """
        Just-In-Time (JIT) Sync:
        Detects customers added manually to DB and runs AI inference.
        """
        conn = feature_store.get_conn()
        try:
            # Find users with NULL or 0 score (newly added via DB)
            pending = pd.read_sql_query("SELECT customer_id FROM customers WHERE risk_score IS NULL OR risk_score <= 0", conn)
            cids = pending['customer_id'].tolist()
            
            if not cids:
                return

            print(f"JIT Sync: Detected {len(cids)} new customers. Running AI Ensemble...")
            cursor = conn.cursor()
            for cid in cids:
                detailed = feature_store.get_customer_detailed(cid)
                if not detailed:
                    continue
                
                features = detailed.get('features', {})
                
                # Run Ensemble
                res = risk_engine.predict_ensemble(features)
                score = int(res['fusion_score'])
                level = "Critical" if score >= 85 else "High" if score >= 45 else "Medium" if score >= 30 else "Low"
                
                # Persist Real-Time
                cursor.execute("UPDATE customers SET risk_score = ?, risk_level = ? WHERE customer_id = ?", (score, level, cid))
            
            conn.commit()
        except Exception as e:
            print(f"JIT Sync Error: {e}")
        finally:
            conn.close()

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
        Returns customers from the DB, with optional ML enrichment.
        """
        risk_filter = input_data.risk_filter
        search = input_data.search
        enrich_ml = input_data.enrich_ml
        limit = input_data.limit
        
        print(f"DEBUG: Processing list_customers request: {input_data}")
        try:
             result = feature_store.get_customers(
                limit=limit, 
                risk_filter=risk_filter,
                search=search
            )
             print(f"DEBUG: Fetched {len(result.get('customers', []))} customers from DB")
        except Exception as e:
             print(f"DEBUG: Error fetching customers: {e}")
             return {"error": str(e)}

        if enrich_ml:
            customers = result.get("customers", [])
            # Optimization: For large lists, perform deep ML enrichment only for the top 50 critical cases
            # to maintain high performance while providing deep insights where they matter most.
            enrich_limit = 50 if len(customers) > 100 else len(customers)
            
            print(f"DEBUG: enrich_ml enabled → deep enriching top {enrich_limit} of {len(customers)} customers")
            
            for i, c in enumerate(customers):
                if i >= enrich_limit:
                    break
                    
                cid = c.get("customer_id")
                if not cid:
                    continue
                try:
                    detailed = feature_store.get_customer_detailed(cid)
                    if not detailed:
                        continue
                    features = detailed.get("features", {})
                    ml = risk_engine.predict_ensemble(features, customer_id=cid)

                    reasoning = ml.get("agent_reasoning", {})
                    ml_signals = [] 
                    found_deep_insight = False
                    for _, reasons in reasoning.items():
                        for r in reasons:
                            if ("Flag" in r or "Insight" in r) and "stable" not in r.lower() and "normal range" not in r.lower() and "acceptable" not in r.lower():
                                ml_signals.append(f"🧠 {r}")
                                found_deep_insight = True
                    
                    # Merge Strategy: If we have deep ML signals, we replace the basic heuristics
                    # to keep the dashboard clean and "high-IQ" as per user request.
                    if found_deep_insight:
                        c["signals"] = ml_signals
                    else:
                        # Keep heuristics but maybe filter them if too many
                        c["signals"] = c.get("signals", [])[:3] 

                    # Sync scores (using MAX logic)
                    ml_score = int(ml.get("fusion_score", 0))
                    db_score = int(c.get("risk_score", 0))
                    c["risk_score"] = max(ml_score, db_score)
                    
                    score = c["risk_score"]
                    c["risk_level"] = "Critical" if score >= 85 else "High" if score >= 45 else "Medium" if score >= 30 else "Low"

                    scores = ml.get("agent_scores", {})
                    c["agent_scores"] = {
                        "xgboost": scores.get("xgboost_risk", 0),
                        "lightgbm": scores.get("lightgbm_risk", 0),
                        "lstm": scores.get("lstm_pattern", 0),
                    }
                except Exception as e:
                    print(f"ML signal enrich error for {cid}: {e}")

            # Re-sort by Real-Time Risk Score to ensure "Critical" comes first
            customers.sort(key=lambda x: x.get("risk_score", 0), reverse=True)
            
        return result

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
        # self.sync_pending_customers()
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
        ml_result = risk_engine.predict_ensemble(features, customer_id=input_data.customer_id)
        
        # Decision Context
        context = context_solver.resolve_context(features, ml_result, customer_id=input_data.customer_id)
        
        # Unify Risk Thresholds: High >= 45, Critical >= 85
        score = ml_result['fusion_score']
        legacy_score = detailed_data.get('legacy_score', 0)
        display_score = max(score, legacy_score)
        
        # Interventions (Now aware of the final Unified Score)
        intervention = intervention_engine.generate_intervention(input_data.customer_id, features, ml_result, context, display_score)
        
        # GenAI PERSONALIZATION (Model-to-Human Bridge) - MOVED TO ON-DEMAND ENDPOINT
        # Returning placeholders to save latency/tokens
        risk_level = "Critical" if display_score >= 85 else "High" if display_score >= 45 else "Medium" if display_score >= 30 else "Low"
        genai_narrative = "" # Placeholder
        intervention['message'] = intervention.get('message', "Click 'Generate AI Insights' to synthesize personalized intervention.")
            
        print(f"DEBUG: genai_narrative produced: {len(genai_narrative) if genai_narrative else 0} chars")
        if not genai_narrative:
             print(f"WARNING: Narrative empty for {core.get('name')}")

        agent_scores = ml_result.get('agent_scores', {})
        return {
            "customer_info": core,
            "risk_analysis": {
                "score": display_score,
                "fusion_score": score,
                "legacy_score": legacy_score,
                "level": risk_level,
                "confidence": ml_result.get('confidence_score', 0.75),
                "agent_contributions": {
                    "financial": agent_scores.get('xgboost_risk', 0),
                    "behavioral": agent_scores.get('lightgbm_risk', 0),
                    "velocity": agent_scores.get('lstm_pattern', 0)
                },
                "agent_reasoning": ml_result.get('agent_reasoning', {}),
                "genai_narrative": genai_narrative
            },
            "decision_intelligence": context,
            "intervention": intervention,
            "repayment_stats": detailed_data.get('repayment_stats', {}),
            "explained_features": {k: v for i, (k, v) in enumerate(features.items()) if i < 50}
        }

    @bentoml.api
    async def generate_ai_insights(self, input_data: RiskInput) -> Dict[str, Any]:
        """
        On-Demand GenAI Insight Generation.
        Only called when the user clicks the "Generate AI Insights" button.
        """
        if not input_data.customer_id:
            return {"error": "customer_id required"}
            
        detailed_data = feature_store.get_customer_detailed(input_data.customer_id)
        if not detailed_data:
            return {"error": "Customer not found"}
        
        features = detailed_data['features']
        core = detailed_data['core']
        
        # Re-run Ensemble for fresh insights (or could cache, but this is cleaner)
        ml_result = risk_engine.predict_ensemble(features, customer_id=input_data.customer_id)
        context = context_solver.resolve_context(features, ml_result, customer_id=input_data.customer_id)
        
        score = ml_result['fusion_score']
        legacy_score = detailed_data.get('legacy_score', 0)
        display_score = max(score, legacy_score)
        risk_level = "Critical" if display_score >= 85 else "High" if display_score >= 45 else "Medium" if display_score >= 30 else "Low"
        
        intervention = intervention_engine.generate_intervention(input_data.customer_id, features, ml_result, context, display_score)
        
        shap_factors = ml_result.get('shap_explanation', [])
        top_factors = [{"feature": f['feature'].replace('_', ' ').title(), "value": f['value']} for f in shap_factors[:5]]
        
        # GenAI is on-demand only (lazy init)
        local_genai = GenAI()

        # Prepare parallel tasks
        narrative_task = asyncio.to_thread(local_genai.explain_risk, display_score, risk_level, top_factors, core.get('name', 'Customer'))
        
        genai_context = {
            "name": core.get('name', 'Customer'),
            "risk_score": display_score,
            "spending_gap": intervention.get('spending_gap', 5000), 
            "offer": intervention.get('recommended_offer', 'Financial Advisory'),
            "shap_explanation": shap_factors 
        }
        intervention_task = asyncio.to_thread(local_genai.generate_intervention, genai_context)
        
        # Execute in parallel
        genai_narrative, genai_msg = await asyncio.gather(narrative_task, intervention_task)
        
        return {
            "genai_narrative": genai_narrative,
            "personalized_message": genai_msg
        }
# Restarting...

