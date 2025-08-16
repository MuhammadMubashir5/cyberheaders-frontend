import dns.resolver
import logging

logger = logging.getLogger(__name__)

def dns_scan(domain):
    results = {
        "dnssec": False,
        "dmarc": False,
        "dkim": False,
        "spf": False,
        "mx_records": []
    }

    try:
        # Check DNSSEC
        try:
            dns.resolver.resolve(domain, 'DNSKEY')
            results["dnssec"] = True
        except:
            results["dnssec"] = False

        # Check DMARC
        try:
            dns.resolver.resolve(f'_dmarc.{domain}', 'TXT')
            results["dmarc"] = True
        except:
            pass

        # Check DKIM (common selectors)
        common_dkim_selectors = ['google', 'selector1', 'selector2', 'dkim']
        for selector in common_dkim_selectors:
            try:
                dns.resolver.resolve(f'{selector}._domainkey.{domain}', 'TXT')
                results["dkim"] = True
                break
            except:
                continue

        # Check SPF
        try:
            answers = dns.resolver.resolve(domain, 'TXT')
            for rdata in answers:
                if "v=spf1" in str(rdata):
                    results["spf"] = True
                    break
        except:
            pass

        # Get MX records
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            results["mx_records"] = [str(r.exchange) for r in mx_records]
        except:
            pass

    except Exception as e:
        results["error"] = str(e)
        logger.error(f"DNS scan error for {domain}: {str(e)}")

    return results