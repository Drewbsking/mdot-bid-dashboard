import requests
from bs4 import BeautifulSoup
import os


def scrape_letting_dates(save_path):
    url = "https://mdotjboss.state.mi.us/BidLetting/BidLettingHome.htm"
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    letting_box = soup.find("div", id="lettingBox")
    if not letting_box:
        print("Could not find the lettingBox div.")
        return []

    inputs = letting_box.find_all("input", class_="lettingButtons")
    titles = [inp.get("title") for inp in inputs if inp.get("title")]

    if not titles:
        print("No titles found in lettingBox.")
    else:
        with open(save_path, "w", encoding="utf-8") as f:
            for t in titles:
                f.write(t + "\n")
        print(f"Saved {len(titles)} letting dates to {save_path}.")

    return titles


def download_file(url, save_dir, letting_date):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            content_type = response.headers.get("Content-Type", "")
            content = response.content
            content_text = content.decode(errors="ignore")

            if (
                "An Error Occurred while processing your request" in content_text
                or "text/html" in content_type
                or len(content) < 1024  # Too small to be a real Excel file
            ):
                print(f"Skipped {letting_date}: Invalid or error page.")
                return None

            filename = letting_date + ".xlsx"
            save_path = os.path.join(save_dir, filename)
            os.makedirs(save_dir, exist_ok=True)
            with open(save_path, 'wb') as file:
                file.write(content)
            print(f"Downloaded: {filename}")
            return save_path
        else:
            print(f"Failed to download from {url}. Status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Error downloading from {url}: {e}")
        return None



def main():
    txt_file = "Dates.txt"

    # Step 1: Scrape letting dates and write to file
    letting_dates = scrape_letting_dates(txt_file)
    if not letting_dates:
        return

    # Step 2: Set download directory to ./xlsx next to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    save_dir = os.path.join(script_dir, "xlsx")

    # Step 3: Download files using letting dates
    for part in letting_dates:
        part = part.strip()
        url = f"https://mdotjboss.state.mi.us/BidLetting/getFileByName.htm?fileName={part}/btaexcel.xlsx"
        download_file(url, save_dir, part)




if __name__ == "__main__":
    main()
