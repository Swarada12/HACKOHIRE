import os
import requests
import json
import random
from dotenv import load_dotenv

load_dotenv()
load_dotenv("backend/.env")

class GenAI:
    """
    Generative AI Wrapper using OpenRouter API.
    Interacts with LLMs (e.g., Mistral, Llama 3, GPT-4) for hyper-personalized banking interventions.
    """
    
    def __init__(self):
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.api_key = os.environ.get("OPENROUTER_API_KEY")
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.models = [
            "google/gemini-2.0-flash-lite-preview-02-05:free",
            "google/gemini-2.0-pro-exp-02-05:free",
            "huggingfaceh4/zephyr-7b-beta:free",
            "mistralai/mistral-7b-instruct:free",
            "gryphe/mythomax-l2-13b:free",
            "openrouter/auto"
        ]
        self.model = "gemini-1.5-flash" # Default working model

    def generate_intervention(self, context: dict) -> str:
        """
        Generates a persuasive, empathetic intervention message.
        """
        prompt = self._construct_prompt(context)
        res = self._ask_llm(prompt)
        return res if res else self._fallback_simulation(context)

    def _ask_llm(self, prompt: str, system_msg: str = "You are an empathetic, professional banking assistant.") -> str:
        """
        Unified method to call LLMs with discovery and failover.
        """
        # 1. Try Google Gemini (Direct API) - Optimized
        if self.gemini_key:
            try:
                # Use a reliable model directly instead of discovery every time
                working_model = "gemini-1.5-flash"
                payload = {
                    "contents": [{
                        "parts": [{"text": f"{system_msg} {prompt}"}]
                    }]
                }
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{working_model}:generateContent?key={self.gemini_key}"
                response = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload), timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    return data['candidates'][0]['content']['parts'][0]['text'].strip()
                else:
                    print(f"GenAI Gemini Error {response.status_code}: {response.text[:100]}")
            except Exception as e:
                print(f"GenAI Direct Gemini Failed: {e}")

        # 2. Try OpenRouter (Failover) - Only first 2 models to save time
        if self.api_key:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://hackohire.com",
                "X-Title": "BankRiskEngine"
            }
            payload = {
                "messages": [
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt}
                ]
            }
            # Only try the fastest models
            for model in self.models[:2]:
                try:
                    payload["model"] = model
                    response = requests.post(self.api_url, headers=headers, data=json.dumps(payload), timeout=5)
                    if response.status_code == 200:
                        result = response.json()
                        return result['choices'][0]['message']['content'].strip()
                except Exception:
                    continue

        return "" # All APIs failed

    def _construct_prompt(self, context: dict) -> str:
        name = context.get('name', 'Customer')
        risk_score = context.get('risk_score', 0)
        spending_gap = context.get('spending_gap', 0)
        offer = context.get('offer', 'Financial Review')
        shap_factors = context.get('shap_explanation', [])
        
        # Build insight string from SHAP
        insights = []
        for f in shap_factors[:3]:
            feat = f['feature'].replace('_', ' ')
            impact = "positive" if f['impact'] > 0 else "negative"
            # Only mention significant drivers
            if abs(f['impact']) > 0.05:
                insights.append(f"{feat} (Model contribution: {f['impact']:.2f})")
        
        insight_str = ", ".join(insights) if insights else "general financial volatility"

        return f"""
        Draft a short, empathetic yet urgent message for {name}.
        The bank's AI Risk Ensemble (XGBoost/LSTM) has flagged the following profile details:
        - Risk Score: {risk_score}/100
        - Top Model Drivers (SHAP): {insight_str}
        - Detected Liquidity Gap: Rs.{spending_gap}
        - Recommended Action: {offer}
        
        Instruction: Write a professional SMS/WhatsApp message (max 2 sentences) that encourages them to accept the {offer} to protect their credit standing. Mention that an AI audit detected these specific patterns.
        """

    def _fallback_simulation(self, context: dict) -> str:
        """
        Fallback for when API is unavailable.
        """
        name = context.get('name', 'Customer')
        offer = context.get('offer', 'Assistance')
        return f"Hi {name}, our systems detected a potential shortfall. To avoid penalties, we recommend: {offer}. Reply YES to activate."

    def _construct_narrative_prompt(self, risk_score: int, risk_level: str, factors: list, customer_name: str) -> str:
        factor_str = "\n".join([f"- {f['feature']}: {f['value']}" for f in factors])
        return f"""
        Act as a Senior Risk Analyst for a premium bank. 
        Write a 2-3 sentence executive summary explaining why {customer_name} has been flagged as {risk_level} Risk with a score of {risk_score}/100.
        
        Key Drivers identified by AI Ensemble:
        {factor_str}
        
        Requirements:
        1. Be professional, data-centric, and executive-ready.
        2. Do not use generic filler. Mention specific data points if they indicate stress.
        3. Use a varied sentence structure. 
        4. Focus on the causal relationship between the drivers and the risk level.
        """

    def explain_risk(self, risk_score: int, risk_level: str, factors: list, customer_name: str) -> str:
        """
        Generates a natural language executive summary of risk.
        Now uses TRUE LLM generation.
        """
        prompt = self._construct_narrative_prompt(risk_score, risk_level, factors, customer_name)
        res = self._ask_llm(prompt, system_msg="You are a Senior Risk Analyst.")
        
        if res:
             return f"**AI Risk Analysis**:\n\n{res}"

        # Fallback to Template
        return self._explain_risk_deterministic(risk_score, risk_level, factors, customer_name)

    def _explain_risk_deterministic(self, risk_score: int, risk_level: str, factors: list, customer_name: str) -> str:
        
        # Templates for natural language generation
        intros = [
            f"Based on a comprehensive analysis of {customer_name}'s financial profile,",
            f"Our AI risk engine has evaluated {customer_name}'s recent activity and",
            f"The early warning system has flagged this profile."
        ]
        
        intro = random.choice(intros)
        
        # Analysis of key factors
        factor_analysis = []
        for f in factors[:3]: # Top 3 drivers
            feat = f['feature'].lower()
            val = f['value']
            
            if "delay" in feat:
                factor_analysis.append(f"detected a significant delay in salary credits ({val:.0f} days), which is a primary indicator of liquidity stress.")
            elif "debit" in feat or "bounce" in feat:
                 factor_analysis.append(f"observed {val:.0f} recent failed auto-debits, suggesting potential cash flow gaps.")
            elif "util" in feat:
                 factor_analysis.append(f"noted high credit utilization ({val:.0f}%), indicating reliance on credit lines.")
            elif "savings" in feat or "balance" in feat:
                 factor_analysis.append(f"identified a concerning depletion in savings reserves.")
            elif "gambling" in feat:
                 factor_analysis.append(f"flagged high-frequency discretionary outflows to high-risk categories.")
            else:
                factor_analysis.append(f"highlighted {feat} as a contributing risk factor.")
                
        if not factor_analysis:
            factor_analysis.append("identified unusual patterns in transaction velocity and credit behavior.")
            
        analysis_text = " ".join(factor_analysis)
        
        conclusion = ""
        if risk_score > 70:
            conclusion = "Immediate proactive intervention is recommended to prevent default. Consider offering a payment restructuring plan."
        elif risk_score > 40:
            conclusion = "Monitoring is advised. A courtesy call to discuss financial wellness may be beneficial."
        else:
            conclusion = "The customer's financial health appears stable with no immediate signs of distress."
            
        return f"**AI Risk Analysis (Deterministic Fallback)**:\n\n{intro} determined a **{risk_level} Risk Level** ({risk_score}/100).\n\nThe model {analysis_text}\n\n**Recommendation**:\n{conclusion}"
