from typing import Any

from .oauth_client import OAuthClient
from .types import LDAPAttributeDict


class MicrosoftEntraClient(OAuthClient):
    """OAuth client for the Microsoft Entra backend."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        tenant_id: str,
        *args: Any,
        **kwargs: Any,
    ):
        redirect_uri = "urn:ietf:wg:oauth:2.0:oob"  # this is the "no redirect" URL
        scopes = ["https://graph.microsoft.com/.default"]  # this is the default scope
        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        self.tenant_id = tenant_id
        super().__init__(
            *args,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scopes=scopes,
            token_url=token_url,
            **kwargs,
        )

    def domain(self) -> str:
        users = self.users()
        domains = {user["domain"][0] for user in users}
        if len(domains) > 1:
            domains = [domain for domain in domains if "onmicrosoft.com" not in domain]
        return sorted(domains)[0]

    def extract_token(self, json_response: dict[str, str | list[str]]) -> None:
        return json_response["access_token"]

    def groups(self) -> list[LDAPAttributeDict]:
        output = []
        try:
            group_data = self.query("https://graph.microsoft.com/v1.0/groups/")
            for group_dict in group_data["value"]:
                attributes = {k: [v if v else ""] for k, v in dict(group_dict).items()}
                attributes["objectclass"] = ["top", "group"]
                attributes["name"] = [str(group_dict["displayName"]).split("@")[0]]
                output.append(attributes)
        except KeyError:
            pass
        return output

    def users(self) -> list[LDAPAttributeDict]:
        output = []
        try:
            user_data = self.query("https://graph.microsoft.com/v1.0/users/")
            for user_dict in user_data["value"]:
                attributes = {k: [v if v else ""] for k, v in dict(user_dict).items()}
                attributes["objectclass"] = [
                    "top",
                    "person",
                    "organizationalPerson",
                    "user",
                ]
                group_memberships = self.query(
                    f"https://graph.microsoft.com/v1.0/users/{user_dict['id']}/memberOf"
                )
                attributes["memberOf"] = [
                    group["displayName"]
                    for group in group_memberships["value"]
                    if group["displayName"]
                ]
                attributes["name"] = [str(user_dict["userPrincipalName"]).split("@")[0]]
                attributes["domain"] = [
                    str(user_dict["userPrincipalName"]).split("@")[1]
                ]
                output.append(attributes)
        except KeyError:
            pass
        return output
