#!/bin/bash

echo "🚀 SMS Test with curl"
echo "===================="

# Check if phone number is provided
if [ -z "$1" ]; then
    echo "Usage: ./curl_sms_test.sh <phone_number>"
    echo "Example: ./curl_sms_test.sh 1234567890"
    exit 1
fi

PHONE_NUMBER=$1
MESSAGE="This is a test SMS from your AI assistant! 🤖"

echo "📱 Testing SMS to: $PHONE_NUMBER"
echo "📝 Message: $MESSAGE"
echo ""

# Test with TextBelt (free tier)
echo "📧 Testing TextBelt SMS..."
echo "   (Free tier: 1 SMS per day)"

curl -X POST https://textbelt.com/text \
  -d phone="$PHONE_NUMBER" \
  -d message="$MESSAGE" \
  -d key="textbelt_test"

echo ""
echo ""
echo "📋 Results:"
echo "- If you see 'success: true', the SMS was sent!"
echo "- If you see 'success: false', check the error message"
echo "- Check your phone for the message"
echo ""
echo "💡 To use a paid TextBelt key:"
echo "1. Go to https://textbelt.com"
echo "2. Get an API key"
echo "3. Replace 'textbelt_test' with your key"
echo ""
echo "💡 To use Twilio (more reliable):"
echo "1. Sign up at https://www.twilio.com"
echo "2. Get Account SID and Auth Token"
echo "3. Buy a phone number"
echo "4. Set environment variables and test"
