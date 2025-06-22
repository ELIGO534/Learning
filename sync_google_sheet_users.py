import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import django
import re
from django.core.exceptions import ValidationError
from django.db import transaction

# --- Django Setup ---
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "adani.settings")
django.setup()

from myapp.models import CustomUser
from django.contrib.auth.hashers import make_password

# --- Connect to Google Sheet ---
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('adroit-outlet-453916-g6-1a7849adf277.json', scope)
client = gspread.authorize(creds)

sheet = client.open("Onboarding Sheet").worksheet("Form Responses 1")
data = sheet.get_all_values()
header = data[0]

# Column indices
status_idx = header.index("Status")
name_idx = header.index("Name")
phone_idx = header.index("Phone number")
domain_idx = header.index("Selected domain")

DOMAIN_MAP = {
    "web development": "web_dev_numbers",
    "data analysis": "data_analysis_numbers", 
    "autocad": "autocad",
    "machine learning": "ml_numbers",
    "ml": "ml_numbers",
    "rohit team": "rohitteam"
}

def clean_phone(phone):
    """Standardize phone number to 10 digits"""
    return re.sub(r'\D', '', phone)[-10:]  # Extract last 10 digits

def get_next_available_id():
    """Get the next available user ID by finding current max and incrementing"""
    max_user = CustomUser.objects.all().order_by('-id').first()
    if max_user:
        next_id = max_user.id + 1
    else:
        next_id = 1  # First user
    
    # Safety check in case of gaps in ID sequence
    while CustomUser.objects.filter(id=next_id).exists():
        next_id += 1
    
    return next_id

def update_views_py(new_entries, views_path='myapp/views.py'):
    """Robust views.py updater with exact pattern matching for your file format"""
    try:
        # Convert to absolute path for debugging
        abs_path = os.path.abspath(views_path)
        print(f"🔍 Absolute path to views.py: {abs_path}")
        
        with open(views_path, 'r+', encoding='utf-8-sig') as f:  # utf-8-sig handles BOM
            content = f.read()
            
            # Debug: Show first 200 chars of file
            print(f"📄 File snippet:\n{content[:200]}...\n")
            
            changes_made = False
            
            for domain, phone in new_entries:
                var_name = DOMAIN_MAP.get(domain.lower(), domain.lower().replace(" ", "_"))
                print(f"\n🔍 Processing: domain='{domain}' → var_name='{var_name}' → phone='{phone}'")
                
                # Skip if phone exists (check both quote types)
                if f'"{phone}"' in content or f"'{phone}'" in content:
                    print(f"   ✅ Phone {phone} already exists")
                    continue
                
                # EXACT pattern for your views.py format
                pattern = rf"'{var_name}'\s*:\s*\[[^\]]*"
                print(f"   🔎 Searching for: {pattern}")
                
                match = re.search(pattern, content)
                
                if not match:
                    # Show available lists for debugging
                    all_lists = re.findall(r"'(\w+)'\s*:\s*\[", content)
                    print(f"   ❌ List not found! Available lists: {all_lists}")
                    continue
                
                # Prepare new entry with EXACT indentation (8 spaces)
                new_entry = f',\n        "{phone}"'
                updated_content = content.replace(match.group(0), match.group(0) + new_entry)
                
                if updated_content != content:
                    content = updated_content
                    changes_made = True
                    print(f"   ✅ Added {phone} to {var_name}")
                else:
                    print("   ⚠️ No change made (possible formatting issue)")
            
            if changes_made:
                f.seek(0)
                f.write(content)
                f.truncate()
                print("\n💾 Successfully updated views.py")
                return True
            else:
                print("\nℹ️ No changes needed in views.py")
                return False
                
    except Exception as e:
        print(f"❌ Critical error updating views.py: {str(e)}")
        return False
                
    except Exception as e:
        print(f"❌ Error updating views.py: {e}")
        return False

@transaction.atomic
def create_user_safely(name, phone):
    """Create user with proper ID handling in a transaction"""
    user = CustomUser(
        id=get_next_available_id(),
        name=name,
        phone=phone,
        password=make_password(phone),
        is_active=True
    )
    user.full_clean()
    user.save()
    return user

def main():
    new_users = []
    rows_to_update = []
    new_entries_for_views = []

    print("🔍 Starting user synchronization process...")
    
    for row_index, row in enumerate(data[1:], start=2):
        status = row[status_idx].strip().lower()
        if status != "sent":
            continue
            
        name = row[name_idx].strip()
        raw_phone = row[phone_idx]
        phone = clean_phone(raw_phone)
        domain = row[domain_idx].strip().lower()
        
        # Validate data
        if not name:
            print(f"⚠️ Row {row_index}: Missing name")
            continue
        if not phone or len(phone) != 10:
            print(f"⚠️ Row {row_index}: Invalid phone number '{raw_phone}' (cleaned to '{phone}')")
            continue
            
        # Check for existing user by phone
        if CustomUser.objects.filter(phone=phone).exists():
            print(f"ℹ️ User with phone {phone} already exists in database")
            mapped_domain = DOMAIN_MAP.get(domain, domain)
            new_entries_for_views.append((mapped_domain, phone))
            rows_to_update.append(row_index)
            continue
                
        try:
            user = create_user_safely(name, phone)
            print(f"✅ Created user: ID={user.id}, Name='{name}', Phone={phone}")
            new_users.append(user)
            
            mapped_domain = DOMAIN_MAP.get(domain, domain)
            new_entries_for_views.append((mapped_domain, phone))
            rows_to_update.append(row_index)
        except Exception as e:
            print(f"❌ Failed to create user '{name}' ({phone}): {str(e)}")
            continue
    
    # Update Google Sheet status
    if rows_to_update:
        try:
            print(f"🔄 Updating {len(rows_to_update)} rows in Google Sheet...")
            for row in rows_to_update:
                sheet.update_cell(row, status_idx + 1, "Processed")
            print("✅ Google Sheet updated successfully")
        except Exception as e:
            print(f"❌ Failed to update Google Sheet: {str(e)}")
    
    # Update views.py
    if new_entries_for_views:
        print(f"📝 Updating views.py with {len(new_entries_for_views)} new numbers...")
        if update_views_py(new_entries_for_views):
            print("✅ views.py updated successfully")
            run_git_commands()  # 🚀 Add this line

    else:
        print("ℹ️ No new numbers to add to views.py")

    print(f"\n🎉 Synchronization complete! Created {len(new_users)} new users.")

import time

if __name__ == "__main__":
    while True:
        print("⏳ Checking for new 'Sent' entries in the Google Sheet...")
        main()
        print("✅ Done. Next check in 1 minutes...\n")
        time.sleep(60)  

import subprocess

def run_git_commands():
    try:
        subprocess.run(["git", "add", "myapp/views.py"], check=True)
        subprocess.run(["git", "commit", "-m", "Update views.py with new phone numbers"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("🚀 Git operations completed: add → commit → push")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git command failed: {e}")
