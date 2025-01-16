from __future__ import annotations

import time
from typing import TYPE_CHECKING, Self

from ldaptor.interfaces import IConnectedLDAPEntry, ILDAPEntry
from ldaptor.protocols.ldap.distinguishedname import DistinguishedName
from twisted.python import log
from zope.interface import implementer

from apricot.ldap.oauth_ldap_entry import OAuthLDAPEntry

if TYPE_CHECKING:
    from twisted.internet import defer

    from apricot.oauth import OAuthClient, OAuthDataAdaptor


@implementer(IConnectedLDAPEntry)
class OAuthLDAPTree:
    """An LDAP tree that represents a view of an OAuth directory."""

    def __init__(
        self: Self,
        oauth_adaptor: OAuthDataAdaptor,
        oauth_client: OAuthClient,
        *,
        background_refresh: bool,
        refresh_interval: int,
    ) -> None:
        """Initialise an OAuthLDAPTree.

        @param background_refresh: Whether to refresh the LDAP tree in the background rather than on access
        @param oauth_adaptor: An OAuth data adaptor used to construct the LDAP tree
        @param oauth_client: An OAuth client used to retrieve user and group data
        @param refresh_interval: Interval in seconds after which the tree must be refreshed
        """
        self.background_refresh = background_refresh
        self.debug = oauth_client.debug
        self.last_update = time.monotonic()
        self.oauth_adaptor = oauth_adaptor
        self.oauth_client = oauth_client
        self.refresh_interval = refresh_interval
        self.root_: OAuthLDAPEntry | None = None

    @property
    def dn(self: Self) -> DistinguishedName:
        return self.root.dn

    @property
    def root(self: Self) -> OAuthLDAPEntry:
        """Lazy-load the LDAP tree on request.

        @return: An OAuthLDAPEntry for the tree

        @raises: ValueError.
        """
        if not self.background_refresh:
            self.refresh()
        if not self.root_:
            msg = "LDAP tree could not be loaded"
            raise ValueError(msg)
        return self.root_

    def __repr__(self: Self) -> str:
        return f"{self.__class__.__name__} with backend {self.oauth_client.__class__.__name__}"

    def lookup(self: Self, dn: DistinguishedName | str) -> defer.Deferred[ILDAPEntry]:
        """Lookup the referred to by dn.

        @return: A Deferred returning an ILDAPEntry.
        """
        if not isinstance(dn, DistinguishedName):
            dn = DistinguishedName(stringValue=dn)
        if self.debug:
            log.msg(f"Starting an LDAP lookup for '{dn.getText()}'.")
        return self.root.lookup(dn)

    def refresh(self: Self) -> None:
        """Refresh the LDAP tree."""
        if (
            not self.root_
            or (time.monotonic() - self.last_update) > self.refresh_interval
        ):
            # Update users and groups from the OAuth server
            log.msg("Retrieving OAuth data.")
            oauth_groups, oauth_users = self.oauth_adaptor.retrieve_all()

            # Create a root node for the tree
            log.msg("Rebuilding LDAP tree.")
            self.root_ = OAuthLDAPEntry(
                dn=self.oauth_adaptor.root_dn,
                attributes={"objectClass": ["dcObject"]},
                oauth_client=self.oauth_client,
            )

            # Add OUs for users and groups
            groups_ou = self.root_.add_child(
                "OU=groups",
                {"ou": ["groups"], "objectClass": ["organizationalUnit"]},
            )
            users_ou = self.root_.add_child(
                "OU=users",
                {"ou": ["users"], "objectClass": ["organizationalUnit"]},
            )

            # Add groups to the groups OU
            if self.debug:
                log.msg(
                    f"Attempting to add {len(oauth_groups)} groups to the LDAP tree.",
                )
            for group_attrs in oauth_groups:
                groups_ou.add_child(f"CN={group_attrs.cn}", group_attrs.to_dict())
            if self.debug:
                children = groups_ou.list_children()
                for child in children:
                    log.msg(f"... {child.dn.getText()}")
                log.msg(f"There are {len(children)} groups in the LDAP tree.")

            # Add users to the users OU
            if self.debug:
                log.msg(
                    f"Attempting to add {len(oauth_users)} users to the LDAP tree.",
                )
            for user_attrs in oauth_users:
                users_ou.add_child(f"CN={user_attrs.cn}", user_attrs.to_dict())
            if self.debug:
                children = users_ou.list_children()
                for child in children:
                    log.msg(f"... {child.dn.getText()}")
                log.msg(f"There are {len(children)} users in the LDAP tree.")

            # Set last updated time
            log.msg("Finished building LDAP tree.")
            self.last_update = time.monotonic()
