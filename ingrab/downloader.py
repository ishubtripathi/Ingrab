"""
Ingrab - Instagram Media Downloader
A professional tool to download content from public Instagram profiles
"""

import instaloader
import os
import shutil
import time
import sys
import re
import webbrowser
import random
from datetime import datetime, timedelta
from collections import deque

# ============ CONFIGURATION ============
VERSION = "1.4.0"
AUTHOR = "Shubh Tripathi"
EMAIL = "bugingrab@gmail.com"
LINKEDIN = "https://www.linkedin.com/in/ishubtripathi/"
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp')
VIDEO_EXTENSIONS = ('.mp4', '.mov')

# ============ LOADING ANIMATION ============
class LoadingAnimation:
    """Display animated loading indicator"""
    
    def __init__(self):
        self.spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.idx = 0
        self.running = False
    
    def start(self, message="Processing"):
        """Start loading animation"""
        import threading
        self.running = True
        self.message = message
        
        def animate():
            while self.running:
                sys.stdout.write(f'\r{self.message} {self.spinner[self.idx]} ')
                sys.stdout.flush()
                self.idx = (self.idx + 1) % len(self.spinner)
                time.sleep(0.1)
        
        self.thread = threading.Thread(target=animate, daemon=True)
        self.thread.start()
    
    def stop(self, success=True):
        """Stop loading animation"""
        self.running = False
        if success:
            sys.stdout.write('\r✓ Done!          \n')
        else:
            sys.stdout.write('\r✗ Failed         \n')
        sys.stdout.flush()
        time.sleep(0.2)

# ============ ERROR MESSAGES ============
ERROR_MESSAGES = {
    400: "Bad Request - The request was invalid. Please try again.",
    401: "Unauthorized - Instagram requires you to wait before making more requests.\n   ⏰ Please wait 30-60 minutes and try again.",
    402: "Payment Required - This is not applicable for Instagram downloads.",
    403: "Forbidden - Instagram has temporarily blocked your requests.\n   ⏰ Please wait 30-60 minutes before trying again.\n   💡 Tip: Login to Instagram (option 3) to avoid this.",
    404: "Not Found - The profile or content does not exist.",
    429: "Too Many Requests - You've made too many requests too quickly.\n   ⏰ Please wait 15-30 minutes and try again with fewer downloads.",
    500: "Server Error - Instagram's servers are having issues.\n   ⏰ Please wait a few minutes and try again.",
    503: "Service Unavailable - Instagram is temporarily unavailable.\n   ⏰ Please wait and try again later.",
}

def get_error_message(status_code, default_message=None):
    """Get user-friendly error message for status code"""
    if status_code in ERROR_MESSAGES:
        return ERROR_MESSAGES[status_code]
    return default_message or f"An error occurred (HTTP {status_code}). Please try again later."

# ============ SMART RATE LIMITER ============
class SmartRateLimiter:
    """Proactively prevents rate limiting"""
    
    def __init__(self):
        self.daily_limits = {
            'profile_views': 50,
            'downloads': 40,
        }
        self.usage = {key: 0 for key in self.daily_limits}
        self.last_reset = datetime.now().date()
        
        self.min_delay = 3
        self.max_delay = 8
        self.last_request_time = 0
        self.request_timestamps = deque(maxlen=20)
        self.consecutive_errors = 0
        self.in_cooldown = False
        self.cooldown_until = None
        
    def reset_if_needed(self):
        today = datetime.now().date()
        if today > self.last_reset:
            for key in self.usage:
                self.usage[key] = 0
            self.last_reset = today
            print("\n✅ Daily limits reset!")
            return True
        return False
    
    def can_proceed(self, action_type='downloads'):
        self.reset_if_needed()
        
        if self.in_cooldown and self.cooldown_until:
            if datetime.now() < self.cooldown_until:
                wait = (self.cooldown_until - datetime.now()).total_seconds()
                return False, wait, "Cooling down from previous errors"
            else:
                self.in_cooldown = False
                self.cooldown_until = None
                self.consecutive_errors = 0
        
        limit = self.daily_limits.get(action_type, 40)
        used = self.usage.get(action_type, 0)
        
        if used >= limit:
            return False, 0, f"Daily limit reached ({limit}/day). Try tomorrow!"
        
        now = time.time()
        if len(self.request_timestamps) >= 15:
            oldest = self.request_timestamps[0]
            if now - oldest < 300:
                wait = 60 - (now - self.request_timestamps[-1])
                if wait > 0:
                    return False, wait, "Making too many requests. Please slow down."
        
        time_since_last = now - self.last_request_time
        if time_since_last < self.min_delay:
            wait = self.min_delay - time_since_last + random.uniform(0, 2)
            return False, wait, "Waiting between requests to avoid blocks..."
        
        return True, 0, "OK"
    
    def record_request(self, action_type='downloads', success=True):
        now = time.time()
        self.last_request_time = now
        self.request_timestamps.append(now)
        
        if success:
            self.usage[action_type] += 1
            self.consecutive_errors = 0
        else:
            self.consecutive_errors += 1
            if self.consecutive_errors >= 2:
                cooldown_minutes = min(30, 5 * self.consecutive_errors)
                self.in_cooldown = True
                self.cooldown_until = datetime.now() + timedelta(minutes=cooldown_minutes)
                print(f"\n⚠️ Multiple errors detected. Cooling down for {cooldown_minutes} minutes.")
    
    def get_random_delay(self):
        return random.uniform(self.min_delay, self.max_delay)
    
    def get_remaining(self, action_type='downloads'):
        self.reset_if_needed()
        limit = self.daily_limits.get(action_type, 40)
        used = self.usage.get(action_type, 0)
        return max(0, limit - used)
    
    def show_status(self):
        self.reset_if_needed()
        print("\n" + "-"*50)
        print("Daily Usage Status")
        print("-"*50)
        for action, limit in self.daily_limits.items():
            used = self.usage.get(action, 0)
            remaining = limit - used
            percent = (used / limit) * 100 if limit > 0 else 0
            bar_length = 20
            filled = int(bar_length * used / limit) if limit > 0 else 0
            bar = "█" * filled + "░" * (bar_length - filled)
            action_name = "Profile Views" if action == 'profile_views' else "Media Downloads"
            print(f"{action_name:15} {bar} {used}/{limit} ({percent:.0f}%)")
        
        if self.in_cooldown and self.cooldown_until:
            remaining = (self.cooldown_until - datetime.now()).total_seconds() / 60
            print(f"\n Cooling down: {remaining:.0f} minutes remaining")
        print("-"*50)

# ============ SESSION MANAGER ============
class SessionManager:
    """Manages Instagram session"""
    
    def __init__(self):
        self.session_file = "ingrab_session"
        self.loader = None
        self.is_logged_in = False
        
    def get_loader(self):
        if self.loader is None:
            self.loader = instaloader.Instaloader(
                max_connection_attempts=3,
                request_timeout=30
            )
            self.loader.context._session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            self._load_existing_session()
        return self.loader
    
    def _load_existing_session(self):
        try:
            if os.path.exists(self.session_file):
                self.loader.load_session(self.session_file)
                self.is_logged_in = True
                return True
        except Exception:
            pass
        return False
    
    def login(self):
        loader = self.get_loader()
        
        if self._load_existing_session():
            try:
                instaloader.Profile.from_username(loader.context, "instagram")
                print("✅ Session is valid!")
                return True
            except:
                print("⚠️ Session expired, please login again")
        
        print("\n" + "="*50)
        print("Instagram Login (Recommended)")
        print("="*50)
        print("\nBenefits of logging in:")
        print("  • Higher download limits (200+ per day)")
        print("  • Access to private profiles you follow")
        print("  • Fewer rate limiting issues")
        print("\n⚠️ Your password is not stored - only a session cookie is saved\n")
        
        choice = input("Login to Instagram? (y/n): ").strip().lower()
        if choice != 'y':
            print("\n⚠️ Continuing without login - limited to 40 downloads per day")
            return False
        
        username = input("\nInstagram Username: ").strip()
        password = input("Instagram Password: ").strip()
        
        try:
            print("\n🔄 Logging in...")
            loader.login(username, password)
            loader.save_session(self.session_file)
            self.is_logged_in = True
            print("\n✅ Login successful!")
            return True
        except Exception as e:
            print(f"\n❌ Login failed: {e}")
            return False
    
    def logout(self):
        if os.path.exists(self.session_file):
            os.remove(self.session_file)
            self.is_logged_in = False
            print("✅ Logged out successfully")
        else:
            print("No active session found")
    
    def is_authenticated(self):
        return self.is_logged_in

# ============ MAIN DOWNLOADER ============
class IngrabDownloader:
    """Main downloader with rate limiting"""
    
    def __init__(self):
        self.rate_limiter = SmartRateLimiter()
        self.session_manager = SessionManager()
        self.loader = self.session_manager.get_loader()
        self.loading = LoadingAnimation()
        
    def handle_http_error(self, error_str):
        """Parse HTTP error and return user-friendly message"""
        # Extract status code from error string
        import re
        match = re.search(r'HTTP (\d{3})', error_str)
        if match:
            status_code = int(match.group(1))
            return get_error_message(status_code)
        
        # Check for common error patterns
        if "401" in error_str or "Unauthorized" in error_str:
            return get_error_message(401)
        elif "403" in error_str or "Forbidden" in error_str:
            return get_error_message(403)
        elif "429" in error_str or "Too Many Requests" in error_str:
            return get_error_message(429)
        elif "404" in error_str or "Not Found" in error_str:
            return get_error_message(404)
        
        return None
    
    def get_profile_safe(self, profile_name):
        """Get profile with retry logic and user-friendly errors"""
        max_retries = 2
        
        for attempt in range(max_retries):
            can_proceed, wait_time, message = self.rate_limiter.can_proceed('profile_views')
            
            if not can_proceed:
                if wait_time > 0 and wait_time < 120:
                    print(f"\n {message} Waiting {wait_time:.0f} seconds...")
                    time.sleep(wait_time)
                else:
                    if "Daily limit reached" in message:
                        print(f"\n❌ {message}")
                    return None
            
            try:
                self.loading.start(f"Fetching @{profile_name}")
                time.sleep(self.rate_limiter.get_random_delay() * 0.3)
                profile = instaloader.Profile.from_username(self.loader.context, profile_name)
                self.loading.stop(True)
                self.rate_limiter.record_request('profile_views', success=True)
                return profile
                
            except instaloader.exceptions.ConnectionException as e:
                self.loading.stop(False)
                error_str = str(e)
                
                # Get user-friendly error message
                friendly_msg = self.handle_http_error(error_str)
                
                if friendly_msg:
                    print(f"\n❌ {friendly_msg}")
                    
                    # Provide additional guidance for 401/403
                    if "401" in error_str or "403" in error_str:
                        print("\n What you can do:")
                        print("   1. Wait 30-60 minutes before trying again")
                        print("   2. Login to Instagram (option 3 in main menu)")
                        print("   3. Download fewer items (5-10 at a time)")
                        print("   4. Try a different profile")
                    
                    self.rate_limiter.record_request('profile_views', success=False)
                    return None
                else:
                    print(f"\n⚠️ Connection issue: {error_str[:150]}")
                    if attempt < max_retries - 1:
                        print("   Retrying in 30 seconds...")
                        time.sleep(30)
                    else:
                        return None
                        
            except instaloader.exceptions.ProfileNotExistsException:
                self.loading.stop(False)
                print(f"\n❌ Profile '@{profile_name}' does not exist on Instagram")
                return None
            except instaloader.exceptions.PrivateProfileNotFollowedException:
                self.loading.stop(False)
                print(f"\n❌ Profile '@{profile_name}' is private")
                if not self.session_manager.is_authenticated():
                    print("   💡 Tip: Login to Instagram to access private profiles you follow")
                return None
            except Exception as e:
                self.loading.stop(False)
                error_str = str(e)
                friendly_msg = self.handle_http_error(error_str)
                if friendly_msg:
                    print(f"\n❌ {friendly_msg}")
                else:
                    print(f"\n❌ Error: {error_str[:150]}")
                return None
        
        return None
    
    def download_profile_picture(self, profile_name):
        """Download profile picture"""
        remaining = self.rate_limiter.get_remaining('profile_views')
        if remaining <= 0:
            print(f"\n❌ Daily limit reached! Please try again tomorrow.")
            return
        
        print(f"\n📸 Downloading profile picture for @{profile_name}...")
        
        profile = self.get_profile_safe(profile_name)
        if not profile:
            return
        
        try:
            self.loading.start("Downloading profile picture")
            time.sleep(self.rate_limiter.get_random_delay())
            self.loader.download_profilepic(profile)
            self.loading.stop(True)
            print(f"✅ Profile picture saved successfully!")
            self.rate_limiter.record_request('profile_views', success=True)
        except Exception as e:
            self.loading.stop(False)
            error_str = str(e)
            friendly_msg = self.handle_http_error(error_str)
            if friendly_msg:
                print(f"❌ {friendly_msg}")
            else:
                print(f"❌ Error: {error_str[:100]}")
    
    def download_media(self, profile_name, media_type='posts', count=None):
        """Generic media downloader for posts and reels"""
        remaining = self.rate_limiter.get_remaining('downloads')
        
        if remaining <= 0:
            print(f"\n❌ Daily limit reached! Please try again tomorrow.")
            return
        
        # Handle 'all' download
        if count is None:
            print(f"\n⚠️ Downloading ALL {media_type} may take significant time")
            confirm = input("Continue? (y/n): ").strip().lower()
            if confirm != 'y':
                return
        
        # Validate count
        if count is not None:
            if count < 1:
                count = 1
            if count > remaining:
                print(f"\n⚠️ Reducing from {count} to {remaining} (daily limit)")
                count = remaining
            if count > 20:
                print(f"\n⚠️ Limiting to 20 items to avoid rate limiting")
                count = 20
        
        profile = self.get_profile_safe(profile_name)
        if not profile:
            return
        
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', profile_name)
        os.makedirs(safe_name, exist_ok=True)
        
        media_label = "posts" if media_type == 'posts' else "reels"
        print(f"\n📥 Downloading {media_label} from @{profile_name}...")
        print(f"   Remaining today: {remaining} downloads")
        if count:
            print(f"   Target: {count} {media_label}")
        
        downloaded = 0
        errors = 0
        
        # Get posts iterator
        try:
            self.loading.start(f"Scanning {media_label}")
            posts_iterator = profile.get_posts()
            self.loading.stop(True)
        except Exception as e:
            self.loading.stop(False)
            error_str = str(e)
            friendly_msg = self.handle_http_error(error_str)
            if friendly_msg:
                print(f"❌ {friendly_msg}")
            else:
                print(f"❌ Cannot access posts: {error_str[:100]}")
            return
        
        for post in posts_iterator:
            if count and downloaded >= count:
                break
            
            # Filter by media type
            if media_type == 'posts' and post.is_video:
                continue
            if media_type == 'reels' and not post.is_video:
                continue
            
            # Check rate limit
            can_proceed, wait_time, message = self.rate_limiter.can_proceed('downloads')
            
            if not can_proceed:
                if wait_time > 0 and wait_time < 120:
                    print(f"\n {message} Waiting {wait_time:.0f} seconds...")
                    time.sleep(wait_time)
                    can_proceed, _, _ = self.rate_limiter.can_proceed('downloads')
                    if not can_proceed:
                        print(f"\n❌ Cannot continue - {message}")
                        break
                else:
                    print(f"\n❌ {message}")
                    break
            
            try:
                # Show download progress
                sys.stdout.write(f"\r📥 Downloading {media_label[:-1]} {downloaded + 1}... ")
                sys.stdout.flush()
                
                delay = self.rate_limiter.get_random_delay()
                time.sleep(delay)
                
                temp_dir = f"{safe_name}_temp"
                os.makedirs(temp_dir, exist_ok=True)
                
                self.loader.download_post(post, target=temp_dir)
                
                # Move files
                files_moved = 0
                for file in os.listdir(temp_dir):
                    ext = file.lower()
                    if media_type == 'posts' and ext.endswith(IMAGE_EXTENSIONS):
                        src = os.path.join(temp_dir, file)
                        dst = os.path.join(safe_name, file)
                        shutil.move(src, dst)
                        files_moved += 1
                    elif media_type == 'reels' and ext.endswith(VIDEO_EXTENSIONS):
                        src = os.path.join(temp_dir, file)
                        dst = os.path.join(safe_name, file)
                        shutil.move(src, dst)
                        files_moved += 1
                
                shutil.rmtree(temp_dir)
                
                if files_moved > 0:
                    downloaded += 1
                    errors = 0
                    self.rate_limiter.record_request('downloads', success=True)
                    
                    remaining_now = self.rate_limiter.get_remaining('downloads')
                    sys.stdout.write(f"\r✅ Downloaded {downloaded} {media_label} ({remaining_now} left)   \n")
                else:
                    sys.stdout.write(f"\r⚠️ No media found in this post\n")
                
                sys.stdout.flush()
                
            except instaloader.exceptions.ConnectionException as e:
                errors += 1
                error_str = str(e)
                friendly_msg = self.handle_http_error(error_str)
                
                if friendly_msg and ("401" in error_str or "403" in error_str):
                    print(f"\n❌ {friendly_msg}")
                    print("\nRecommendation: Wait 30-60 minutes before trying again")
                    break
                elif friendly_msg:
                    print(f"\n❌ {friendly_msg}")
                else:
                    print(f"\n⚠️ Connection issue: {error_str[:100]}")
                
                self.rate_limiter.record_request('downloads', success=False)
                
                if errors >= 3:
                    print("\n❌ Too many errors. Stopping download.")
                    break
                    
            except Exception as e:
                errors += 1
                error_str = str(e)
                friendly_msg = self.handle_http_error(error_str)
                if friendly_msg:
                    print(f"\n❌ {friendly_msg}")
                else:
                    print(f"\n⚠️ Error: {error_str[:100]}")
                self.rate_limiter.record_request('downloads', success=False)
                
                if errors >= 5:
                    print("\n❌ Too many errors. Stopping download.")
                    break
        
        if downloaded == 0:
            print(f"\n📭 No {media_label} found for @{profile_name}")
        else:
            print(f"\n✅ Downloaded {downloaded} {media_label} to './{safe_name}/'")
    
    def show_status(self):
        self.rate_limiter.show_status()
        if self.session_manager.is_authenticated():
            print("\n✅ Status: Logged in to Instagram")
            print("   Daily limit: 200 downloads")
        else:
            print("\n⚠️ Status: Not logged in")
            print("   Daily limit: 40 downloads")
            print("   💡 Type '3' then '1' to login for higher limits")
    
    def show_help(self):
        print("\n" + "-"*60)
        print("📋 INGRAB - Instagram Media Downloader")
        print("-"*60)
        print(f"\nVersion: {VERSION}")
        print(f"Developer: {AUTHOR}")
        print(f"LinkedIn: {LINKEDIN}")
        
        print("\nFEATURES:")
        print("  • Download profile pictures")
        print("  • Download posts (images)")
        print("  • Download reels (videos)")
        print("  • Automatic rate limiting protection")
        
        print("\n⚠️ LIMITATIONS:")
        print("  • Only PUBLIC profiles can be downloaded")
        print("  • 40 downloads/day without login")
        print("  • 200 downloads/day with login")
        print("  • Cannot download from private profiles (unless you follow them and login)")
        
        print("\nERROR MESSAGES EXPLAINED:")
        print("  • 401 / 403 - Instagram is temporarily blocking you")
        print("    → Wait 30-60 minutes before trying again")
        print("    → Login to Instagram to prevent this")
        print("    → Download fewer items (5-10 at a time)")
        print("")
        print("  • 429 - Too many requests")
        print("    → You're downloading too quickly")
        print("    → Wait 15-30 minutes")
        print("    → Our tool automatically adds delays to prevent this")
        print("")
        print("  • 404 - Profile not found")
        print("    → Check if the username is correct")
        print("    → Make sure the profile is public")
        
        print("\nBEST PRACTICES:")
        print("  • Login to Instagram for higher limits")
        print("  • Download 5-10 items at a time")
        print("  • Check daily usage before downloading")
        print("  • Download during off-peak hours (early morning)")
        print("-"*60)

# ============ UTILITY FUNCTIONS ============
def extract_username(input_value):
    """Extract username from URL or validate"""
    if not input_value:
        return None
    
    input_value = input_value.strip()
    if input_value.startswith('@'):
        input_value = input_value[1:]
    
    url_pattern = r'https?://(?:www\.)?instagram\.com/([A-Za-z0-9_.]+)/?'
    match = re.match(url_pattern, input_value)
    if match:
        return match.group(1)
    
    if re.match(r'^[A-Za-z0-9._]{1,30}$', input_value):
        return input_value
    
    return None

def report_bug():
    print("\n" + "-"*50)
    print("🐛 REPORT A BUG")
    print("-"*50)
    bug_details = input("\nDescribe the issue: ").strip()
    
    if not bug_details:
        print("❌ No description provided!")
        return
    
    subject = f"Ingrab Bug Report - {VERSION}"
    body = f"Bug: {bug_details}\nVersion: {VERSION}"
    gmail_link = f"https://mail.google.com/mail/?view=cm&fs=1&to={EMAIL}&su={subject}&body={body}"
    webbrowser.open(gmail_link)
    print("\n✅ Thank you for reporting!")

# ============ MAIN MENU ============
def main():
    """Main entry point"""
    downloader = IngrabDownloader()
    
    # Welcome banner
    print("\n" + "-"*60)
    print("   INGRAB - Instagram Media Downloader")
    print("-"*60)
    print(f"\nVersion: {VERSION} | Author: {AUTHOR}")
    print(f"LinkedIn: {LINKEDIN}")
    print("\nImportant Notes:")
    print("   • Only works with PUBLIC Instagram profiles")
    print("   • 40 downloads/day without login (200 with login)")
    print("   • Automatic delays between downloads to prevent blocking")
    print("   • If you see 401/403 errors, wait 30-60 minutes\n")
    
    # Offer login
    if not downloader.session_manager.is_authenticated():
        choice = input("Login to Instagram for higher limits? (y/n): ").strip().lower()
        if choice == 'y':
            downloader.session_manager.login()
    
    while True:
        print("\n" + "-"*50)
        print("   MAIN MENU")
        print("-"*50)
        print(" 1. Download Media")
        print(" 2. Check Daily Usage")
        print(" 3. Login/Logout")
        print(" 4. Help & Error Explanations")
        print(" 5. Report Bug")
        print(" 6. Exit")
        print("-"*50)
        
        try:
            option = input("\nChoose option (1-6): ").strip()
            
            if option == "1":
                print("\n" + "-"*40)
                input_value = input("Instagram Username or URL: ").strip()
                username = extract_username(input_value)
                
                if not username:
                    print("❌ Invalid username or URL!")
                    print("   Example: 'natgeo' or 'https://instagram.com/natgeo'")
                    input("\nPress Enter to continue...")
                    continue
                
                # Show remaining limits
                remaining = downloader.rate_limiter.get_remaining('downloads')
                print(f"\n✅ Target: @{username}")
                print(f"📊 Remaining downloads today: {remaining}")
                
                if remaining == 0:
                    print("\n❌ Daily limit reached! Please try again tomorrow.")
                    input("\nPress Enter to continue...")
                    continue
                
                # Get media type
                print("\n" + "-"*40)
                print("What would you like to download?")
                print("  1 - Posts (Images only)")
                print("  2 - Reels (Videos only)")
                print("  3 - Profile Picture")
                print("  B - Back to Main Menu")
                print("-"*40)
                
                media_choice = input("\nChoose (1-3): ").strip()
                
                if media_choice == "3":
                    downloader.download_profile_picture(username)
                    input("\nPress Enter to continue...")
                    continue
                elif media_choice.lower() == "b":
                    continue
                elif media_choice not in ["1", "2"]:
                    print("❌ Invalid choice!")
                    input("\nPress Enter to continue...")
                    continue
                
                media_type = 'posts' if media_choice == "1" else 'reels'
                max_allowed = min(20, remaining)
                
                print(f"\nHow many {media_type} would you like to download?")
                print(f"  Allowed range: 1 to {max_allowed}")
                print(f"  Type 'all' to download everything")
                print(f"  💡 Recommended: 5-10 to avoid rate limiting")
                
                count_input = input("\nEnter number or 'all': ").strip()
                
                try:
                    if count_input.lower() == 'all':
                        count = None
                    else:
                        count = int(count_input)
                        if count < 1:
                            count = 1
                        if count > max_allowed:
                            print(f"\n⚠️ Reducing to {max_allowed} (daily limit)")
                            count = max_allowed
                    
                    if count:
                        print(f"\n📥 Ready to download {count} {media_type}")
                    else:
                        print(f"\n📥 Ready to download all {media_type}")
                    
                    confirm = input("Proceed with download? (y/n): ").strip().lower()
                    if confirm == 'y':
                        downloader.download_media(username, media_type, count)
                    
                except ValueError:
                    print("❌ Invalid input! Please enter a number or 'all' ")
                
                input("\nPress Enter to continue...")
            
            elif option == "2":
                downloader.show_status()
                input("\nPress Enter to continue...")
            
            elif option == "3":
                print("\n" + "-"*40)
                print("1 - Login to Instagram")
                print("2 - Logout (clear session)")
                print("3 - Check Login Status")
                print("-"*40)
                
                sub = input("\nChoose (1-3): ").strip()
                if sub == "1":
                    downloader.session_manager.login()
                elif sub == "2":
                    downloader.session_manager.logout()
                elif sub == "3":
                    if downloader.session_manager.is_authenticated():
                        print("✅ Status: Logged in to Instagram")
                        print("   Daily limit: 200 downloads")
                        remaining = downloader.rate_limiter.get_remaining('downloads')
                        print(f"   Remaining today: {remaining} downloads")
                    else:
                        print("❌ Status: Not logged in")
                        print("   Daily limit: 40 downloads")
                        print("   Type '1' above to login for higher limits")
                input("\nPress Enter to continue...")
            
            elif option == "4":
                downloader.show_help()
                input("\nPress Enter to continue...")
            
            elif option == "5":
                report_bug()
                input("\nPress Enter to continue...")
            
            elif option == "6":
                print("\nThank you for using Ingrab!")
                sys.exit(0)
            
            else:
                print("❌ Invalid option! Please choose 1-6")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! See you soon.")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()