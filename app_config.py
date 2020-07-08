import os

CLIENT_ID = "8e41ec7f-1b2b-422a-b83d-d433e8c4efc8"

CLIENT_SECRET = "~TZ-~_PZ5LCq~eu7UdjVs1cCe5fUMy3L6j"

AUTHORITY = "https://login.microsoftonline.com/5b71f334-6f32-452f-9046-e127a708ce42"

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
