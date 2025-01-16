from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Self

from ldaptor.protocols.ldap.ldaperrors import LDAPProtocolError
from ldaptor.protocols.ldap.ldapserver import LDAPServer
from twisted.logger import Logger

if TYPE_CHECKING:
    from ldaptor.interfaces import ILDAPEntry
    from ldaptor.protocols.pureldap import (
        LDAPAddRequest,
        LDAPBindRequest,
        LDAPCompareRequest,
        LDAPDelRequest,
        LDAPExtendedRequest,
        LDAPModifyDNRequest,
        LDAPModifyRequest,
        LDAPProtocolRequest,
        LDAPSearchRequest,
        LDAPSearchResultDone,
        LDAPSearchResultEntry,
        LDAPUnbindRequest,
    )
    from twisted.internet import defer

    from apricot.oauth import LDAPControlTuple


class ReadOnlyLDAPServer(LDAPServer):
    """A read-only LDAP server."""

    def __init__(self: Self, *, debug: bool = False) -> None:
        """Initialise a ReadOnlyLDAPServer.

        @param debug: Enable debug output
        """
        self.logger = Logger()
        super().__init__()
        self.debug = debug

    def getRootDSE(  # noqa: N802
        self: Self,
        request: LDAPProtocolRequest,
        reply: Callable[[LDAPSearchResultEntry], None] | None,
    ) -> LDAPSearchResultDone:
        """Handle an LDAP Root DSE request."""
        try:
            self.logger.debug("Handling an LDAP Root DSE request.")
            return super().getRootDSE(request, reply)
        except Exception as exc:
            msg = f"LDAP Root DSE request failed. {exc!s}"
            self.logger.error(msg)  # noqa: TRY400
            raise LDAPProtocolError(msg) from exc

    def handle_LDAPAddRequest(  # noqa: N802
        self: Self,
        request: LDAPAddRequest,
        controls: list[LDAPControlTuple] | None,
        reply: Callable[..., None] | None,
    ) -> defer.Deferred[ILDAPEntry]:
        """Refuse to handle an LDAP add request."""
        id((request, controls, reply))  # ignore unused arguments
        self.logger.debug("Handling an LDAP add request.")
        msg = "ReadOnlyLDAPServer will not handle LDAP add requests"
        self.logger.error(msg)
        raise LDAPProtocolError(msg)

    def handle_LDAPBindRequest(  # noqa: N802
        self: Self,
        request: LDAPBindRequest,
        controls: list[LDAPControlTuple] | None,
        reply: Callable[..., None] | None,
    ) -> defer.Deferred[ILDAPEntry]:
        """Handle an LDAP bind request."""
        try:
            self.logger.debug("Handling an LDAP bind request.")
            return super().handle_LDAPBindRequest(request, controls, reply)
        except Exception as exc:
            msg = f"LDAP bind request failed. {exc!s}"
            self.logger.error(msg)  # noqa: TRY400
            raise LDAPProtocolError(msg) from exc

    def handle_LDAPCompareRequest(  # noqa: N802
        self: Self,
        request: LDAPCompareRequest,
        controls: list[LDAPControlTuple] | None,
        reply: Callable[..., None] | None,
    ) -> defer.Deferred[ILDAPEntry]:
        """Handle an LDAP compare request."""
        try:
            self.logger.debug("Handling an LDAP compare request.")
            return super().handle_LDAPCompareRequest(request, controls, reply)
        except Exception as exc:
            msg = f"LDAP compare request failed. {exc!s}"
            self.logger.error(msg)  # noqa: TRY400
            raise LDAPProtocolError(msg) from exc

    def handle_LDAPDelRequest(  # noqa: N802
        self: Self,
        request: LDAPDelRequest,
        controls: list[LDAPControlTuple] | None,
        reply: Callable[..., None] | None,
    ) -> defer.Deferred[ILDAPEntry]:
        """Refuse to handle an LDAP delete request."""
        id((request, controls, reply))  # ignore unused arguments
        self.logger.debug("Handling an LDAP delete request.")
        msg = "ReadOnlyLDAPServer will not handle LDAP delete requests"
        self.logger.error(msg)
        raise LDAPProtocolError(msg)

    def handle_LDAPExtendedRequest(  # noqa: N802
        self: Self,
        request: LDAPExtendedRequest,
        controls: list[LDAPControlTuple] | None,
        reply: Callable[..., None] | None,
    ) -> defer.Deferred[ILDAPEntry]:
        """Handle an LDAP extended request."""
        try:
            self.logger.debug("Handling an LDAP extended request.")
            return super().handle_LDAPExtendedRequest(request, controls, reply)
        except Exception as exc:
            msg = f"LDAP extended request failed. {exc!s}"
            self.logger.error(msg)  # noqa: TRY400
            raise LDAPProtocolError(msg) from exc

    def handle_LDAPModifyDNRequest(  # noqa: N802
        self: Self,
        request: LDAPModifyDNRequest,
        controls: list[LDAPControlTuple] | None,
        reply: Callable[..., None] | None,
    ) -> defer.Deferred[ILDAPEntry]:
        """Refuse to handle an LDAP modify DN request."""
        self.logger.debug("Handling an LDAP modify DN request.")
        id((request, controls, reply))  # ignore unused arguments
        msg = "ReadOnlyLDAPServer will not handle LDAP modify DN requests"
        self.logger.error(msg)
        raise LDAPProtocolError(msg)

    def handle_LDAPModifyRequest(  # noqa: N802
        self: Self,
        request: LDAPModifyRequest,
        controls: list[LDAPControlTuple] | None,
        reply: Callable[..., None] | None,
    ) -> defer.Deferred[ILDAPEntry]:
        """Refuse to handle an LDAP modify request."""
        self.logger.debug("Handling an LDAP modify request.")
        id((request, controls, reply))  # ignore unused arguments
        msg = "ReadOnlyLDAPServer will not handle LDAP modify requests"
        self.logger.error(msg)
        raise LDAPProtocolError(msg)

    def handle_LDAPSearchRequest(  # noqa: N802
        self: Self,
        request: LDAPSearchRequest,
        controls: list[LDAPControlTuple] | None,
        reply: Callable[[LDAPSearchResultEntry], None] | None,
    ) -> defer.Deferred[ILDAPEntry]:
        """Handle an LDAP search request."""
        try:
            self.logger.debug("Handling an LDAP search request.")
            return super().handle_LDAPSearchRequest(request, controls, reply)
        except Exception as exc:
            msg = f"LDAP search request failed. {exc!s}"
            self.logger.error(msg)  # noqa: TRY400
            raise LDAPProtocolError(msg) from exc

    def handle_LDAPUnbindRequest(  # noqa: N802
        self: Self,
        request: LDAPUnbindRequest,
        controls: list[LDAPControlTuple] | None,
        reply: Callable[..., None] | None,
    ) -> None:
        """Handle an LDAP unbind request."""
        try:
            self.logger.debug("Handling an LDAP unbind request.")
            super().handle_LDAPUnbindRequest(request, controls, reply)
        except Exception as exc:
            msg = f"LDAP unbind request failed. {exc!s}"
            self.logger.error(msg)  # noqa: TRY400
            raise LDAPProtocolError(msg) from exc
