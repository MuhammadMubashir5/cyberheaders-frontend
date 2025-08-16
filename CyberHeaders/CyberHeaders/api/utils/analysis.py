import logging
from datetime import datetime, timezone
from .headers import fetch_headers_and_content, analyze_headers
from .ssl import ssl_scan
from .dns import dns_scan
from .wordpress import check_wordpress, analyze_wordpress_headers
from .gemini import generate_gemini_analysis
from ..exceptions import AnalysisError  # Added import
from inspect import iscoroutinefunction

logger = logging.getLogger(__name__)

async def analyze_website(url, include_gemini_analysis=False, deep_scan=False):
    try:
        # Always async
        headers, body = await fetch_headers_and_content(url)

        header_analysis = analyze_headers(headers)  # sync

        # ssl_scan may be async or sync
        if iscoroutinefunction(ssl_scan):
            ssl_analysis = await ssl_scan(url)
        else:
            ssl_analysis = ssl_scan(url)

        # dns_scan may be async or sync
        if deep_scan:
            if iscoroutinefunction(dns_scan):
                dns_analysis = await dns_scan(url)
            else:
                dns_analysis = dns_scan(url)
        else:
            dns_analysis = {}

        is_wordpress = check_wordpress(headers, body)
        if is_wordpress:
            header_analysis["wordpress_issues"] = analyze_wordpress_headers(headers, body)

        security_score, score_breakdown = calculate_security_score(header_analysis, ssl_analysis)
        risk_level = "High" if security_score < 40 else "Medium" if security_score < 70 else "Low"
        recommendations = generate_recommendations(header_analysis, ssl_analysis)
        passed_checks, failed_checks = categorize_checks(header_analysis, ssl_analysis)

        response_data = {
            "url": url,
            "status_code": 200,
            "security_score": security_score,
            "score_breakdown": score_breakdown,
            "headers": headers,
            "analysis": header_analysis,
            "ssl": ssl_analysis,
            "dns": dns_analysis,
            "recommendations": recommendations,
            "passed_checks": passed_checks,
            "failed_checks": failed_checks,
            "risk_level": risk_level,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if include_gemini_analysis:
            try:
                response_data["gemini_analysis"] = generate_gemini_analysis(response_data)
            except Exception as e:
                response_data["gemini_analysis"] = f"Gemini analysis failed: {str(e)}"

        return response_data

    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise AnalysisError(f"Analysis failed: {str(e)}")

def calculate_security_score(header_analysis, ssl_analysis):
    score = 100
    breakdown = {
        "headers": 40,
        "ssl": 30,
        "cookies": 15,
        "cors": 10,
        "wordpress": 5
    }

    # Deduct for missing headers
    missing_penalty = len(header_analysis["missing_essential"]) * 3
    score -= missing_penalty
    breakdown["headers"] -= missing_penalty

    # Deduct for deprecated headers
    deprecated_penalty = len(header_analysis["deprecated"]) * 2
    score -= deprecated_penalty
    breakdown["headers"] -= deprecated_penalty

    # Deduct for other issues
    score -= len(header_analysis["csp_issues"]) * 2
    score -= len(header_analysis["cookie_issues"]) * 2
    score -= len(header_analysis["cors_issues"]) * 2
    score -= len(header_analysis["hsts_issues"]) * 2

    # SSL penalties
    if ssl_analysis.get("weak_ciphers"):
        ssl_penalty = len(ssl_analysis["weak_ciphers"]) * 3
        score -= ssl_penalty
        breakdown["ssl"] -= ssl_penalty

    if ssl_analysis.get("compression_enabled"):
        score -= 10
        breakdown["ssl"] -= 10

    # WordPress specific penalties
    if "wordpress_issues" in header_analysis:
        wp_penalty = len(header_analysis["wordpress_issues"]) * 2
        score -= wp_penalty
        breakdown["wordpress"] -= wp_penalty

    # Ensure no negative scores
    score = max(score, 0)
    for k in breakdown:
        breakdown[k] = max(breakdown[k], 0)

    return score, breakdown


def generate_recommendations(header_analysis, ssl_analysis):
    recommendations = []

    # Header recommendations
    for header in header_analysis["missing_essential"]:
        recommendations.append(f"Add missing security header: {header}")

    for header in header_analysis["deprecated"]:
        recommendations.append(f"Remove deprecated header: {header}")

    for issue in header_analysis["csp_issues"]:
        recommendations.append(f"CSP issue: {issue}")

    for issue in header_analysis["cookie_issues"]:
        recommendations.append(f"Cookie security issue: {issue}")

    for issue in header_analysis["cors_issues"]:
        recommendations.append(f"CORS issue: {issue}")

    for issue in header_analysis["hsts_issues"]:
        recommendations.append(f"HSTS issue: {issue}")

    # WordPress specific recommendations
    if "wordpress_issues" in header_analysis:
        for issue in header_analysis["wordpress_issues"]:
            recommendations.append(f"WordPress issue: {issue}")

    # SSL recommendations
    if ssl_analysis.get("weak_ciphers"):
        recommendations.append("Disable weak cipher suites: " + ", ".join(ssl_analysis["weak_ciphers"]))

    if ssl_analysis.get("compression_enabled"):
        recommendations.append("Disable TLS compression (CRIME vulnerability risk)")

    if "error" in ssl_analysis:
        recommendations.append(f"Fix SSL error: {ssl_analysis['error']}")

    return recommendations


def categorize_checks(header_analysis, ssl_analysis):
    passed = []
    failed = []

    # Header checks
    essential_headers = [
        "content-security-policy",
        "x-content-type-options",
        "x-frame-options",
        "strict-transport-security"
    ]

    for header in essential_headers:
        if header not in header_analysis["missing_essential"]:
            passed.append(f"Header present: {header}")
        else:
            failed.append(f"Header missing: {header}")

    # SSL checks
    if not ssl_analysis.get("weak_ciphers"):
        passed.append("No weak cipher suites")
    else:
        failed.append(f"Weak ciphers found: {', '.join(ssl_analysis['weak_ciphers'])}")

    if not ssl_analysis.get("compression_enabled"):
        passed.append("TLS compression disabled")
    else:
        failed.append("TLS compression enabled (CRIME vulnerability risk)")

    return passed, failed