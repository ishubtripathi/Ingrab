import instaloader
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
    print()  # Move to the next line after the loading

def is_valid_instagram_url(url):
    """Validates the Instagram profile URL."""
    regex = r'https?://(www\.)?instagram\.com/[A-Za-z0-9._]+/?'
    return re.match(regex, url) is not None

def download_posts(profile_url, recent_count=None):
    loader = instaloader.Instaloader()
    profile_name = profile_url.strip('/').split('/')[-1]
    profile = instaloader.Profile.from_username(loader.context, profile_name)

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
        print(f"No images found for {profile_name}.")
    else:
        print(f"{count} images downloaded successfully.")

def download_videos(profile_url, recent_count=None):
    loader = instaloader.Instaloader()
    profile_name = profile_url.strip('/').split('/')[-1]
    profile = instaloader.Profile.from_username(loader.context, profile_name)

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
    
    # Construct the Gmail URL
    gmail_link = f"https://mail.google.com/mail/?view=cm&fs=1&to=ishubtripathi@gmail.com&su={subject}&body={body}"
    
    webbrowser.open(gmail_link) 
    print("Thank you for reporting a bug. \nYour report has been submitted successfully!")


def main():
    print("\nWelcome to Ingrab!")
    
    while True:
        print("\nOptions:")
        print("1 - User Ingrab")
        print("2 - Help")
        print("3 - Developer")
        print("4 - Version")
        print("5 - Report Bug")
        print("6 - Exit")

        try:
            option = int(input("Choose an option : "))
            
            if option == 1:
                profile_url = input("Enter the Instagram profile URL: ")
                # Validate the Instagram URL
                if not is_valid_instagram_url(profile_url):
                    print("Error: Please enter a valid Instagram profile URL.")
                    continue  # Go back to the main menu
                
                print("Options:")
                print("1 - Download all images")
                print("2 - Download all videos (reels)")
                print("3 - Download both images and videos (reels)")
                print("4 - Download the recent 5 images")
                print("5 - Download the recent 5 videos (reels)")
                print("6 - Download the recent 5 images and videos (reels)")
                
                try:
                    download_option = int(input("Choose an option for downloading: "))
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
                print("Help: This application allows you to download images and videos from Instagram profiles.")
                print("Enter the profile URL and choose the type of media to download.")
            
            elif option == 3:
                print("Developer: Your Name - [Your Contact Information or Website]")

            elif option == 4:
                print("Version: 1.0.1")

            elif option == 5:
                report_bug()  # Call the bug reporting function

            elif option == 6:
                print("Exiting the application.")
                break  # Exit the loop and the program
            
            else:
                print("Invalid option. Please choose a number between 1 and 6.")

        except ValueError:
            print("Error: Please enter a valid number for the option.")

if __name__ == "__main__":
    main()
