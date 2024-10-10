import instaloader  # Import instaloader library directly
import os
import shutil
import time
import sys
import re
import webbrowser  # Import webbrowser module

# ANSI escape codes for text formatting (bold, underline, and colors)
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
RESET = '\033[0m'
RED = '\033[91m'
GREEN = '\033[92m'
CYAN = '\033[96m'
GREY = '\033[37m'

def loading_animation():
    """Displays a loading animation."""
    print(BOLD + "Loading" + RESET, end="")
    for _ in range(3):
        print(".", end="")
        sys.stdout.flush()
        time.sleep(0.5)
    print()  # Move to the next line after loading

def is_valid_instagram_url(url):
    """Validates the Instagram profile URL."""
    regex = r'https?://(www\.)?instagram\.com/[A-Za-z0-9._]+/?'
    return re.match(regex, url) is not None

def download_posts(profile_url, recent_count=None):
    loader = instaloader.Instaloader()
    profile_name = profile_url.strip('/').split('/')[-1]
    
    try:
        profile = instaloader.Profile.from_username(loader.context, profile_name)
    except Exception as e:
        print(BOLD + f"Error: {e}" + RESET)
        return

    count = 0
    # Create the target directory if it doesn't exist
    if not os.path.exists(profile_name):
        os.makedirs(profile_name)

    loading_animation()  # Show loading animation

    for post in profile.get_posts():
        if not post.is_video:  # Download only non-video posts (images)
            temp_dir = f"{profile_name}_temp"
            os.makedirs(temp_dir, exist_ok=True)
            loader.download_post(post, target=temp_dir)  # Download to temp dir
            
            # Move image files to the main profile directory
            for file in os.listdir(temp_dir):
                if file.endswith('.jpg') or file.endswith('.png'):
                    shutil.move(os.path.join(temp_dir, file), os.path.join(profile_name, file))
            
            # Cleanup the temp directory
            shutil.rmtree(temp_dir)
            count += 1
            if recent_count and count >= recent_count:
                break

    if count == 0:
        print(BOLD + f"No images found for {profile_name}." + RESET)
    else:
        print(BOLD + f"{count} images downloaded successfully." + RESET)

def download_videos(profile_url, recent_count=None):
    loader = instaloader.Instaloader()
    profile_name = profile_url.strip('/').split('/')[-1]

    try:
        profile = instaloader.Profile.from_username(loader.context, profile_name)
    except Exception as e:
        print(BOLD + f"Error: {e}" + RESET)
        return

    count = 0
    # Create the target directory if it doesn't exist
    if not os.path.exists(profile_name):
        os.makedirs(profile_name)

    loading_animation()  # Show loading animation

    for post in profile.get_posts():
        if post.is_video:  # Download only video posts (reels)
            temp_dir = f"{profile_name}_temp"
            os.makedirs(temp_dir, exist_ok=True)
            loader.download_post(post, target=temp_dir)  # Download to temp dir
            
            # Move video files to the main profile directory
            for file in os.listdir(temp_dir):
                if file.endswith('.mp4'):
                    shutil.move(os.path.join(temp_dir, file), os.path.join(profile_name, file))
            
            # Cleanup the temp directory
            shutil.rmtree(temp_dir)
            count += 1
            if recent_count and count >= recent_count:
                break

    if count == 0:
        print(BOLD + f"No reels found for {profile_name}." + RESET)
    else:
        print(BOLD + f"{count} reels downloaded successfully." + RESET)

def download_all(profile_url, recent_count=None):
    download_posts(profile_url, recent_count)
    download_videos(profile_url, recent_count)

def report_bug():
    """Allows the user to report a bug via Gmail.""" 
    bug_details = input(BOLD + "Please describe the bug you encountered: " + RESET)
    subject = "Bug Report from Ingrab"
    body = f"Bug Details: {bug_details}"
    
    # Construct the Gmail URL
    gmail_link = f"https://mail.google.com/mail/?view=cm&fs=1&to=bugingrab@gmail.com&su={subject}&body={body}"
    
    webbrowser.open(gmail_link) 
    print(BOLD + "Thank you for reporting a bug. \nYour report has been submitted successfully!" + RESET)

def show_details():
    """Displays project details and developer information."""
    print("\n" + BOLD + "\033[91m--- What is INGRAB? ---\033[0m" + RESET)  # Title in red

    # Project description
    print("Ingrab is a user-friendly application designed for downloading posts and reels from Instagram user profiles.")
    print("With a simple interface, users can easily access their favorite media content without hassle.")

    # Developer information
    print("\033[92m" +  "DEVELOPER: SHUBH TRIPATHI" + RESET + "\033[0m")  # Developer name in green
    print("\033[92m" +  "LINKEDIN PROFILE: https://www.linkedin.com/in/ishubtripathi/" + RESET + "\033[0m") 

    # Additional details
    print("\033[96m" + BOLD + "Version: 1.0.1" + RESET + "\033[0m")  # Version in cyan
    print("\033[96m" + BOLD + "Features:" + RESET + "\033[0m") 
    print("- Download posts and reels from Instagram profiles.")
    print("- Download recent media posts with a single click.")
    print("- Easy navigation and usage for all users.")

    print("\033[90m" + "------------------------\n" + RESET)  # Separator in dark gray

def main():
    print("\n-------------------------------")
    print(RED + BOLD + "✌ --- WELCOME TO INGRAB ---✌" + RESET) 
    print("-------------------------------")

    while True:
        print("\n" + GREY + BOLD + "--- Main Menu ---" + RESET)
        print("1 - USE INGRAB")
        print("2 - DETAILS")
        print("3 - VERSION")
        print("4 - REPORT BUG")
        print((RED + "5 - EXIT") + RESET)

        try:
            option = int(input(GREEN + BOLD + "Choose an option: " + RESET))  # Change prompt to green
            
            if option == 1:
                profile_url = input("Enter the Instagram profile URL: ")
                # Validate the Instagram URL
                if not is_valid_instagram_url(profile_url):
                    print(BOLD + "Error: Please enter a valid Instagram profile URL." + RESET)
                    continue  # Go back to the main menu
                
                print("\n" + GREY + BOLD + "--- Download Options ---" + RESET)
                print("1 - All posts")
                print("2 - All reels")
                print("3 - All posts and reels")
                print("4 - Recent 5 posts")
                print("5 - Recent 5 reels")
                print("6 - Recent 5 posts and reels")
                
                try:
                    download_option = int(input(GREEN + BOLD + "Choose an option for downloading: " + RESET))
                    if download_option == 1:
                        download_posts(profile_url)
                    elif download_option == 2:
                        download_videos(profile_url)
                    elif download_option == 3:
                        download_all(profile_url)
                    elif download_option == 4:
                        download_posts(profile_url, recent_count=5)
                    elif download_option == 5:
                        download_videos(profile_url, recent_count=5)
                    elif download_option == 6:
                        download_all(profile_url, recent_count=5)
                    else:
                        print(BOLD + "Invalid option. Please choose a number between 1 and 6." + RESET)
                except ValueError:
                    print(BOLD + "Error: Please enter a valid number for the option." + RESET)

            elif option == 2:
                show_details()  # Show project details

            elif option == 3:
                print(BOLD + "Version: 1.0.1" + RESET)

            elif option == 4:
                report_bug()  # Call the bug reporting function

            elif option == 5:
                print(BOLD + "Thank you for using Ingrab! ❤︎" + RESET)
                break  # Exit the loop and the program
            
            else:
                print(BOLD + "Invalid option. Please choose a number between 1 and 5." + RESET)

        except ValueError:
            print(BOLD + "Error: Please enter a valid number for the option." + RESET)

if __name__ == "__main__":
    main()
