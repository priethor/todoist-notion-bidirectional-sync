# Understanding Todoist Webhook Verification

Todoist uses a two-step verification process for webhooks:

1. **Initial Endpoint Verification** - Uses a verification token during setup
2. **Ongoing Request Verification** - Uses signature verification for all webhook events

Both steps are important to ensure secure webhook communication.

## Step 1: Initial Endpoint Verification (Verification Token)

When you first register a webhook URL with Todoist:

1. Todoist sends a GET request to your webhook URL with a `verification_token` query parameter
2. Your endpoint must respond with the exact verification token as plain text
3. This confirms you control the endpoint and it's ready to receive webhooks

This happens only once during webhook setup. Our application automatically handles this by responding to GET requests with the verification token.

## Step 2: Ongoing Signature Verification (Client Secret)

1. Todoist generates a unique "Client Secret" for your webhook
2. When sending a webhook, Todoist:
   - Takes the raw JSON payload (request body)
   - Computes an HMAC-SHA256 hash of the payload using your Client Secret as the key
   - **Base64 encodes** this hash value
   - Sends the Base64-encoded hash in the `X-Todoist-Hmac-SHA256` header

3. Your application must:
   - Extract the raw request body before parsing it as JSON
   - Compute the same HMAC-SHA256 hash using your Client Secret
   - **Base64 encode** the computed hash (important!)
   - Compare your Base64-encoded hash with the one in the header
   - Reject the request if they don't match

## Setting Up Your `.env` File Correctly

The Client Secret must be set in your `.env` file:

```
TODOIST_CLIENT_SECRET=your_client_secret_from_todoist
```

Where to find the Client Secret:
1. Go to the [Todoist Developer Console](https://developer.todoist.com/appconsole.html)
2. Find your application/integration
3. Go to the "Webhooks" section
4. When viewing your webhook, you'll see the Client Secret

**Important:** The Client Secret should be kept secure and never shared publicly.

## Troubleshooting Signature Verification

If signature verification is failing, check these common issues:

1. **Client Secret Mismatch**
   - Ensure the Client Secret in your `.env` file exactly matches what's shown in the Todoist Developer Console
   - No extra spaces, line breaks, or quotes should be included

2. **Signature Format**
   - Todoist sends the signature in **Base64 format**, not hexadecimal format
   - Make sure your verification code is base64-encoding the computed hash before comparison
   - You'll see errors like `Expected: 4ef82b62724d... Got: TvgrYnJN3Sg=` if you're using hex instead of base64

3. **Request Modification**
   - The raw request body must be used for verification exactly as it was received
   - Any modification to the request body (even parsing and re-serializing it) will cause the verification to fail

4. **Character Encoding**
   - Ensure all systems use the same encoding (UTF-8 is standard)

5. **Header Case Sensitivity**
   - The `X-Todoist-Hmac-SHA256` header might be provided in different case formats by different proxies or servers
   - Check your code to ensure it's case-insensitive when looking for this header

For detailed debugging, set `LOG_LEVEL=DEBUG` in your `.env` file to see more information about the signature verification process.