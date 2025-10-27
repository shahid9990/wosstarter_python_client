# This file fetches journal name, issn, e_issn, publisher, country, address, edition, and category and saves it to a csv file.
import time
import csv
import clarivate.wos_journals.client
from clarivate.wos_journals.client.api import journals_api
from pprint import pprint

# --------------------------
# Configuration
# --------------------------
configuration = clarivate.wos_journals.client.Configuration(
    host="https://api.clarivate.com/apis/wos-journals/v1"
)

configuration.api_key['key'] = '96b3108392316ffeffebca5e9422a16f03675a7e'

# --------------------------
# File setup
# --------------------------
start = 1
output_file = f"journals/journals_data_{start}.csv"

# CSV header
header = ["name", "issn", "e_issn", "publisher", "country", "address", "edition", "category"]

with open(output_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(header)

    # --------------------------
    # API Client Setup
    # --------------------------
    max_pages = 200    # number of pages to fetch
    limit = 50          # number of journals per page
    jcr_year = 2024

    with clarivate.wos_journals.client.ApiClient(configuration) as api_client:
        api_instance = journals_api.JournalsApi(api_client)

        for page in range(start, max_pages + start):
            try:
                print(f"\n--- Fetching Page {page} ---")
                api_response = api_instance.journals_get(jcr_year=jcr_year, page=page, limit=limit)

                if not api_response.hits:
                    print("No more journals found, stopping early.")
                    break

                for journal in api_response.hits:
                    journal_id = journal['id']
                    print(f"Fetching details for: {journal_id}")

                    try:
                        # Fetch complete journal details
                        detail = api_instance.journals_id_get(journal_id)
                        data = detail.to_dict() if hasattr(detail, "to_dict") else detail

                        # Extract fields safely
                        name = data.get("name", "")
                        issn = data.get("issn", "")
                        e_issn = data.get("e_issn", "")

                        publisher_info = data.get("publisher", {}) or {}
                        publisher_name = publisher_info.get("name", "")
                        country = publisher_info.get("country_region", "")
                        address = publisher_info.get("address", "")

                        # Handle multiple categories (flattened)
                        categories = data.get("categories", [])
                        if categories:
                            for cat in categories:
                                edition = cat.get("edition", "")
                                category = cat.get("name", "")
                                writer.writerow([name, issn, e_issn, publisher_name, country, address, edition, category])
                        else:
                            writer.writerow([name, issn, e_issn, publisher_name, country, address, "", ""])

                    except clarivate.wos_journals.client.ApiException as e:
                        print(f"Failed to get details for {journal_id}: {e}")

                    # Avoid rate limit
                    time.sleep(0.3)

            except clarivate.wos_journals.client.ApiException as e:
                print(f"Error fetching page {page}: {e}")
                break

            time.sleep(0.5)

print(f"\nDone! Journal data saved to '{output_file}'")
