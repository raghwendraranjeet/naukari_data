
import yaml
import csv
import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import os


def load_config(config_file_path):
    """
    Load configurations from the YAML file.

    Args:
    config_file_path (str): Path to the YAML configuration file.

    Returns:
    dict: Dictionary containing the configurations.
    """
    with open(config_file_path, 'r') as config_file:
        config = yaml.safe_load(config_file)
    return config

def initialize_driver(url, chromedriver_path):
    """
    Initialize a WebDriver instance and navigate to the given URL.

    Args:
    url (str): The URL to navigate to.
    chromedriver_path (str): Path to the ChromeDriver executable.

    Returns:
    WebDriver: The initialized WebDriver instance.
    """

    driver = webdriver.Chrome()
    driver.get(url)
    return driver

def wait_for_element(driver, xpath):
    """
    Wait for the presence of an element identified by the given XPath.

    Args:
    driver (WebDriver): The WebDriver instance.
    xpath (str): The XPath of the element to wait for.

    Returns:
    WebElement: The WebElement corresponding to the located element.
    """
    return WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, xpath)))

def write_to_csv(csv_writer, data, current_date, current_time, days_ago, time_taken):
    """
    Write the scraped data to a CSV file.

    Args:
    csv_writer (_csv.writer): The CSV writer object.
    data (list): The list of data to write to the CSV file.
    current_date (str): The current date in "YYYY-MM-DD" format.
    current_time (str): The current time in "HH:MM:SS" format.
    days_ago (int): The number of days ago the job was posted.
    time_taken (float): The time taken to scrape the data.
    """
    csv_writer.writerow([*data, current_date, current_time, days_ago, time_taken])

def close_driver(driver):
    """
    Close the WebDriver instance.

    Args:
    driver (WebDriver): The WebDriver instance to close.
    """
    driver.quit()

def scrape_basic_job_details(driver, url, count, output_csv):
    """
    Scrape basic job details such as position, company name, vacancy link, experience needed, salary, location,
    posting time, openings, applicants, education, employment type, and industry type from Naukri.com.

    Args:
    driver (WebDriver): The WebDriver instance.
    url (str): The URL to scrape.
    count (int): The number of job details to scrape.
    output_csv (str): Path to the output CSV file.
    """
    if os.path.exists(output_csv):
        os.remove(output_csv)  # Remove the existing file
        
    with open(output_csv, 'a', encoding="utf-8", newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Position', 'Company_Name', 'Vacancy_Link', 'Experience_Needed', 'Salary', 'Location', 'Posting_Time', 'Openings', 'Applicants', 'Education', 'Employment_Type', 'Industry_Type', 'Current_Date', 'Current_Time', 'Days_Ago', 'Time_Taken'])

        driver.get(url)
        index, new_index, i = '0', 1, 0
        Position_xpath = '//*[@id="listContainer"]/div[2]/div/div[1]/div/div[1]/a'
        link_xpath = '//*[@id="listContainer"]/div[2]/div/div[1]/div/div[1]/a'
        company_name_xpath = '//*[@id="listContainer"]/div[2]/div/div[1]/div/div[2]/span/a[1]'
        experience_xpath = '//*[@id="listContainer"]/div[2]/div/div[1]/div/div[3]/div/span[1]/span/span'
        salary_xpath = '//*[@id="listContainer"]/div[2]/div/div[1]/div/div[3]/div/span[2]/span/span'
        location_xpath = '//*[@id="listContainer"]/div[2]/div/div[1]/div/div[3]/div/span[3]/span'
        posting_time_xpath = '//*[@id="listContainer"]/div[2]/div/div[1]/div/div[6]/span[1]'

        unique_records = set()

        while len(unique_records) < count:
            for j in range(20):
                start_time = time.time()
                temp_index = str(new_index).zfill(2)
                Position_xpath = Position_xpath.replace(index, temp_index)
                link_xpath = link_xpath.replace(index, temp_index)
                company_name_xpath = company_name_xpath.replace(index, temp_index)
                experience_xpath = experience_xpath.replace(index, temp_index)
                salary_xpath = salary_xpath.replace(index, temp_index)
                location_xpath = location_xpath.replace(index, temp_index)
                posting_time_xpath = posting_time_xpath.replace(index, temp_index)
                index = str(new_index).zfill(2)
                
                try:
                    # Extract basic job details
                    Position = wait_for_element(driver, Position_xpath).text
                    Vacancy_Link = wait_for_element(driver, link_xpath).get_attribute('href')
                    Company_Name = wait_for_element(driver, company_name_xpath).text
                    Experience_Needed = wait_for_element(driver, experience_xpath).text
                    Salary = wait_for_element(driver, salary_xpath).text
                    Location = wait_for_element(driver, location_xpath).text
                    Posted_time = wait_for_element(driver, posting_time_xpath).text

                    # Get current date and time
                    current_date_time = datetime.datetime.now()
                    current_date = current_date_time.strftime("%Y-%m-%d")
                    current_time = current_date_time.strftime("%H:%M:%S")

                    if "day" in Posted_time.lower():
                        # Calculate posting date based on days ago
                        days_ago = int(Posted_time.split()[0])
                        posting_date = (current_date_time - datetime.timedelta(days=days_ago)).strftime("%Y-%m-%d")
                    else:
                        days_ago = None
                    
                except:
                    continue
                
                # Define a unique key for each record
                record_key = (Position, Company_Name, Vacancy_Link, Experience_Needed, Salary, Location, Posted_time)

                # Add record to set if it's unique
                if record_key not in unique_records:
                    unique_records.add(record_key)
                    i += 1

                    # Open vacancy link in a new tab
                    driver.execute_script("window.open('');")
                    driver.switch_to.window(driver.window_handles[1])
                    driver.get(Vacancy_Link)

                    try:
                        # Extract additional job details
                        openings = wait_for_element(driver, '//*[@id="job_header"]/div[2]/div[1]/span[2]/span').text
                        applicants = wait_for_element(driver, '//*[@id="job_header"]/div[2]/div[1]/span[3]/span').text
                        Education = wait_for_element(driver, '//*[@id="root"]/div/main/div[1]/div[1]/section[2]/div[1]/div[3]/div[2]/span').text
                        Employment_Type = wait_for_element(driver, '//*[@id="root"]/div/main/div[1]/div[1]/section[2]/div[1]/div[2]/div[4]/span/span').text
                        Industry_Type = wait_for_element(driver, '//*[@id="root"]/div/main/div[1]/div[1]/section[2]/div[1]/div[2]/div[2]/span/a').text

                        end_time = time.time()
                        time_taken = end_time - start_time

                        # Write data to CSV
                        write_to_csv(csv_writer, [Position, Company_Name, Vacancy_Link, Experience_Needed, Salary, Location, Posted_time, openings, applicants, Education, Employment_Type, Industry_Type], current_date, current_time, days_ago, time_taken)
                    
                    except Exception as e:
                        print(f"Error scraping additional data: {e}")

                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                    if len(unique_records) >= count:
                        break
                
                if i >= count:
                    break
            if i >= count:
                break
            wait_for_element(driver, '//*[text() = "Next"]').click()
            new_index = 1

def main():
    # Load configurations from config.yml
    config = load_config("config.yml")

    # Initialize WebDriver
    driver = initialize_driver(config['scraping']['url'], config['selenium']['chromedriver_path'])

    # Scrape basic job details
    scrape_basic_job_details(driver, config['scraping']['url'], int(config['scraping']['job_count']), config['file_paths']['output_csv'])

    # Read the output CSV file using pandas
    Naukri_Bangalore = pd.read_csv(config['file_paths']['output_csv'])

    # Close WebDriver
    close_driver(driver)

if __name__ == "__main__":
    main()
