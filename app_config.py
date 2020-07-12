import os

CLIENT_ID = "2680555c-83de-4fc4-8bbb-a0a7854407a4"

CLIENT_SECRET = "MNuFjm~Mlw.Ou9H5PP0~mPHK1~AXxB1ggG"

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
