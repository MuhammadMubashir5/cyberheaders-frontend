from django.contrib import admin
from .models import ScanResult, SecurityHeader, SSLScanResult, DNSScanResult

@admin.register(ScanResult)
class ScanResultAdmin(admin.ModelAdmin):
    list_display = ('url', 'security_score', 'risk_level', 'timestamp')
    list_filter = ('risk_level', 'timestamp')
    search_fields = ('url', 'analysis_data')
    readonly_fields = ('timestamp',)

@admin.register(SecurityHeader)
class SecurityHeaderAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'recommendation')
    list_filter = ('status',)

@admin.register(SSLScanResult)
class SSLScanResultAdmin(admin.ModelAdmin):
    list_display = ('scan_result', 'has_weak_ciphers', 'compression_enabled')
    readonly_fields = ('scan_result',)

@admin.register(DNSScanResult)
class DNSScanResultAdmin(admin.ModelAdmin):
    list_display = ('scan_result', 'dnssec', 'dmarc', 'dkim', 'spf')
    readonly_fields = ('scan_result',)