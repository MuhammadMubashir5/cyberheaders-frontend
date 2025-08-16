import re
import logging

logger = logging.getLogger(__name__)

def check_wordpress(headers, body):
    wordpress_indicators = [
        "x-powered-by" in headers and "wordpress" in headers["x-powered-by"].lower(),
        "link" in headers and "wp-json" in headers["link"].lower(),
        any("wordpress" in v.lower() for v in headers.values()),
        "wp-content" in body.lower(),
        "wp-includes" in body.lower()
    ]
    return any(wordpress_indicators)

def analyze_wordpress_headers(headers, body):
    issues = []
    wordpress_headers = ["x-wp-cron", "x-redirect-by", "x-pingback"]

    for header in wordpress_headers:
        if header in headers:
            issues.append(f"WordPress header exposed: {header}")

    if "x-pingback" in headers:
        issues.append("XML-RPC pingback endpoint exposed (consider disabling if not needed)")

    if "link" in headers and "wp-json" in headers["link"]:
        issues.append("WordPress REST API endpoint exposed (consider restricting access if not needed)")

    if any("admin-ajax.php" in v for v in headers.values()):
        issues.append("WordPress admin-ajax.php endpoint exposed (consider rate limiting)")

    # Check for version leaks in body
    version_patterns = [
        r"wordpress [0-9.]+",
        r"wp-includes/js/wp-embed\.js\?ver=([0-9.]+)",
        r"wp-includes/css/dist/block-library/style\.min\.css\?ver=([0-9.]+)"
    ]

    for pattern in version_patterns:
        match = re.search(pattern, body, re.IGNORECASE)
        if match:
            version = match.group(1) if len(match.groups()) > 0 else match.group(0)
            issues.append(f"WordPress version {version} exposed in HTML")
            break

    return issues