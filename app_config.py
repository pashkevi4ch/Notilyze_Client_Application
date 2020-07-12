import os

CLIENT_ID = "75c6abe9-3615-4375-bfe9-2866f051617d"

CLIENT_SECRET = "-.8_2pO3IeZxZOfKfH3cdx~4YQufD1W9-T"

AUTHORITY = "https://login.microsoftonline.com/a111daf6-3065-41cb-9b63-ab81be54bafd"

REDIRECT_PATH = "/getAToken"  # Used for forming an absolute URL to your redirect URI.
                              # The absolute URL must match the redirect URI you set
                              # in the app's registration in the Azure portal.

# You can find more Microsoft Graph API endpoints from Graph Explorer
# https://developer.microsoft.com/en-us/graph/graph-explorer
ENDPOINT = 'https://graph.microsoft.com/v1.0/users'  # This resource requires no admin consent

# You can find the proper permission names from this document
# https://docs.microsoft.com/en-us/graph/permissions-reference
SCOPE = ["User.ReadBasic.All"]

SESSION_TYPE = "filesystem"  # Specifies the token cache should be stored in server-side session
