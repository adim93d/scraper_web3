import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from urllib.parse import urljoin


def scrape_page(url):
    """
    Fetches the content of a given URL and returns a BeautifulSoup object.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/112.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

    return BeautifulSoup(response.text, 'html.parser')


def parse_jobs(soup, base_url):
    """
    Parses the BeautifulSoup object to extract job listings.
    Returns a list of dictionaries containing job details.
    """
    job_list = []

    # Each job listing is within a <tr> with class 'table_row'
    job_rows = soup.find_all('tr', class_='table_row')

    for job in job_rows:
        try:
            # Extract Title and Link
            title_tag = job.find('h2', class_='fs-6 fs-md-5 fw-bold my-primary')
            if title_tag:
                title = title_tag.get_text(strip=True)
                link_tag = title_tag.find_parent('a', href=True)
                link = urljoin(base_url, link_tag['href']) if link_tag else None
            else:
                title = None
                link = None

            # Extract Company
            company_tag = job.find('h3')
            company = company_tag.get_text(strip=True) if company_tag else None

            # Extract Posted Time
            time_tag = job.find('time')
            posted_time = time_tag.get_text(strip=True) if time_tag else None

            # Extract Location
            location_tag = job.find('span', style=lambda value: value and 'color: #d5d3d3' in value)
            location = location_tag.get_text(strip=True) if location_tag else None

            # Extract Compensation
            compensation_tag = job.find('p', class_='ps-0 mb-0 text-salary')
            if compensation_tag:
                # Clean the compensation text (e.g., "$21k - $64k")
                compensation = compensation_tag.get_text(strip=True).split(' ')[0]
            else:
                compensation = None

            # Create a dictionary for the job
            job_info = {
                'Title': title,
                'Company': company,
                'Location': location,
                'Compensation': compensation,
                'Posted Time': posted_time,
                'Job Link': link  # Added Job Link
            }

            job_list.append(job_info)
        except Exception as e:
            print(f"Error parsing job: {e}")
            continue

    return job_list


def get_next_page(soup, base_url):
    """
    Identifies and returns the URL of the next page, if it exists.
    """
    # Assuming there's a pagination section with a 'Next' button or link
    # Update the selector based on the actual pagination structure
    pagination = soup.find('ul', class_='pagination')  # Example selector
    if pagination:
        # Updated from 'text' to 'string' to fix DeprecationWarning
        next_link = pagination.find('a', string='Next')
        if next_link and 'href' in next_link.attrs:
            return urljoin(base_url, next_link['href'])

    # Alternative method: look for a link with rel='next'
    next_button = soup.find('a', rel='next')
    if next_button and 'href' in next_button.attrs:
        return urljoin(base_url, next_button['href'])

    return None


def main():
    base_url = "https://web3.career/entry-level+remote-jobs"
    current_url = base_url
    all_jobs = []
    page_number = 1  # To keep track of pages scraped
    max_pages = 10  # Maximum number of pages to scrape

    while current_url and page_number <= max_pages:
        print(f"Scraping page {page_number}: {current_url}")
        soup = scrape_page(current_url)
        if not soup:
            print("Failed to retrieve or parse the page.")
            break

        jobs = parse_jobs(soup, base_url)  # Pass base_url for correct link formation
        if not jobs:
            print("No jobs found on this page.")
            break

        all_jobs.extend(jobs)
        print(f"Found {len(jobs)} jobs on page {page_number}.")

        # Find the next page URL
        next_page = get_next_page(soup, base_url)
        if next_page and next_page != current_url:
            current_url = next_page
            page_number += 1
            time.sleep(1)  # Be polite and wait a bit before the next request
        else:
            print("No more pages to scrape.")
            break

    # Create a DataFrame and export to CSV
    if all_jobs:
        df = pd.DataFrame(all_jobs)
        df.to_csv('web3_career_jobs.csv', index=False)
        print(f"Scraping completed. {len(all_jobs)} jobs saved to 'web3_career_jobs.csv'.")
    else:
        print("No job data scraped.")


if __name__ == "__main__":
    main()
