import requests
import concurrent.futures
import os

# Configuration
INPUT_FILE = "README.txt"       # The file containing the raw list of URLs
OUTPUT_FILE = "valid_repos.txt" # The file where valid, unique URLs will be saved

def clean_and_read_urls(filename):
    """
    Reads the file, removes whitespace, strips trailing slashes,
    and removes duplicates.
    """
    if not os.path.exists(filename):
        print(f"[-] File {filename} not found!")
        return []

    with open(filename, 'r', encoding='utf-8') as f:
        # 1. strip(): Removes surrounding whitespace/newlines.
        # 2. rstrip('/'): Removes the trailing slash (e.g., 'url/' becomes 'url').
        #    This ensures 'repo/' and 'repo' are treated as the same URL.
        raw_urls = [line.strip().rstrip('/') for line in f if line.strip()]
    
    # 3. set(): Automatically removes duplicate entries.
    unique_urls = list(set(raw_urls))
    return unique_urls

def check_url(url):
    """
    Sends an HTTP GET request to check if the repository exists.
    Returns the URL if status code is 200, otherwise None.
    """
    try:
        # Timeout is set to 5 seconds to avoid hanging on dead links.
        # allow_redirects=True handles cases where GitHub redirects repo names.
        response = requests.get(url, timeout=5, allow_redirects=True)
        if response.status_code == 200:
            return url
    except requests.RequestException:
        # Catches connection errors, timeouts, etc.
        pass
    return None

def main():
    print("[*] Reading and cleaning URLs...")
    urls = clean_and_read_urls(INPUT_FILE)
    print(f"[*] Found {len(urls)} unique URLs after cleaning duplicates.")
    print("[*] Starting validation check (using multi-threading)...")

    valid_links = []
    
    # Use ThreadPoolExecutor to check multiple URLs simultaneously.
    # max_workers=20 means 20 checks happen at the same time (much faster).
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        # Map the check_url function to the list of URLs
        results = executor.map(check_url, urls)
        
        # Collect valid results
        for result in results:
            if result:
                valid_links.append(result)
                print(f"[+] Found valid: {result}")

    # Write the final valid list to the output file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for link in valid_links:
            f.write(link + '\n')

    print("-" * 30)
    print(f"[✓] Done! Saved {len(valid_links)} valid repositories to '{OUTPUT_FILE}'")

if __name__ == "__main__":
    main()