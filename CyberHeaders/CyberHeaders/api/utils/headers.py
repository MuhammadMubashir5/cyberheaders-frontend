import re
import httpx
import logging
from django.conf import settings
from ..exceptions import RequestFailedError

logger = logging.getLogger(__name__)

async def fetch_headers_and_content(url):
    async with httpx.AsyncClient(timeout=settings.SCAN_TIMEOUT) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return {k.lower(): v for k, v in response.headers.items()}, response.text
        except httpx.HTTPError as e:
            raise RequestFailedError(f"Request to target website failed: {str(e)}")

def analyze_headers(headers):
    analysis = {
        "missing_essential": [],
        "deprecated": [],
        "insecure": [],
        "csp_issues": [],
        "cookie_issues": [],
        "cors_issues": [],
        "hsts_issues": [],
        "additional_headers": check_additional_headers(headers),
        "owasp_compliance": check_owasp_compliance(headers)
    }

    # Essential headers check
    essential_headers = [
        "content-security-policy",
        "x-content-type-options",
        "x-frame-options",
        "strict-transport-security",
        "x-xss-protection",
        "referrer-policy",
        "permissions-policy",
        "cross-origin-opener-policy",
        "cross-origin-embedder-policy",
        "cross-origin-resource-policy"
    ]
    analysis["missing_essential"] = [h for h in essential_headers if h not in headers]

    # Deprecated headers check
    deprecated_headers = [
        "public-key-pins",
        "x-aspnet-version",
        "x-powered-by",
        "server",
        "x-webkit-csp",
        "x-content-security-policy"
    ]
    analysis["deprecated"] = [h for h in deprecated_headers if h in headers]

    # Specific header analysis
    if "content-security-policy" in headers:
        analysis["csp_issues"] = analyze_csp(headers["content-security-policy"])

    if "set-cookie" in headers:
        analysis["cookie_issues"] = analyze_cookies(headers["set-cookie"])

    if "access-control-allow-origin" in headers:
        analysis["cors_issues"] = analyze_cors(headers["access-control-allow-origin"])

    if "strict-transport-security" in headers:
        analysis["hsts_issues"] = analyze_hsts(headers["strict-transport-security"])

    return analysis

def analyze_csp(csp_header):
    issues = []
    unsafe_directives = ["unsafe-inline", "unsafe-eval", "unsafe-hashes"]
    important_directives = ["default-src", "script-src", "object-src", "base-uri"]
    permissive_sources = ["*", "'unsafe-inline'", "data:", "http:", "ftp:"]

    for directive in unsafe_directives:
        if directive in csp_header:
            issues.append(f"CSP contains unsafe directive: {directive}")

    for directive in important_directives:
        if f"{directive}" not in csp_header:
            issues.append(f"CSP missing important directive: {directive}")

    for source in permissive_sources:
        if source in csp_header:
            issues.append(f"CSP contains overly permissive source: {source}")

    return issues

def analyze_cookies(cookie_header):
    issues = []
    cookies = [c.strip() for c in cookie_header.split(";")]

    if not any("secure" in c.lower() for c in cookies):
        issues.append("Missing Secure flag")

    if not any("httponly" in c.lower() for c in cookies):
        issues.append("Missing HttpOnly flag")

    samesite = next((c for c in cookies if "samesite" in c.lower()), None)
    if not samesite:
        issues.append("Missing SameSite attribute")
    elif "samesite=none" in samesite.lower() and not any("secure" in c.lower() for c in cookies):
        issues.append("SameSite=None without Secure flag")

    if any("domain=" in c.lower() for c in cookies):
        issues.append("Overly broad domain setting")

    return issues

def analyze_cors(acao_header):
    issues = []
    if acao_header == "*":
        issues.append("Overly permissive CORS policy: Access-Control-Allow-Origin: *")
    return issues

def analyze_hsts(hsts_header):
    issues = []
    if "max-age" not in hsts_header:
        issues.append("HSTS missing max-age directive")
    else:
        max_age_match = re.search(r"max-age=(\d+)", hsts_header)
        if max_age_match:
            max_age = int(max_age_match.group(1))
            if max_age < 31536000:
                issues.append(f"HSTS max-age too short: {max_age} (should be at least 31536000)")

    if "includesubdomains" not in hsts_header.lower():
        issues.append("HSTS missing includeSubDomains directive")
    return issues

def check_additional_headers(headers):
    return {
        "clear_site_data": "clear-site-data" in headers,
        "report_to": "report-to" in headers,
        "feature_policy": "feature-policy" in headers,
        "expect_ct": "expect-ct" in headers
    }

def check_owasp_compliance(headers):
    return {
        "content_security_policy": "content-security-policy" in headers,
        "x_content_type_options": headers.get("x-content-type-options", "").lower() == "nosniff",
        "x_frame_options": "x-frame-options" in headers,
        "strict_transport_security": "strict-transport-security" in headers,
        "x_xss_protection": "x-xss-protection" in headers,
        "referrer_policy": "referrer-policy" in headers,
        "permissions_policy": "permissions-policy" in headers,
        "cross_origin_opener_policy": "cross-origin-opener-policy" in headers,
        "cross_origin_embedder_policy": "cross-origin-embedder-policy" in headers,
        "cross_origin_resource_policy": "cross-origin-resource-policy" in headers
    }