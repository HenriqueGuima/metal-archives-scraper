import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import glob

# TODO: save the discography data to a single CSV file

def get_last_processed_band():

    processed_files = glob.glob('bands_discos/*_discography.csv')
    if not processed_files:
        return None
    
    last_file = max(processed_files, key=os.path.getctime)
    last_band = os.path.basename(last_file).replace('_discography.csv', '')
    return last_band

def extract_discography(soup, band_id):
    discography = []
    disco_table = soup.select_one('table.display.discog')
    if disco_table:
        rows = disco_table.select('tbody tr')
        for row in rows:

            name_element = row.select_one('td a')
            name = name_element.text.strip() if name_element else 'Unknown Album'  

            type_element = row.select_one('td:nth-child(2)')
            type_ = type_element.text.strip() if type_element else 'Unknown Type'  

            year_element = row.select_one('td:nth-child(3)')
            year = year_element.text.strip() if year_element else 'Unknown Year'  

            reviews_element = row.select_one('td:nth-child(4) a')
            reviews_text = reviews_element.text.strip() if reviews_element else 'No Reviews'  

            discography.append([name, type_, year, reviews_text, band_id])
            print(f"Album: {name}, Type: {type_}, Year: {year}, Reviews: {reviews_text}, Band ID: {band_id}")
            print('-' * 40)

    else:
        print("Discography table not found.")
    return discography

def scrape_band_page(band_name, band_id):
    base_url = f"https://www.metal-archives.com/band/discography/id/{band_id}/tab/all"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    response = requests.get(base_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve data for {band_name}. Status Code: {response.status_code}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    discography = extract_discography(soup, band_id)

    sanitized_band_name = re.sub(r'[<>:"/\\|?*]', '_', str(band_name))

    if discography:
        df_disco = pd.DataFrame(discography, columns=["Album Name", "Type", "Year", "Reviews", "Band ID"])
        df_disco.to_csv(f"bands_discos/{sanitized_band_name}_discography.csv", index=False)

    print(f"Data for {band_name} saved successfully.")

def main():
    start_time = time.time()
    bands_df = pd.read_csv("metal_bands.csv")

    # print(f"Scraping {len(bands_df)} bands.")

    if 'Name' not in bands_df.columns or 'URL' not in bands_df.columns:
        print("CSV file is missing 'Name' or 'URL' columns.")
        return

    last_processed_band = get_last_processed_band()
    start_processing = False if last_processed_band else True

    for _, row in bands_df.iterrows():
        band_name = row['Name']
        band_url = row['URL']
        band_id = band_url.split('/')[-1]  

        if not start_processing:
            if band_name == last_processed_band:
                start_processing = True
            continue

        os.system('cls' if os.name == 'nt' else 'clear')

        print(f"Scraping {band_name}, ID: {band_id}")
        scrape_band_page(band_name, band_id)

        elapsed_time = time.time() - start_time
        hours, rem = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(rem, 60)
        print(f"Time elapsed: {int(hours):02}:{int(minutes):02}:{int(seconds):02}")

        time.sleep(1)
if __name__ == "__main__":
    main()
