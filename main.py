from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import sys
import os
import re
import yaml
import time


def main():
    def grab_track_from_element(element, track_urls) -> str:

        track_action = element.find_element(By.CSS_SELECTOR, "span.track-action")
        track_action.click()

        menu_list = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.menu-list")))

        track_share = menu_list.find_element(By.CSS_SELECTOR, "ul > li.track-share")

        link_element = track_share.find_element(By.CSS_SELECTOR, "a")
        link_element.click()

        modal_content = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.modal-content")))

        input_element = modal_content.find_element(By.CSS_SELECTOR, "input.share-url")
        value = input_element.get_attribute("value")

        if value not in track_urls:
            track_urls.append(value)

        close_button = modal_content.find_element(By.CSS_SELECTOR, "button.close")
        close_button.click()

        return value

    with open("config.yml", "r") as config_file:
        config = yaml.safe_load(config_file)

    options = Options()
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0")
    if bool(config["headless"]):
        options.add_argument("-headless")

    driver = webdriver.Firefox(options=options)
    driver.set_window_size(1500, 1000)

    wait = WebDriverWait(driver, 10)

    if not os.path.exists("output"):
        os.makedirs("output")

    email = config["email"]
    password = config["password"]

    # Ask the user for the URL
    url = input("Qobuz Playlist URL: ")

    if "open" in url:
        print("Url open.qobuz.com not supported!\nUse play.qobuz.com instead!")
        driver.quit()
        sys.exit(0)

    driver.get(url)
    print("Login")

    cookies_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[id="onetrust-accept-btn-handler"]')))
    cookies_button.click()

    time.sleep(2)

    login_btn = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button.ButtonPrimary')))
    login_btn.click()

    login_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="_username"]')))
    login_input.send_keys(email)

    password_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="_password"]')))
    password_input.send_keys(password)

    hide_element_script = """
    var element = document.querySelector('div.onetrust-pc-dark-filter.ot-fade-in');
    if (element) element.style.display = 'none';
    """
    driver.execute_script(hide_element_script)

    submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[name="login"]')))
    submit_button.click()

    print("Waiting captcha...")

    track_urls = []

    try:
        playlist_info = WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.CSS_SELECTOR, "p.header-page__playlist-tracks")))
        playlist_info = playlist_info.get_attribute("innerHTML")
        print("Logged in!")
    except TimeoutException:
        print("Error getting playlist information, login failed?")
        sys.exit(0)

    time.sleep(5)

    tracks_total = int(re.search(r"\b\d+\b", playlist_info).group())

    draggable_items = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "div.playlist-tracks-list li.draggable-item")))

    for draggable_item in draggable_items:
        grab_track_from_element(draggable_item, track_urls)
        print("Fetching {:^3} / {:^3}".format(len(track_urls), tracks_total), end="\r", flush=True)

    previous_last_urls = []
    repeated_urls_counter = 0
    while len(track_urls) < tracks_total:
        current_last_urls = []
        draggable_items = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "div.playlist-tracks-list li.draggable-item")))[-3:]

        for draggable_item in draggable_items:
            url = grab_track_from_element(draggable_item, track_urls)
            current_last_urls.append(url)
            print("Fetching {:>3} / {:<3}".format(len(track_urls), tracks_total), end="\r", flush=True)

        if current_last_urls == previous_last_urls:
            repeated_urls_counter += 1

        if repeated_urls_counter == 3:
            print(f"\nFound {tracks_total - len(track_urls)} duplicates")
            break

        previous_last_urls = current_last_urls

    driver.close()

    with open("output/tracks.txt", "w") as f:
        f.write("\n".join(track_urls))

    print("\nUrls saved!")

if __name__ == "__main__":
    main()
