from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import json

# Path of the HTML file / URL to scrape
PATH_HTML = r""
# Path of the chromedriver.exe for the Google Chrome browser
PATH_CHROME_DRIVER = r"C:\Program Files (x86)\chromedriver.exe"
# Determines if the browser-window should be displayed or not
HEADLESS_BROWSER = True
# Output name of the JSON file
JSON_OUTPUT_NAME = 'Booking.com Results'

# This function is used to verify if an element exists or not by checking the XPATH
def check_element(part, xpath):
    try:
        part.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True


def hotel_scraper():
    try:
        service = Service(executable_path=PATH_CHROME_DRIVER)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.headless = HEADLESS_BROWSER
        driver = webdriver.Chrome(options=chrome_options, service=service)

        html = PATH_HTML
        driver.get(html)

        # Red
        hotel_name = driver.find_element(By.XPATH, '//span[@id="hp_hotel_name"]').text
        address = driver.find_element(By.XPATH, '//span[@id="hp_address_subtitle"]').text
        location_rating_dict = {
            'Location Rating': driver.find_element(By.XPATH, '//div[@id="location_score_tooltip"]/p/strong').text,
            'Location Rating Score': driver.find_element(By.XPATH, '//div[@id="location_score_tooltip"]/p[1]').text.split('rated ')[1].split('! (')[0]
        }

        # Pink
        review_dict = {
            'Review Score': driver.find_element(By.XPATH, '//span[@class="average js--hp-scorecard-scoreval"]').text + ' / 10',
            'Number of reviews': driver.find_element(By.XPATH, '//strong[@class="count"]').text
        }

        # Blue
        description_body = driver.find_element(By.XPATH, '//div[@class="hotel_description_wrapper_exp "][p]')
        description_lines = description_body.find_elements(By.TAG_NAME, "p")
        description_dict = {}
        for ind, item in enumerate(description_lines):
            description_dict[f"Line {ind + 1}"] = item.text.strip().replace("\n", " ")

        # Green
        last_booking = driver.find_element(By.XPATH, '//div[@class="hp_last_booking"]').text
        room_categories = driver.find_element(By.XPATH, '//table[@id="maxotel_rooms"]')
        rooms = room_categories.find_elements(By.TAG_NAME, 'tr')
        room_categories_dict = {'Last booking': last_booking}
        for item in rooms[1:]:
            if check_element(item, './/td[@class="ftd"]'):
                room_name = item.find_element(By.XPATH, './/td[@class="ftd"]').text
            if check_element(item, './/i'):
                occupancy = item.find_element(By.XPATH, './/i').get_attribute('title').split('occupancy: ')[1]
            if check_element(item, './/span[@class="jq_tooltip with_kids"]'):
                children = item.find_element(By.XPATH, './/span[@class="jq_tooltip with_kids"]').get_attribute('title').split('Max children: ')[1]
            else:
                children = 'No'
            room_categories_dict[f'{room_name}'] = {'Maximum Occupancy': occupancy, 'With Children': children}

        # Yellow
        alternative_hotel_section = driver.find_element(By.XPATH, '//tr[@id="althotelsRow"]')
        alt_hotels = alternative_hotel_section.find_elements(By.XPATH, '//td[@class="althotelsCell tracked"]')
        alt_dict = {}
        for item in alt_hotels:
            if check_element(item, '//a[@class="althotel_link"]'):
                alt_name = item.find_element(By.XPATH, './/a[@class="althotel_link"]').text
                alt_stars = item.find_element(By.XPATH, './/span[@class="invisible_spoken"]').text
                link = item.find_element(By.XPATH, './/a').get_attribute('href')
            if check_element(item, '//span[@class="hp_compset_description"]'):
                alt_description = item.find_element(By.XPATH, './/span[@class="hp_compset_description"]').text
            if check_element(item, '//div[@class="althotelsDiv alt_hotels_info_row"]'):
                alt_score = item.find_element(By.XPATH, './/div[@class="althotelsDiv alt_hotels_info_row"]').text
            if check_element(item, '//p[@class="altHotels_most_recent_booking urgency_message_red"]'):
                alt_recent_booking = item.find_element(By.XPATH, './/p[@class="altHotels_most_recent_booking urgency_message_red"]').text
            alt_dict[alt_name] = {'Classification': alt_stars,
                                  'Link': link,
                                  'Description': alt_description,
                                  'Reviews': alt_score,
                                  'Recent Bookings': alt_recent_booking}

        summary_dict = {"Hotel name": hotel_name,
                        "Address": address,
                        "Location rating": location_rating_dict,
                        "Reviews": review_dict,
                        "Description": description_dict,
                        "Room categories": room_categories_dict,
                        "Alternative hotels": alt_dict}
        driver.quit()
        # Converting the summary dictionary into a JSON-object
        with open(f"{JSON_OUTPUT_NAME}.json", "w", encoding='utf-8') as jd:
            data = json.dumps(summary_dict, indent=4, ensure_ascii=False)
            jd.write(data)
        return data
    except Exception as e:
        print(e)


def main():
    hotel_scraper()


if __name__ == "__main__":
    main()
