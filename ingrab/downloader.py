import instaloader  # Import instaloader library directly
import os
import shutil
import time
import sys
import re
import webbrowser  # Import webbrowser module

def loading_animation():
    """Displays a loading animation."""
    print("Loading", end="")
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
        print(f"Error: {e}")
        return

    count = 0
    if not os.path.exists(profile_name):
        os.makedirs(profile_name)

    loading_animation()

    for post in profile.get_posts():
        if not post.is_video:  # Download only non-video posts (images)
            temp_dir = f"{profile_name}_temp"
            os.makedirs(temp_dir, exist_ok=True)
            loader.download_post(post, target=temp_dir)
            
            for file in os.listdir(temp_dir):
                if file.endswith('.jpg') or file.endswith('.png'):
                    shutil.move(os.path.join(temp_dir, file), os.path.join(profile_name, file))
            
            shutil.rmtree(temp_dir)
            count += 1
            if recent_count and count >= recent_count:
                break

    if count == 0:
        print(f"No images found for {profile_name}.")
    else:
        print(f"{count} images downloaded successfully.")

def download_videos(profile_url, recent_count=None):
    loader = instaloader.Instaloader()
    profile_name = profile_url.strip('/').split('/')[-1]

    try:
        profile = instaloader.Profile.from_username(loader.context, profile_name)
    except Exception as e:
        print(f"Error: {e}")
        return

    count = 0
    if not os.path.exists(profile_name):
        os.makedirs(profile_name)

    loading_animation()

    for post in profile.get_posts():
        if post.is_video:  # Download only video posts (reels)
            temp_dir = f"{profile_name}_temp"
            os.makedirs(temp_dir, exist_ok=True)
            loader.download_post(post, target=temp_dir)
            
            for file in os.listdir(temp_dir):
                if file.endswith('.mp4'):
                    shutil.move(os.path.join(temp_dir, file), os.path.join(profile_name, file))
            
            shutil.rmtree(temp_dir)
            count += 1
            if recent_count and count >= recent_count:
                break

    if count == 0:
        print(f"No reels found for {profile_name}.")
    else:
        print(f"{count} reels downloaded successfully.")

def download_all(profile_url, recent_count=None):
    download_posts(profile_url, recent_count)
    download_videos(profile_url, recent_count)

def report_bug():
    """Allows the user to report a bug via Gmail.""" 
    bug_details = input("Please describe the bug you encountered: ")
    subject = "Bug Report from Ingrab"
    body = f"Bug Details: {bug_details}"
    
    gmail_link = f"https://mail.google.com/mail/?view=cm&fs=1&to=bugingrab@gmail.com&su={subject}&body={body}"
    
    webbrowser.open(gmail_link) 
    print("Thank you for reporting a bug. \nYour report has been submitted successfully!")

def show_details():
    """Displays project details and developer information."""
    print("\n--- What is INGRAB? ---")

    print("Ingrab is a user-friendly application designed for downloading posts and reels from Instagram user profiles.")
    print("With a simple interface, users can easily access their favorite media content without hassle.\n")

    print("DEVELOPER: SHUBH TRIPATHI")
    print("LINKEDIN PROFILE: https://www.linkedin.com/in/ishubtripathi/")

    print("\nVersion: 1.2.6")
    print("\nFeatures:")
    print("- Download posts and reels from Instagram profiles.")
    print("- Download recent media posts with a single click.")
    print("- Easy navigation and usage for all users.\n")

def main():
    print("\n-------------------------------")
    print("------ WELCOME TO INGRAB ------")
    print("-------------------------------")

    while True:
        print("\n---------- Main Menu ----------")
        print("1 - USE INGRAB")
        print("2 - DETAILS")
        print("3 - VERSION")
        print("4 - REPORT BUG")
        print("5 - EXIT")
        print("-------------------------------")

        try:
            option = int(input("Choose an option: "))
            
            if option == 1:
                profile_url = input("Enter the Instagram profile URL: ")
                if not is_valid_instagram_url(profile_url):
                    print("Error: Please enter a valid Instagram profile URL.")
                    continue
                
                print("\n----- Download Options -----")
                print("1 - All posts")
                print("2 - All reels")
                print("3 - All posts and reels")
                print("4 - Recent 5 posts")
                print("5 - Recent 5 reels")
                print("6 - Recent 5 posts and reels")
                print("-------------------------------")
                
                try:
                    download_option = int(input("Choose an option : "))
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
                        print("Invalid option. Please choose a number between 1 and 6.")
                except ValueError:
                    print("Error: Please enter a valid number for the option.")

            elif option == 2:
                show_details()

            elif option == 3:
                print("Version: 1.2.6")

            elif option == 4:
                report_bug()

            elif option == 5:
                print("\nThank you for using Ingrab!")
                break
            
            else:
                print("Invalid option. Please choose a number between 1 and 5.")

        except ValueError:
            print("Error: Please enter a valid number for the option.")

if __name__ == "__main__":
    main()
