# Quick SMS Setup Guide

## Option 1: Twilio (Recommended - Most Reliable)

### Step 1: Sign up for Twilio
1. Go to https://www.twilio.com
2. Create a free account
3. Verify your email and phone number

### Step 2: Get Your Credentials
1. Go to your Twilio Console
2. Copy your **Account SID** and **Auth Token**
3. Purchase a phone number (costs ~$1/month)

### Step 3: Set Environment Variables
Add these to your `.env` file or set them in your terminal:

```bash
export TWILIO_ACCOUNT_SID=your_account_sid_here
export TWILIO_AUTH_TOKEN=your_auth_token_here
export TWILIO_PHONE_NUMBER=your_twilio_phone_number_here
```

### Step 4: Test
Run the test script:
```bash
python test_sms.py
```

## Option 2: TextBelt (Free Testing)

### Step 1: Get Free API Key
1. Go to https://textbelt.com
2. Get a free API key (limited to 1 SMS per day)

### Step 2: Set Environment Variable
```bash
export TEXTBELT_API_KEY=your_textbelt_key_here
```

### Step 3: Test
The system will automatically use TextBelt if Twilio is not configured.

## Option 3: Email-to-SMS (Free but Limited)

### Supported Carriers:
- **Verizon**: `{phone}@vtext.com`
- **AT&T**: `{phone}@txt.att.net`
- **T-Mobile**: `{phone}@tmomail.net`
- **Sprint**: `{phone}@messaging.sprintpcs.com`

### Setup:
1. Find your carrier's gateway
2. Configure email service (SMTP)
3. Send emails to the gateway address

## Testing Your Setup

### 1. Provide Your Phone Number
In the AI Agents Demo, say:
- "My phone number is 1234567890"
- Or just type your 10-digit number

### 2. Test SMS Sending
- Click "Test SMS" button
- Or say: "Send me an SMS reminder"

### 3. Check Results
- Look for success/error messages
- Check your phone for actual SMS

## Troubleshooting

### SMS Not Received?
1. **Check phone number format**: Use 10 digits (1234567890)
2. **Verify carrier**: Some carriers block SMS from unknown numbers
3. **Check spam folder**: SMS might be marked as spam
4. **Test with Twilio**: Most reliable option

### Twilio Errors?
1. **Invalid credentials**: Double-check Account SID and Auth Token
2. **Insufficient balance**: Add money to your Twilio account
3. **Phone number not verified**: Verify your phone in Twilio console

### TextBelt Errors?
1. **Daily limit**: Free tier allows only 1 SMS per day
2. **Invalid phone**: Make sure phone number is correct
3. **Upgrade needed**: Consider paid plan for more messages

## Quick Test Commands

```bash
# Check environment variables
echo $TWILIO_ACCOUNT_SID
echo $TWILIO_AUTH_TOKEN
echo $TWILIO_PHONE_NUMBER

# Run test script
python test_sms.py

# Test with curl (if you have a TextBelt key)
curl -X POST https://textbelt.com/text \
  -d phone=1234567890 \
  -d message="Test SMS" \
  -d key=your_textbelt_key
```

## Cost Comparison

| Service | Setup Cost | Per SMS | Reliability |
|---------|------------|---------|-------------|
| Twilio | $1/month | $0.0075 | ⭐⭐⭐⭐⭐ |
| TextBelt | Free | $0.01 | ⭐⭐⭐ |
| Email-to-SMS | Free | Free | ⭐⭐ |

## Next Steps

1. **For Development**: Use TextBelt free tier
2. **For Production**: Use Twilio
3. **For Testing**: Use Email-to-SMS gateways

Choose the option that best fits your needs and budget!
