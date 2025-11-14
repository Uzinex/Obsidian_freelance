from __future__ import annotations

from rest_framework.throttling import SimpleRateThrottle


class _LoginThrottleMixin(SimpleRateThrottle):
    scope = "login"

    def get_scope(self, request, view):  # pragma: no cover - helper for clarity
        return getattr(view, "throttle_scope", None)

    def allow_request(self, request, view):
        if getattr(view, "throttle_scope", None) != "login":
            return True
        return super().allow_request(request, view)


class LoginIPThrottle(_LoginThrottleMixin):
    scope = "login_ip"

    def get_cache_key(self, request, view):
        if getattr(view, "throttle_scope", None) != "login":
            return None
        ident = self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}


class LoginUserThrottle(_LoginThrottleMixin):
    scope = "login_user"

    def get_cache_key(self, request, view):
        if getattr(view, "throttle_scope", None) != "login":
            return None
        credential = request.data.get("credential") or "anonymous"
        return self.cache_format % {"scope": self.scope, "ident": credential.lower()}
