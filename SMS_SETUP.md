# SMS Setup Guide

## Overview
The AI agent system supports sending SMS messages through multiple services. Currently, the system will simulate SMS sending if no SMS service is configured.

## Available SMS Services

### 1. Twilio (Recommended)
Twilio is a reliable SMS service with good delivery rates.

**Setup:**
1. Sign up for a Twilio account at https://www.twilio.com
2. Get your Account SID and Auth Token from the Twilio Console
3. Purchase a phone number from Twilio
4. Set the following environment variables:
   ```
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_PHONE_NUMBER=your_twilio_phone_number
   ```

### 2. TextBelt API
TextBelt offers a free tier for testing SMS functionality.

**Setup:**
1. Visit https://textbelt.com
2. Get a free API key (limited to 1 SMS per day)
3. The system will automatically use TextBelt if Twilio is not configured

### 3. Email-to-SMS Gateway
Many mobile carriers support email-to-SMS gateways.

**Supported Carriers:**
- Verizon: `{phone_number}@vtext.com`
- AT&T: `{phone_number}@txt.att.net`
- T-Mobile: `{phone_number}@tmomail.net`
- Sprint: `{phone_number}@messaging.sprintpcs.com`

## Testing SMS Functionality

1. **Provide your phone number:**
   - Say: "My phone number is 1234567890"
   - Or just type your 10-digit number

2. **Test SMS sending:**
   - Click the "Test SMS" button in the AI Agents Demo
   - Or say: "Send me an SMS reminder"

3. **Check the response:**
   - The system will show if the SMS was sent successfully
   - If using simulation, it will indicate that real SMS requires service configuration

## Troubleshooting

### SMS not being sent
1. Check if your phone number is saved in the database
2. Verify SMS service configuration
3. Check the server logs for error messages

### Twilio errors
1. Verify your Account SID and Auth Token
2. Ensure your Twilio phone number is active
3. Check your Twilio account balance

### TextBelt errors
1. Free tier is limited to 1 SMS per day
2. Consider upgrading to a paid plan for more messages

## Environment Variables

Add these to your `.env` file:

```env
# Twilio Configuration (Optional)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number

# TextBelt Configuration (Optional - used as fallback)
TEXTBELT_API_KEY=your_textbelt_key
```

## Code Location

The SMS functionality is implemented in:
- `agent_router_service/enhanced_agents.py` - Main SMS sending logic
- `api_gateway/routers/ai_agents.py` - API endpoints for SMS
- `frontend/components/ai-agents-demo.js` - Frontend SMS testing

## Security Notes

1. Never commit API keys to version control
2. Use environment variables for sensitive configuration
3. Consider rate limiting for SMS sending
4. Implement proper error handling for failed SMS attempts
