import instaloader
import os
import shutil
import time
import sys
import re
import webbrowser

def loading_animation(duration=3):
    """Displays a loading animation."""
    spinner = ['|', '/', '-', '\\']
    end_time = time.time() + duration

    print("Loading ", end="", flush=True)
    while time.time() < end_time:
        for symbol in spinner:
            print(f"\rLoading {symbol}", end="", flush=True)
            time.sleep(0.2) 
    print("\nInitializing download....") 

def is_valid_instagram_url(url):
    """Validates the Instagram profile URL."""
    if url is None:  # Ensure url is not None
        return False
    regex = r'https?://(www\.)?instagram\.com/[A-Za-z0-9._]+/?'
    return re.match(regex, url) is not None

def extract_username(input_value):
    """Extracts the username from the input (either URL or direct username)."""
    if is_valid_instagram_url(input_value):
        return input_value.strip('/').split('/')[-1]  # Extract from URL
    return input_value  # Assume it's a username

def download_profile_picture(profile_name):
    """Downloads the Instagram profile picture."""
    loader = instaloader.Instaloader()
    
    try:
        profile = instaloader.Profile.from_username(loader.context, profile_name)
        loader.download_profilepic(profile)
        print(f"Profile picture of {profile_name} downloaded successfully.")
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"Error: Profile '{profile_name}' does not exist.")
    except instaloader.exceptions.PrivateProfileNotFollowedException:
        print(f"Error: Profile '{profile_name}' is private and not followed.")
    except Exception as e:
        print(f"Unexpected error while downloading profile picture: {e}")

def download_stories(profile_name):
    """Downloads Instagram stories of a user."""
    loader = instaloader.Instaloader()
    
    try:
        profile = instaloader.Profile.from_username(loader.context, profile_name)
        if profile.has_public_story:
            loader.download_stories(userids=[profile.userid], filename_target=f'{profile_name}_stories')
            print(f"Stories of {profile_name} downloaded successfully.")
        else:
            print(f"No public stories found for {profile_name}.")
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"Error: Profile '{profile_name}' does not exist.")
    except instaloader.exceptions.PrivateProfileNotFollowedException:
        print(f"Error: Profile '{profile_name}' is private and not followed.")
    except Exception as e:
        print(f"Unexpected error while downloading stories: {e}")

def download_posts(profile_name, recent_count=None):
    """Downloads posts of a user."""
    loader = instaloader.Instaloader()
    
    try:
        profile = instaloader.Profile.from_username(loader.context, profile_name)
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"Error: Profile '{profile_name}' does not exist.")
        return
    except instaloader.exceptions.PrivateProfileNotFollowedException:
        print(f"Error: Profile '{profile_name}' is private and not followed.")
        return
    except Exception as e:
        print(f"Unexpected error while accessing profile: {e}")
        return

    count = 0
    if not os.path.exists(profile_name):
        os.makedirs(profile_name)

    loading_animation()

    for post in profile.get_posts():
        try:
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
        except Exception as e:
            print(f"Error while downloading post: {e}")

    if count == 0:
        print(f"No images found for {profile_name}.")
    else:
        print(f"{count} images downloaded successfully.")

def download_videos(profile_name, recent_count=None):
    """Downloads video posts (reels) of a user."""
    loader = instaloader.Instaloader()

    try:
        profile = instaloader.Profile.from_username(loader.context, profile_name)
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"Error: Profile '{profile_name}' does not exist.")
        return
    except instaloader.exceptions.PrivateProfileNotFollowedException:
        print(f"Error: Profile '{profile_name}' is private and not followed.")
        return
    except Exception as e:
        print(f"Unexpected error while accessing profile: {e}")
        return

    count = 0
    if not os.path.exists(profile_name):
        os.makedirs(profile_name)

    loading_animation()

    for post in profile.get_posts():
        try:
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
        except Exception as e:
            print(f"Error while downloading video: {e}")

    if count == 0:
        print(f"No reels found for {profile_name}.")
    else:
        print(f"{count} reels downloaded successfully.")

def download_highlights(profile_name):
    """Downloads Instagram highlights of a user."""
    loader = instaloader.Instaloader()

    try:
        profile = instaloader.Profile.from_username(loader.context, profile_name)
        highlights = loader.get_highlights(profile)

        if highlights:
            for highlight in highlights:
                loader.download_highlight(highlight, target=f'{profile_name}_highlights')
            print(f"Highlights of {profile_name} downloaded successfully.")
        else:
            print(f"No highlights found for {profile_name}.")
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"Error: Profile '{profile_name}' does not exist.")
    except instaloader.exceptions.PrivateProfileNotFollowedException:
        print(f"Error: Profile '{profile_name}' is private and not followed.")
    except Exception as e:
        print(f"Unexpected error while downloading highlights: {e}")

def download_all(profile_name):
    """Downloads all posts and reels."""
    download_posts(profile_name)  # All posts
    download_videos(profile_name)  # All videos

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
    print("\nVersion: 1.3.3")
    print("\nFeatures:")
    print("- Download profile picture of any PUBLIC Instagram profiles.")
    print("- Download stories from public profiles.")
    print("- Download highlights from profiles.")
    print("- Download recent media posts from user profiles.")
    print("- Download recent reels from user profiles.")
    print("- Specify the number of recent posts/reels to download.")
    print("- Direct option to download all media (posts and reels) from a profile.")
    print("- Easy navigation and usage for all users.")
    print("- Provides feedback for download success and error handling.")
    print("- Bug reporting feature for user feedback.")
    print("- Efficient for quick downloads.")
    print("- Frequent updates to ensure compatibility with Instagram changes.\n")


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
                input_value = input("Enter Instagram Profile URL or Username: ")
                profile_name = extract_username(input_value)

                if not is_valid_instagram_url(input_value) and not profile_name:
                    print("Error: Invalid Instagram profile URL or username.")
                    continue

                while True:
                    print("\n------- Download Options -------")
                    print("1 - Download Profile Picture")
                    print("2 - Download Stories")
                    print("3 - Download Highlights")
                    print("4 - Download Posts")
                    print("5 - Download Reels")
                    print("6 - Download Recent Posts")
                    print("7 - Download Recent Reels")
                    print("8 - Download All Recent Media")
                    print("E - Exit Download Options")
                    print("-------------------------------")

                    try:
                        download_option = input("Choose an option: ").strip()

                        if download_option == "1":
                            download_profile_picture(profile_name)
                        elif download_option == "2":
                            download_stories(profile_name)
                        elif download_option == "3":
                            download_highlights(profile_name)
                        elif download_option == "4":
                            download_posts(profile_name)  # Remove recent count
                        elif download_option == "5":
                            download_videos(profile_name)  # Remove recent count
                        elif download_option == "6":
                            recent_count = int(input("How many recent posts would you like to download? "))
                            download_posts(profile_name, recent_count=recent_count)
                        elif download_option == "7":
                            recent_count = int(input("How many recent reels would you like to download? "))
                            download_videos(profile_name, recent_count=recent_count)
                        elif download_option == "8":
                            print("Downloading all recent media...")
                            download_all(profile_name)  # Directly download all media
                        elif download_option.lower() == "e":
                            print("Exiting the download options...")
                            break
                        else:
                            print("Error: Invalid option selected. Please try again.")
                    
                    except ValueError:
                        print("Error: Invalid input. Please enter a number corresponding to the options.")
                    except Exception as e:
                        print(f"Unexpected error in download options: {e}")

            elif option == 2:
                show_details()
            elif option == 3:
                print("Version: 1.3.3")
                print("\nFeatures:")
                print("- Download profile picture of any PUBLIC Instagram profiles.")
                print("- Download stories from public profiles.")
                print("- Download highlights from profiles.")
                print("- Download recent media posts from user profiles.")
                print("- Download recent reels from user profiles.")
                print("- Specify the number of recent posts/reels to download.")
                print("- Direct option to download all media (posts and reels) from a profile.")
                print("- Easy navigation and usage for all users.")
                print("- Provides feedback for download success and error handling.")
                print("- Bug reporting feature for user feedback.")
                print("- Efficient for quick downloads.")
                print("- Frequent updates to ensure compatibility with Instagram changes.\n")
            elif option == 4:
                report_bug()
            elif option == 5:
                print("Thank you for using Ingrab! Goodbye!")
                sys.exit(0)
            else:
                print("Error: Invalid option selected. Please try again.")

        except ValueError:
            print("Error: Invalid input. Please enter a number.")
        except Exception as e:
            print(f"Unexpected error in main menu: {e}")

if __name__ == "__main__":
    main()
