import random

class GenAI:
    """
    Simulates a Generative AI Agent for Risk Explainability.
    In a production system, this would wrap calls to GPT-4, Gemini, or a local LLM like Llama 3.
    """
    
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
