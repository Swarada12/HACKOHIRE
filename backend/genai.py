import os
import requests
import json
import random

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
        self.model = self.models[0]

    def generate_intervention(self, context: dict) -> str:
        """
        Generates a persuasive, empathetic intervention message.
        Prioritizes Direct Gemini API if key is available.
        """
        # 1. Try Direct Google Gemini API first (Most Reliable)
        if self.gemini_key:
            try:
                return self._call_google_gemini(context)
            except Exception as e:
                print(f"Direct Gemini API Failed: {e}")
                # Fallthrough to OpenRouter

        # 2. Try OpenRouter
        if not self.api_key:
            return self._fallback_simulation(context)
            
        prompt = self._construct_prompt(context)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://hackohire.com", 
            "X-Title": "BankRiskEngine"
        }
        
        payload = {
            "messages": [
                {"role": "system", "content": "You are an empathetic, professional banking assistant. Avoid markdown formatting."},
                {"role": "user", "content": prompt}
            ]
        }
        
        # Try models in sequence
        for model in self.models:
            try:
                payload["model"] = model
                response = requests.post(self.api_url, headers=headers, data=json.dumps(payload), timeout=8)
                
                if response.status_code == 200:
                    result = response.json()
                    return result['choices'][0]['message']['content'].strip()
                else:
                    print(f"GenAI Model {model} Failed ({response.status_code}): {response.text}")
                    continue # Try next model
            except Exception as e:
                print(f"GenAI Model {model} Error: {e}")
                continue
                
        # All failed
        print("GenAI: All models failed or timed out. Switching to deterministic fallback.")
        return self._fallback_simulation(context)

    def _call_google_gemini(self, context: dict) -> str:
        """
        Direct calls to Google's Generative Language API.
        Uses Dynamic Model Discovery to find a working model.
        """
        prompt = self._construct_prompt(context)
        
        # 1. Dynamically fetch available models
        try:
            list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={self.gemini_key}"
            list_resp = requests.get(list_url, timeout=5)
            
            working_model = "gemini-2.0-flash-exp" # Updated default fallback
            
            if list_resp.status_code == 200:
                data = list_resp.json()
                # Find first model that supports generateContent
                for m in data.get('models', []):
                    if "generateContent" in m.get('supportedGenerationMethods', []):
                        name = m['name'].split('/')[-1] # Remove 'models/' prefix
                        # Prefer lightweight models for speed
                        if 'flash' in name:
                            working_model = name
                            break
                        if 'pro' in name and working_model == "gemini-1.5-flash":
                            working_model = name
                            
                print(f"GenAI: Discovered working model: {working_model}")
            else:
                print(f"GenAI: Failed to list models ({list_resp.status_code}). Using default: {working_model}")

        except Exception as e:
            print(f"GenAI Discovery Failed: {e}")
            working_model = "gemini-1.5-flash"

        # 2. Call the discovered model
        payload = {
            "contents": [{
                "parts": [{"text": "You are an empathetic banking assistant. Keep it short (max 2 sentences). " + prompt}]
            }]
        }
        
        try:
            # Use the dynamically discovered model
            print(f"GenAI: Using model {working_model}")
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{working_model}:generateContent?key={self.gemini_key}"
            response = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload), timeout=8)
            
            if response.status_code == 200:
                data = response.json()
                return data['candidates'][0]['content']['parts'][0]['text'].strip()
            else:
                # Fallback to pure simulation if API fails (Don't crash)
                print(f"GenAI API Error with model {working_model} ({response.status_code}): {response.text}")
                return self._fallback_simulation(context)
                
        except Exception as e:
            print(f"GenAI Exception: {e}")
            return self._fallback_simulation(context)

    def _construct_prompt(self, context: dict) -> str:
        name = context.get('name', 'Customer')
        risk_score = context.get('risk_score', 0)
        spending_gap = context.get('spending_gap', 0)
        offer = context.get('offer', 'Financial Review')
        
        return f"""
        Draft a short, urgent yet polite intervention message for {name}.
        Context:
        - Risk Score: {risk_score}/100 (High Risk)
        - Financial Issue: Spending gap of Rs.{spending_gap} detected this month.
        - Solution/Offer: {offer}.
        
        Write a message (SMS/WhatsApp style) urging them to accept the offer to avoid penalties.
        """

    def _fallback_simulation(self, context: dict) -> str:
        """
        Fallback for when API is unavailable.
        """
        name = context.get('name', 'Customer')
        offer = context.get('offer', 'Assistance')
        return f"Hi {name}, our systems detected a potential shortfall. To avoid penalties, we recommend: {offer}. Reply YES to activate."

    def explain_risk(self, risk_score: int, risk_level: str, factors: list, customer_name: str) -> str:
        
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
            feat = f['feature']
            val = f['value']
            if feat == "Salary Delay":
                factor_analysis.append(f"detected a significant delay in salary credits ({val:.0f} days), which is a primary indicator of liquidity stress.")
            elif feat == "Failed Debits":
                factor_analysis.append(f"observed {val:.0f} recent failed auto-debits, suggesting potential cash flow gaps.")
            elif feat == "Credit Util":
                factor_analysis.append(f"noted high credit utilization ({val:.0f}%), indicating reliance on credit lines.")
            elif feat == "Savings Trend":
                factor_analysis.append(f"identified a concerning depletion in savings reserves.")
            else:
                factor_analysis.append(f"highlighted {feat} as a contributing risk factor.")
                
        analysis_text = " ".join(factor_analysis)
        
        conclusion = ""
        if risk_score > 70:
            conclusion = "Immediate proactive intervention is recommended to prevent default. Consider offering a payment restructuring plan."
        elif risk_score > 40:
            conclusion = "Monitoring is advised. A courtesy call to discuss financial wellness may be beneficial."
        else:
            conclusion = "The customer's financial health appears stable with no immediate signs of distress."
            
        return f"**AI Risk Analysis**:\n\n{intro} determined a **{risk_level} Risk Level** ({risk_score}/100).\n\nThe model {analysis_text}\n\n**Recommendation**:\n{conclusion}"
