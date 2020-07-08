import os

CLIENT_ID = "e6b5b4f4-71bb-4070-b704-f49e0a2dc2c1"

CLIENT_SECRET = "e.nftK8DPj2.46foQ1oa_~CR3Qlr7HvMem"

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
