from __future__ import annotations

import ipaddress
import logging

from django.conf import settings
from django.contrib import auth
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin

from accounts import rbac

logger = logging.getLogger(__name__)


def _clean_path(path: str) -> str:
    cleaned = "/" + path.lstrip("/")
    if not cleaned.endswith("/"):
        cleaned += "/"
    return cleaned


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Attach hardened security headers to every response."""

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        hsts_parts = [f"max-age={settings.SECURE_HSTS_SECONDS}"]
        if settings.SECURE_HSTS_INCLUDE_SUBDOMAINS:
            hsts_parts.append("includeSubDomains")
        if settings.SECURE_HSTS_PRELOAD:
            hsts_parts.append("preload")
        response.setdefault("Strict-Transport-Security", "; ".join(hsts_parts))
        response.setdefault("X-Frame-Options", settings.X_FRAME_OPTIONS)
        response.setdefault("X-Content-Type-Options", "nosniff")
        response.setdefault("Referrer-Policy", settings.SECURE_REFERRER_POLICY)

        csp_directives = getattr(settings, "CONTENT_SECURITY_POLICY", {})
        if csp_directives and "Content-Security-Policy" not in response:
            pieces = []
            for directive, sources in csp_directives.items():
                pieces.append(f"{directive} {' '.join(sorted(set(sources)))}")
            response["Content-Security-Policy"] = "; ".join(pieces)
        return response


class AdminAccessMiddleware(MiddlewareMixin):
    """Lock down access to the Django admin surface."""

    def __init__(self, get_response):
        super().__init__(get_response)
        self.admin_prefix = _clean_path(settings.ADMIN_BASE_PATH)
        self.allowed_ips = getattr(settings, "ADMIN_ALLOWED_IPS", [])
        self.allowed_asn = getattr(settings, "ADMIN_ALLOWED_ASN", [])

    def _ip_allowed(self, request: HttpRequest) -> bool:
        if not self.allowed_ips:
            return True
        remote_addr = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", ""))
        if not remote_addr:
            return False
        candidate = remote_addr.split(",")[0].strip()
        try:
            ip_obj = ipaddress.ip_address(candidate)
        except ValueError:
            logger.warning("Admin access denied due to invalid IP: %s", candidate)
            return False
        for entry in self.allowed_ips:
            try:
                if ip_obj in ipaddress.ip_network(entry, strict=False):
                    return True
            except ValueError:
                if candidate == entry:
                    return True
        return False

    def _asn_allowed(self, request: HttpRequest) -> bool:
        if not self.allowed_asn:
            return True
        request_asn = request.META.get("HTTP_X_ASN", "").strip()
        return request_asn in self.allowed_asn

    def process_view(self, request: HttpRequest, view_func, view_args, view_kwargs):
        if not request.path.startswith(self.admin_prefix):
            return None

        if not self._ip_allowed(request) or not self._asn_allowed(request):
            logger.warning("Blocked admin request from IP=%s ASN=%s", request.META.get("REMOTE_ADDR"), request.META.get("HTTP_X_ASN"))
            return HttpResponseForbidden("Admin access denied")

        user = request.user
        if not getattr(settings, "AUTH_REQUIRE_2FA_FOR_STAFF", False):
            return None

        if not user.is_authenticated:
            return None

        user_roles = rbac.get_user_roles(user)
        if not settings.ADMIN_REQUIRE_ROLES_2FA.intersection(user_roles):
            return None

        two_factor = getattr(user, "two_factor", None)
        if two_factor and two_factor.is_enabled:
            return None

        logger.warning("Admin access denied for %s due to missing 2FA", user)
        auth.logout(request)
        return HttpResponseForbidden("Two-factor authentication is required for admin access")


__all__ = [
    "SecurityHeadersMiddleware",
    "AdminAccessMiddleware",
]
