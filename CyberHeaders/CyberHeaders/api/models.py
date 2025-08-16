from django.db import models
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

class ScanResult(models.Model):
    RISK_LEVELS = [
        ('L', 'Low'),
        ('M', 'Medium'),
        ('H', 'High'),
    ]

    url = models.CharField(max_length=2048, validators=[URLValidator()])
    security_score = models.IntegerField()
    risk_level = models.CharField(max_length=1, choices=RISK_LEVELS)
    headers_data = models.JSONField(default=dict)
    analysis_data = models.JSONField(default=dict)
    ssl_data = models.JSONField(default=dict)
    dns_data = models.JSONField(default=dict)
    recommendations = models.JSONField(default=list)
    passed_checks = models.JSONField(default=list)
    failed_checks = models.JSONField(default=list)
    gemini_analysis = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    pdf_report = models.FileField(upload_to='reports/', null=True, blank=True)

    def __str__(self):
        return f"{self.url} - {self.get_risk_level_display()} ({self.security_score})"

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Scan Result'
        verbose_name_plural = 'Scan Results'

class SecurityHeader(models.Model):
    STATUS_CHOICES = [
        ('P', 'Present'),
        ('M', 'Missing'),
        ('I', 'Insecure'),
        ('D', 'Deprecated'),
    ]

    scan_result = models.ForeignKey(ScanResult, on_delete=models.CASCADE, related_name='security_headers')
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    value = models.TextField(blank=True, null=True)
    recommendation = models.TextField()

    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"

class SSLScanResult(models.Model):
    scan_result = models.OneToOneField(ScanResult, on_delete=models.CASCADE, related_name='ssl_result')
    valid = models.BooleanField()
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_to = models.DateTimeField(null=True, blank=True)
    issuer = models.TextField(blank=True, null=True)
    signature_algorithm = models.CharField(max_length=100, blank=True, null=True)
    has_weak_ciphers = models.BooleanField()
    weak_ciphers = models.JSONField(default=list)
    compression_enabled = models.BooleanField()
    ocsp_stapling = models.BooleanField()

    def __str__(self):
        return f"SSL Scan for {self.scan_result.url}"

class DNSScanResult(models.Model):
    scan_result = models.OneToOneField(ScanResult, on_delete=models.CASCADE, related_name='dns_result')
    dnssec = models.BooleanField()
    dmarc = models.BooleanField()
    dkim = models.BooleanField()
    spf = models.BooleanField()
    mx_records = models.JSONField(default=list)
    txt_records = models.JSONField(default=list)

    def __str__(self):
        return f"DNS Scan for {self.scan_result.url}"