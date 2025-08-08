#!/usr/bin/env python3
"""
SMS Environment Setup Script
This script helps you set up environment variables for SMS services.
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create or update .env file with SMS configuration"""
    
    # Check if .env file exists
    env_file = Path('.env')
    env_content = ""
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            env_content = f.read()
    
    # SMS configuration template
    sms_config = """
# SMS Configuration
# Uncomment and fill in the values for the SMS service you want to use

# Twilio Configuration (Recommended)
# TWILIO_ACCOUNT_SID=your_account_sid_here
# TWILIO_AUTH_TOKEN=your_auth_token_here
# TWILIO_PHONE_NUMBER=your_twilio_phone_number_here

# TextBelt Configuration (Free tier available)
# TEXTBELT_API_KEY=your_textbelt_key_here

# Email Configuration (for Email-to-SMS)
# SMTP_SERVER=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USERNAME=your_email@gmail.com
# SMTP_PASSWORD=your_app_password
"""
    
    # Check if SMS config already exists
    if "SMS Configuration" not in env_content:
        # Append SMS config to existing .env file
        with open(env_file, 'a') as f:
            f.write(sms_config)
        print("✅ Added SMS configuration to .env file")
    else:
        print("ℹ️  SMS configuration already exists in .env file")
    
    return env_file

def check_current_config():
    """Check current SMS configuration"""
    print("🔍 Current SMS Configuration")
    print("=" * 40)
    
    # Check Twilio
    twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
    
    print("📱 Twilio:")
    print(f"   Account SID: {'✅ Set' if twilio_account_sid else '❌ Not set'}")
    print(f"   Auth Token: {'✅ Set' if twilio_auth_token else '❌ Not set'}")
    print(f"   Phone Number: {'✅ Set' if twilio_phone_number else '❌ Not set'}")
    
    # Check TextBelt
    textbelt_key = os.getenv("TEXTBELT_API_KEY")
    print(f"📧 TextBelt API Key: {'✅ Set' if textbelt_key else '❌ Not set'}")
    
    # Check Email
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_username = os.getenv("SMTP_USERNAME")
    print(f"📧 SMTP Server: {'✅ Set' if smtp_server else '❌ Not set'}")
    print(f"📧 SMTP Username: {'✅ Set' if smtp_username else '❌ Not set'}")
    
    print()
    
    # Determine which service is ready
    if all([twilio_account_sid, twilio_auth_token, twilio_phone_number]):
        print("🎉 Twilio is fully configured and ready to use!")
        return "twilio"
    elif textbelt_key:
        print("🎉 TextBelt is configured and ready to use!")
        return "textbelt"
    elif smtp_server and smtp_username:
        print("🎉 Email-to-SMS is configured and ready to use!")
        return "email"
    else:
        print("⚠️  No SMS service is fully configured")
        return None

def interactive_setup():
    """Interactive setup for SMS services"""
    print("\n🚀 Interactive SMS Setup")
    print("=" * 30)
    
    print("Choose your SMS service:")
    print("1. Twilio (Recommended - Most reliable)")
    print("2. TextBelt (Free tier available)")
    print("3. Email-to-SMS (Free but limited)")
    print("4. Skip for now")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        setup_twilio()
    elif choice == "2":
        setup_textbelt()
    elif choice == "3":
        setup_email_sms()
    elif choice == "4":
        print("👋 Skipping SMS setup. You can configure it later!")
    else:
        print("❌ Invalid choice. Please try again.")

def setup_twilio():
    """Setup Twilio configuration"""
    print("\n📱 Twilio Setup")
    print("=" * 20)
    
    print("To set up Twilio:")
    print("1. Go to https://www.twilio.com")
    print("2. Create a free account")
    print("3. Get your Account SID and Auth Token from the Console")
    print("4. Purchase a phone number (~$1/month)")
    
    account_sid = input("\nEnter your Twilio Account SID: ").strip()
    auth_token = input("Enter your Twilio Auth Token: ").strip()
    phone_number = input("Enter your Twilio Phone Number: ").strip()
    
    if account_sid and auth_token and phone_number:
        # Update .env file
        update_env_file("TWILIO_ACCOUNT_SID", account_sid)
        update_env_file("TWILIO_AUTH_TOKEN", auth_token)
        update_env_file("TWILIO_PHONE_NUMBER", phone_number)
        print("✅ Twilio configuration saved!")
    else:
        print("❌ Please provide all required values")

def setup_textbelt():
    """Setup TextBelt configuration"""
    print("\n📧 TextBelt Setup")
    print("=" * 20)
    
    print("To set up TextBelt:")
    print("1. Go to https://textbelt.com")
    print("2. Get a free API key (limited to 1 SMS per day)")
    
    api_key = input("\nEnter your TextBelt API key: ").strip()
    
    if api_key:
        update_env_file("TEXTBELT_API_KEY", api_key)
        print("✅ TextBelt configuration saved!")
    else:
        print("❌ Please provide the API key")

def setup_email_sms():
    """Setup Email-to-SMS configuration"""
    print("\n📧 Email-to-SMS Setup")
    print("=" * 25)
    
    print("To set up Email-to-SMS:")
    print("1. You'll need an email service (Gmail, etc.)")
    print("2. Enable 2-factor authentication")
    print("3. Generate an app password")
    
    smtp_server = input("\nEnter SMTP server (e.g., smtp.gmail.com): ").strip()
    smtp_port = input("Enter SMTP port (e.g., 587): ").strip()
    smtp_username = input("Enter your email: ").strip()
    smtp_password = input("Enter your app password: ").strip()
    
    if smtp_server and smtp_username and smtp_password:
        update_env_file("SMTP_SERVER", smtp_server)
        update_env_file("SMTP_PORT", smtp_port or "587")
        update_env_file("SMTP_USERNAME", smtp_username)
        update_env_file("SMTP_PASSWORD", smtp_password)
        print("✅ Email-to-SMS configuration saved!")
    else:
        print("❌ Please provide all required values")

def update_env_file(key, value):
    """Update .env file with new key-value pair"""
    env_file = Path('.env')
    
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write(f"{key}={value}\n")
    else:
        # Read existing content
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Update or add the key
        updated = False
        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[i] = f"{key}={value}\n"
                updated = True
                break
        
        if not updated:
            lines.append(f"{key}={value}\n")
        
        # Write back to file
        with open(env_file, 'w') as f:
            f.writelines(lines)

def main():
    """Main function"""
    print("🚀 SMS Environment Setup")
    print("=" * 40)
    
    # Create .env file if it doesn't exist
    env_file = create_env_file()
    
    # Check current configuration
    current_service = check_current_config()
    
    if current_service:
        print(f"✅ You're ready to use {current_service} for SMS!")
        response = input("Do you want to test SMS functionality? (y/n): ").lower().strip()
        if response == 'y':
            print("Run: python test_sms.py")
    else:
        # Offer interactive setup
        response = input("Do you want to set up SMS now? (y/n): ").lower().strip()
        if response == 'y':
            interactive_setup()
        else:
            print("👋 You can set up SMS later by running this script again!")

if __name__ == "__main__":
    main()
