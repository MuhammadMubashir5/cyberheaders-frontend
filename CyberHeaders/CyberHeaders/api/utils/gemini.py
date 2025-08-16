import google.generativeai as genai
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

try:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    logger.info("Successfully initialized Gemini model")
except Exception as e:
    logger.error(f"Failed to initialize Gemini model: {str(e)}")
    gemini_model = None

def generate_gemini_analysis(results):
    if not gemini_model:
        return "Gemini analysis unavailable"

    try:
        prompt = f"""
        Analyze these website security scan results and provide a comprehensive security assessment:

        URL: {results['url']}
        Security Score: {results['security_score']}/100
        Risk Level: {results['risk_level']}

        Key Findings:
        - Missing Headers: {', '.join(results['analysis']['missing_essential']) or 'None'}
        - Deprecated Headers: {', '.join(results['analysis']['deprecated']) or 'None'}
        - CSP Issues: {', '.join(results['analysis']['csp_issues']) or 'None'}
        - WordPress Issues: {', '.join(results['analysis'].get('wordpress_issues', [])) or 'None'}
        - SSL Issues: {results['ssl'].get('error', 'None')}

        Passed Checks:
        {chr(10).join(results['passed_checks'])}

        Failed Checks:
        {chr(10).join(results['failed_checks'])}

        Recommendations:
        {chr(10).join(results['recommendations'])}

        Provide your analysis in this format:
        1. Executive Summary
        2. Critical Vulnerabilities
        3. Security Header Analysis
        4. WordPress-Specific Risks (if applicable)
        5. SSL/TLS Configuration Review
        6. Actionable Recommendations
        7. Overall Risk Assessment
        """

        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini analysis failed: {str(e)}")
        return f"Gemini analysis failed: {str(e)}"