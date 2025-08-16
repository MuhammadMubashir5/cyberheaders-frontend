import ssl
import socket
from datetime import datetime, timezone
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def ssl_scan(url_or_hostname):
    results = {
        "certificate": {},
        "protocols": {},
        "weak_ciphers": [],
        "compression_enabled": False,
        "ocsp_stapling": False,
        "preload_status": "unknown"
    }

    try:
        # Extract hostname from full URL or direct hostname
        parsed = urlparse(url_or_hostname)
        hostname = parsed.hostname if parsed.hostname else url_or_hostname.strip()

        if not hostname:
            raise ValueError("Invalid URL or hostname provided for SSL scan")

        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()

                # Parse certificate dates
                not_after_str = cert.get("notAfter", "")
                if not_after_str:
                    try:
                        cert_expiry = datetime.strptime(not_after_str, "%b %d %H:%M:%S %Y %Z")
                        cert_expiry = cert_expiry.replace(tzinfo=timezone.utc)
                        expires_in_days = (cert_expiry - datetime.now(timezone.utc)).days
                    except Exception as e:
                        expires_in_days = f"error: {str(e)}"
                else:
                    expires_in_days = "unknown"

                results["certificate"] = {
                    "issuer": dict(x[0] for x in cert.get("issuer", [])),
                    "subject": dict(x[0] for x in cert.get("subject", [])),
                    "version": cert.get("version", "unknown"),
                    "serialNumber": cert.get("serialNumber", "unknown"),
                    "notBefore": cert.get("notBefore", "unknown"),
                    "notAfter": not_after_str,
                    "expires_in_days": expires_in_days,
                    "signatureAlgorithm": cert.get("signatureAlgorithm", "unknown")
                }

                # Protocol support (basic check)
                results["protocols"] = {
                    "SSLv2": False,
                    "SSLv3": False,
                    "TLSv1.0": False,
                    "TLSv1.1": False,
                    "TLSv1.2": "TLSv1.2" in str(ssock.version()),
                    "TLSv1.3": "TLSv1.3" in str(ssock.version())
                }

                # Cipher suites
                cipher_list = ssock.shared_ciphers()
                if cipher_list:
                    results["supported_ciphers"] = [c[0] for c in cipher_list]
                    weak_ciphers = [c[0] for c in cipher_list if
                                    any(w in c[0].lower() for w in ["rc4", "des", "3des", "md5"])]
                    results["weak_ciphers"] = weak_ciphers

                # Compression
                results["compression_enabled"] = bool(ssock.compression())

                # OCSP stapling (if available)
                try:
                    results["ocsp_stapling"] = ssock.getpeercert(binary_form=False).get("ocsp", False)
                except Exception:
                    pass

    except Exception as e:
        results["error"] = str(e)
        logger.error(f"SSL scan error for {url_or_hostname}: {str(e)}")

    return results
