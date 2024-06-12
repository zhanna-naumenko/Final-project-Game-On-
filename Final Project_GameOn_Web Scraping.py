import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import StaleElementReferenceException
import pandas as pd
import requests

# Ensure the openpyxl library is installed
try:
    import openpyxl
except ImportError:
    import os

    os.system('pip install openpyxl')


# make a function that will close pop-up window
def close_popup(driver):
    try:
        # Add the correct locator for the  pop-up close button
        close_button = driver.find_element(By.XPATH, '/html/body/div[3]/div/a')
        close_button.click()
        time.sleep(2)  # Wait for the pop-up to close
    except Exception as e:
        print("No pop-up or unable to close pop-up.")
        print(e)


# make a function to handle the redirect
def handle_redirect(driver, original_url):
    # Check if the current URL is different from the original URL
    if driver.current_url != original_url:
        # If redirected, print a message and navigate back to the original page
        print("Redirected to another page. Going back...")
        driver.back()  # Go back to the previous page
        time.sleep(2)  # Wait for 2 seconds to allow the page to load (adjust time as needed)
        return True  # Indicate that a redirect occurred
    return False  # Indicate that no redirect occurred


# Initialize lists
platform_list_new = []
developers_list_new = []
name_list_new = []
publishers_list_new = []
release_date_list_new = []
genres_list_new = []
metascores_list_new = []
critic_positive_new = []
critic_neutral_new = []
critic_negative_new = []
user_positive_new = []
user_neutral_new = []
user_negative_new = []
user_score_new = []


# Loop through page numbers from 1 to 118 (inclusive)
for page_num in range(1, 119):

    # Construct the URL for the current page
    url = f'https://www.metacritic.com/browse/game/?releaseYearMin=2019&releaseYearMax=2024&page={page_num}'

    # Send an HTTP GET request to the URL
    response = requests.get(url)
    # Initialize the Chrome WebDriver
    driver = webdriver.Chrome()
    # Navigate to the URL with the WebDriver
    driver.get(url)
    # Wait for 5 seconds to allow the page to fully load
    time.sleep(5)

    # Close pop-up if it appears
    close_popup(driver)

    # Loop through the div on the page
    list_of_div = [1, 3]

    # Loop through the games on the page
    for div_num in list_of_div:
        for game_num in range(1, 13):

            # Locate the parent div element using the specified XPath.
            # The XPath is dynamically generated using div_num and game_num variables.
            parent_div = driver.find_element(By.XPATH,
                                             f'/html/body/div[1]/div/div/div[2]/div[1]/main/section/div[3]/div[{div_num}]/div[{game_num}]/a')

            # Click on the located parent div element.
            parent_div.click()
            # Wait for 5 seconds to allow the new page or action to complete.
            time.sleep(5)

            # Close pop-up if it appears
            close_popup(driver)

            # Get the HTML source code of the current page from the Selenium driver
            page_source = driver.page_source

            # Parse the HTML source code using BeautifulSoup to create a BeautifulSoup object
            soup_games = BeautifulSoup(page_source, 'html.parser')

            # Find all div elements with the class 'c-gameDetails_Platforms u-flexbox u-flexbox-row'
            # These div elements contain the platform information for the games
            platforms = soup_games.find_all('div', class_='c-gameDetails_Platforms u-flexbox u-flexbox-row')

            # Extract and clean the platform names from the found div elements
            platform_list1 = [li.text.strip() for platform in platforms for li in platform.find_all('li') if
                              li.text.strip() != 'iOS (iPhone/iPad)']

            # Extend the existing platform_list_new list with the newly extracted and cleaned platform names
            platform_list_new.extend(platform_list1)

            # Find all div elements with the class 'c-gameDetails_Developer u-flexbox u-flexbox-row'
            # These div elements contain the developer information for the games
            developers = soup_games.find_all('div', class_='c-gameDetails_Developer u-flexbox u-flexbox-row')

            # Extract and clean the developer names from the found div elements
            developers_list = [li.text.strip() for developer in developers for li in developer.find_all('li')]

            # Check if there are multiple developers listed for a game
            if len(developers_list) > 1:
                # Join multiple developer names with a comma and space
                joined_developers = ', '.join(developers_list)

                # Extend the developers_list_new list with the joined developer names,
                # repeated for each platform in platform_list1
                developers_list_new.extend([joined_developers] * len(platform_list1))
            else:
                # If there is only one developer, extend the developers_list_new list
                # with the single developer name, repeated for each platform in platform_list1
                developers_list_new.extend(developers_list * len(platform_list1))

            # Find all div elements with the class 'c-productHero_title g-inner-spacing-bottom-medium g-outer-spacing-top-medium'
            # These div elements contain the name/title of the game
            name = soup_games.find_all('div',
                                       class_='c-productHero_title g-inner-spacing-bottom-medium g-outer-spacing-top-medium')

            # Extract and clean the game names from the found div elements
            # Find the <h1> element within each div and get its text content, removing leading/trailing whitespace
            name_list = [val.find('h1').text.strip() for val in name]

            # Repeat each game name for the number of platforms it is available on
            # This ensures that each platform entry has a corresponding game name
            name_list = [val for val in name_list for _ in range(len(platform_list1))]

            # Append each game name to the name_list_new list
            # This list will be used to store all the game names, properly repeated for each platform
            for val in name_list:
                name_list_new.append(val)

            # Find all div elements with the class 'c-gameDetails_Distributor u-flexbox u-flexbox-row'
            # These div elements contain the publisher information of the game
            publishers = soup_games.find_all('div', class_='c-gameDetails_Distributor u-flexbox u-flexbox-row')

            # Extract and clean the publisher names from the found div elements
            # Find the second <span> element within each div and get its text content, removing leading/trailing whitespace
            publishers_list = [publisher.find_all('span')[1].text.strip() for publisher in publishers]

            # Repeat each publisher name for the number of platforms the game is available on
            # This ensures that each platform entry has a corresponding publisher name
            publishers_list1 = [publisher for publisher in publishers_list for _ in range(len(platform_list1))]

            # Append each publisher name to the publishers_list_new list
            # This list will be used to store all the publisher names, properly repeated for each platform
            for val in publishers_list1:
                publishers_list_new.append(val)

            # Find all div elements with the class 'c-gameDetails_ReleaseDate u-flexbox u-flexbox-row'
            # These div elements contain the release date information of the game
            release_dates = soup_games.find_all('div', class_='c-gameDetails_ReleaseDate u-flexbox u-flexbox-row')

            # Extract and clean the release dates from the found div elements
            # Find the second <span> element within each div and get its text content, removing leading/trailing whitespace
            release_date_list = [release_date.find_all('span')[1].text.strip() for release_date in release_dates]

            # Repeat each release date for the number of platforms the game is available on
            # This ensures that each platform entry has a corresponding release date
            release_date_list = [date for date in release_date_list for _ in range(len(platform_list1))]

            # Append each release date to the release_date_list_new list
            # This list will be used to store all the release dates, properly repeated for each platform
            for val in release_date_list:
                release_date_list_new.append(val)

            # Find all div elements with the class 'c-gameDetails_sectionContainer u-flexbox u-flexbox-row u-flexbox-alignBaseline'
            # These div elements contain the genre information of the game
            genres = soup_games.find_all('div',
                                         class_='c-gameDetails_sectionContainer u-flexbox u-flexbox-row u-flexbox-alignBaseline')

            # Extract and clean the genres from the found div elements
            # Find the last <span> element within each div and get its text content, removing leading/trailing whitespace
            genres_list = [genre.find_all('span')[-1].text.strip() for genre in genres]

            # Repeat each genre for the number of platforms the game is available on
            # This ensures that each platform entry has a corresponding genre
            genres_list = [genre for genre in genres_list for _ in range(len(platform_list1))]

            # Append each genre to the genres_list_new list
            # This list will be used to store all the genres, properly repeated for each platfo
            for val in genres_list:
                genres_list_new.append(val)

            # Find all div elements with the class 'c-siteReviewScore_background g-outer-spacing-right-xsmall c-siteReviewScore_background-critic_medium'
            # These div elements contain the metascore information of the game
            metascores = soup_games.find_all('div',
                                             class_='c-siteReviewScore_background g-outer-spacing-right-xsmall c-siteReviewScore_background-critic_medium')

            # Extract and clean the metascores from the found div elements
            metascores_list = [meta.find('span').text.strip() for meta in metascores]

            # Adjust the length of metascores_list to match the length of platform_list1
            # This ensures that the number of metascores matches the number of platforms the game is available on
            if len(metascores_list) > len(platform_list1):
                # If there are more metascores than platforms, truncate the list to match the platform count
                metascores_list = metascores_list[:len(platform_list1)]

            elif len(metascores_list) < len(platform_list1):
                # If there are fewer metascores than platforms, repeat the last metascore to match the platform count
                metascores_list.extend([metascores_list[-1]] * (len(platform_list1) - len(metascores_list)))

            # Now metascores_list has the same length as platform_list1
            for val in metascores_list:
                metascores_list_new.append(val)

            # Locate the critic div element using the specified XPath.
            critic_div = driver.find_element(By.XPATH,
                                             '/html/body/div[1]/div/div/div[2]/div[1]/div[4]/div/div[2]/div/div[1]/div[1]/a[2]')

            # Click on the located critic div element.
            critic_div.click()

            # Wait for 5 seconds to allow the new page or action to complete.
            time.sleep(5)

            # Close pop-up if it appears
            close_popup(driver)

            # Initialize lists
            critic_positive = []
            critic_neutral = []
            critic_negative = []

            # Loop through each platform name in the platform_list1
            for platform_name in platform_list1:
                try:

                    # Find and select the dropdown element that allows selecting the platform
                    dropdown = Select(driver.find_element(By.XPATH,
                                                          '/html/body/div[1]/div/div/div[2]/div[1]/div[1]/section/div[3]/div/div[1]/select'))
                    dropdown.select_by_visible_text(platform_name)

                    # Wait for the page to load after selecting the platform
                    time.sleep(5)

                    # Get the current URL before any potential redirect
                    original_url = driver.current_url

                    # Check if there's a redirect after selecting the platform
                    if handle_redirect(driver, original_url):
                        # If redirected, append "null" values to the lists and continue to the next iteration
                        critic_positive.append("null")
                        critic_neutral.append("null")
                        critic_negative.append("null")
                        continue

                    # Get the page source and create a BeautifulSoup object
                    page_source = driver.page_source
                    soup = BeautifulSoup(page_source, 'html.parser')

                    try:

                        # Find the div elements containing the critic scores
                        critic_score = soup.find_all('div',
                                                     class_='c-scoreCount_count g-text-semibold g-outer-spacing-left-small')
                        # Extract and clean the critic scores from the found div elements
                        list_critic_score = [meta.find('span').text.strip() for meta in critic_score]
                        # Append the extracted critic scores to the respective lists
                        critic_positive.append(list_critic_score[0])
                        critic_neutral.append(list_critic_score[1])
                        critic_negative.append(list_critic_score[2])

                    except IndexError:
                        # If no critic scores found, append "null" values to the lists
                        critic_positive.append("null")
                        critic_neutral.append("null")
                        critic_negative.append("null")

                except StaleElementReferenceException:
                    #  If there's a StaleElementReferenceException, print a message and navigate back to the previous page
                    print(f"Element not found for {platform_name}. Navigating back...")
                    driver.back()  # Navigate back to the previous page
                    time.sleep(3) # Wait for the page to load after navigating back
                    # Append "null" values to the lists and continue to the next iteration
                    critic_positive.append("null")
                    critic_neutral.append("null")
                    critic_negative.append("null")
                    continue  # Skip to the next iteration

            # Iterate through each value in critic_positive list and append it to critic_positive_new list
            for val in critic_positive:
                critic_positive_new.append(val)

            # Iterate through each value in critic_neutral list and append it to critic_neutral_new list
            for val in critic_neutral:
                critic_neutral_new.append(val)

            # Iterate through each value in critic_negative list and append it to critic_negative_new list
            for val in critic_negative:
                critic_negative_new.append(val)

            # Locate the user div element using the specified XPath
            user_div = driver.find_element(By.XPATH,
                                           '/html/body/div[1]/div/div/div[2]/div[1]/div[1]/section/div[1]/div/div[2]/div/div/div/ul/li[2]/a')

            # Click on the located user div element.
            user_div.click()

            # Wait for 5 seconds to allow the new page or action to complete.
            time.sleep(5)

            # Initialize lists
            user_positive = []
            user_neutral = []
            user_negative = []
            user_score = []

            # Close pop-up if it appears
            close_popup(driver)

            # Loop through each platform name in the platform_list1
            for platform_name in platform_list1:
                try:
                    #  Find and select the dropdown element that allows selecting the platform
                    dropdown = Select(driver.find_element(By.XPATH,
                                                          '/html/body/div[1]/div/div/div[2]/div[1]/div[1]/section/div[3]/div/div[1]/select'))
                    dropdown.select_by_visible_text(platform_name)
                    # Wait for the page to load after selecting the platform
                    time.sleep(5)

                    # Get the current URL before any potential redirect
                    original_url = driver.current_url

                    # Check if there's a redirect after selecting the platform
                    if handle_redirect(driver, original_url):
                        # If redirected, append "null" values to the lists and continue to the next iteration
                        user_positive.append("null")
                        user_neutral.append("null")
                        user_negative.append("null")
                        user_score.append("null")
                        continue

                    # Get the page source and create a BeautifulSoup object
                    page_source = driver.page_source
                    soup = BeautifulSoup(page_source, 'html.parser')

                    try:
                        # Find the div elements containing the user scores
                        user_scores = soup.find_all('div',
                                                    class_='c-scoreCount_count g-text-semibold g-outer-spacing-left-small')
                        # Extract and clean the user scores from the found div elements
                        list_user_scores = [meta.find('span').text.strip() for meta in user_scores]
                        # Append the extracted user scores to the respective lists
                        user_positive.append(list_user_scores[0])
                        user_neutral.append(list_user_scores[1])
                        user_negative.append(list_user_scores[2])

                        # Find all elements with class 'c-ScoreCardLeft_scoreContent_number' in the soup
                        users = soup.find_all('div', class_='c-ScoreCardLeft_scoreContent_number')
                        # Extract the text from each element and store it in a list called list_users
                        list_users = [user.find('span').text.strip() for user in users]
                        # Iterate through each value in list_users and append it to the user_score list
                        for val in list_users:
                            user_score.append(val)

                    except IndexError:
                        # If no user scores found, append "null" values to the lists
                        user_positive.append("null")
                        user_neutral.append("null")
                        user_negative.append("null")
                        user_score.append("null")

                except StaleElementReferenceException:
                    # If there's a StaleElementReferenceException, print a message and navigate back to the previous page
                    print(f"Element not found for {platform_name}. Navigating back...")
                    driver.back()  # Navigate back to the previous page
                    time.sleep(3)  # Wait for the page to load after navigating back
                    # Append "null" values to the lists and continue to the next iteration
                    user_positive.append("null")
                    user_neutral.append("null")
                    user_negative.append("null")
                    user_score.append("null")
                    continue  # Skip to the next iteration

            # Iterate through each value in user_positive list and append it to user_positive_new list
            for val in user_positive:
                user_positive_new.append(val)

            # Iterate through each value in user_neutral list and append it to user_neutral_new list
            for val in user_neutral:
                user_neutral_new.append(val)

            # Iterate through each value in user_negative list and append it to user_negative_new list
            for val in user_negative:
                user_negative_new.append(val)

            # Iterate through each value in user_score list and append it to user_score_new list
            for val in user_score:
                user_score_new.append(val)

            # Navigate to the URL with the WebDriver
            driver.get(url)
            # Wait for 5 seconds to allow the page to fully load
            time.sleep(5)
            # Close pop-up if it appears
            close_popup(driver)
    # Close the WebDriver after interacting with the page
    driver.quit()

# Printing the lists
print(f"Platforms: {platform_list_new}")
print(f"Developers: {developers_list_new}")
print(f"Game Name: {name_list_new}")
print(f"Publishers: {publishers_list_new}")
print(f"Release date: {release_date_list_new}")
print(f"Genres: {genres_list_new}")
print(f"Ratings: {metascores_list_new}")
print(f"Critic score positive: {critic_positive_new}")
print(f"Critic score neutral: {critic_neutral_new}")
print(f"Critic score negative: {critic_negative_new}")
print(f"User score positive: {user_positive_new}")
print(f"User score neutral: {user_neutral_new}")
print(f"User score negative: {user_negative_new}")
print(f"User score: {user_score_new}")

# Printing the length of the lists
print(f"Len Platforms: {len(platform_list_new)}")
print(f"Len Developers: {len(developers_list_new)}")
print(f"Len Game Name: {len(name_list_new)}")
print(f"Len Publishers: {len(publishers_list_new)}")
print(f"Len Release date: {len(release_date_list_new)}")
print(f"Len Genres: {len(genres_list_new)}")
print(f"Len Ratings: {len(metascores_list_new)}")
print(f"Len Critic score positive: {len(critic_positive_new)}")
print(f"Len Critic score neutral: {len(critic_neutral_new)}")
print(f"Len Critic score negative: {len(critic_negative_new)}")
print(f"Len User score positive: {len(user_positive_new)}")
print(f"Len User score neutral: {len(user_neutral_new)}")
print(f"Len User score negative: {len(user_negative_new)}")
print(f"Len User score: {len(user_score_new)}")

# Create a dictionary containing the data for the games
games_data = {
    'name': name_list_new,
    'platform': platform_list_new,
    'developer': developers_list_new,
    'publisher': publishers_list_new,
    'genre(s)': genres_list_new,
    'release_date': release_date_list_new,
    'critic_positive': critic_positive_new,
    'critic_neutral': critic_neutral_new,
    'critic_negative': critic_negative_new,
    'metascore': metascores_list_new,
    'user_positive': user_positive_new,
    'user_neutral': user_neutral_new,
    'user_negative': user_negative_new,
    'user_score': user_score_new
}

# Create a DataFrame from the dictionary
df = pd.DataFrame(games_data)

# Define the file name for the Excel file
file_name = 'games_data_2019-2024.xlsx'

# Write the DataFrame to an Excel file without including the index
df.to_excel(file_name, index=False)
