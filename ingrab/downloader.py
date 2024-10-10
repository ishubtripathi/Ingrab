import instaloader

def download_posts(profile_url):
    loader = instaloader.Instaloader()
    profile_name = profile_url.strip('/').split('/')[-1]
    profile = instaloader.Profile.from_username(loader.context, profile_name)

    print(f"Downloading all posts from {profile_name}'s profile...")
    for post in profile.get_posts():
        if not post.is_video:  # Download only non-video posts (images)
            loader.download_post(post, target=profile_name)
    print(f"All posts downloaded successfully.")

def download_videos(profile_url):
    loader = instaloader.Instaloader()
    profile_name = profile_url.strip('/').split('/')[-1]
    profile = instaloader.Profile.from_username(loader.context, profile_name)

    print(f"Downloading all videos (reels) from {profile_name}'s profile...")
    for post in profile.get_posts():
        if post.is_video:  # Download only video posts (reels)
            loader.download_post(post, target=profile_name)
    print(f"All videos downloaded successfully.")

def download_all(profile_url):
    loader = instaloader.Instaloader()
    profile_name = profile_url.strip('/').split('/')[-1]
    profile = instaloader.Profile.from_username(loader.context, profile_name)

    print(f"Downloading all posts and reels from {profile_name}'s profile...")
    for post in profile.get_posts():
        loader.download_post(post, target=profile_name)
    print(f"All posts and reels downloaded successfully.")

def main():
    profile_url = input("Enter the Instagram profile URL: ")
    print("Options:")
    print("1 - Download all posts")
    print("2 - Download all videos (reels)")
    print("3 - Download both posts and videos (reels)")
    
    option = int(input("Choose an option (1/2/3): "))

    if option == 1:
        download_posts(profile_url)
    elif option == 2:
        download_videos(profile_url)
    elif option == 3:
        download_all(profile_url)
    else:
        print("Invalid option.")
