from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import pandas as pd

def main():

    columns = [
        'semester', 'year', 'course_code', 'course_name', 'instructor', 'enrollment', 'responses',
        'Q1_1', 'Q1_2', 'Q1_3', 'Q1_4', 'Q1_5', 'N/A_Q1',
        'Q2_1', 'Q2_2', 'Q2_3', 'Q2_4', 'Q2_5', 'N/A_Q2',
        'Q3_1', 'Q3_2', 'Q3_3', 'Q3_4', 'Q3_5', 'N/A_Q3',
        'Q4_1', 'Q4_2', 'Q4_3', 'Q4_4', 'Q4_5', 'N/A_Q4',
        'Q5_1', 'Q5_2', 'Q5_3', 'Q5_4', 'Q5_5', 'N/A_Q5',
        'Q6_1', 'Q6_2', 'Q6_3', 'Q6_4', 'Q6_5', 'N/A_Q6',
        'Q7_1', 'Q7_2', 'Q7_3', 'Q7_4', 'Q7_5', 'N/A_Q7',
        'Q8_1', 'Q8_2', 'Q8_3', 'Q8_4', 'Q8_5', 'N/A_Q8',
        'Q9_1', 'Q9_2', 'Q9_3', 'Q9_4', 'Q9_5', 'N/A_Q9',
        'Q10_1', 'Q10_2', 'Q10_3', 'Q10_4', 'Q10_5', 'N/A_Q10',
        'section_mean_Q1', 'section_mean_Q2', 'section_mean_Q3', 'section_mean_Q4', 'section_mean_Q5', 'section_mean_Q6', 'section_mean_Q7', 'section_mean_Q8', 'section_mean_Q9', 'section_mean_Q10'        
    ]
    sirs_data = pd.DataFrame(columns= columns)
    driver = webdriver.Chrome()
    driver.get('https://sirs.rutgers.edu/index.php')

    print("Please log in manually within 60 seconds...")
    time.sleep(45)

    # After login, navigate to the specified URL within the same session
    semesters = ['Fall', 'Spring']
    years = [str(year) for year in range(2014, 2025) if year != 2020]
    dept_codes = ['125', '155', '180', '332', '440', '540', '635', '650']

    all_sites = []
    for semester in semesters:
        for year in years:
            for code in dept_codes:
                all_sites.append([semester, year, code])
    for site in all_sites:
        sem = site[0]
        year = site[1]
        dept = site[2]
        print(sem, year, dept)
        url = f'https://sirs.rutgers.edu/index.php?survey%5Bsemester%5D={sem}&survey%5Byear%5D={year}&survey%5Bschool%5D=14&survey%5Bdept%5D={dept}&survey%5Bcourse%5D=&mode=course'

        driver.get(url)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        data_to_add = obtain_data(soup)
        new_data = pd.DataFrame(data_to_add, columns=sirs_data.columns)
        sirs_data = pd.concat([sirs_data, new_data], ignore_index=True)
    
    sirs_data.to_csv('sirs_data.csv', index=False)
    driver.quit()

def obtain_data(soup):
    tables = soup.find_all("table", class_='table-container table-bordered')
    data = []
    for table in tables:
        if table.find("span", class_='mono one text') is None:
                continue  # Skip this iteration if no results are found
        data_to_append = []
        course_d = table.find("div", class_="courseInfo")
        br_tags= course_d.find_all("br")
        professor = course_d.find("strong").text.strip()
        course_name_tag = course_d.find("q")
        course_name = course_name_tag.text.strip() if course_name_tag else "N/A"

        info = []
        for tag in br_tags:
            next_item = tag.next_sibling
            if next_item and isinstance(next_item, str):
                info.append(next_item.strip())

        unwanted_phrases = ["Multiple Sections", "Crosslisted with"]
        info = [item for item in info if not any(phrase in item for phrase in unwanted_phrases)]

        semester = info[0].split()[0]
        year = info[0].split()[1]
        course_code = info[1].split()[0]
        enrollment = ''.join(filter(str.isdigit, info[2].split()[1]))
        num_responses = ''.join(filter(str.isdigit, info[2].split()[3]))

        data_to_append.extend([semester, year, course_code, course_name, professor, enrollment, num_responses])

        all_chart_data = table.find_all("td", class_="chart")
        first_10_charts = all_chart_data[:10]

        responses = []
        for chart in first_10_charts:
            numbers = [int(span.get_text()) for span in chart.find_all("span", class_=lambda x: x and "mono" in x)]
            responses.append(numbers)

        flat_responses = [num for sublist in responses for num in sublist]

        section_means = [mean.text.strip() for mean in table.find_all("td", class_='mono stats mQuestion section')][:10]
    
        data_to_append.extend(flat_responses)
        data_to_append.extend(section_means)
        data.append(data_to_append)


    return data


if __name__ == "__main__":
    main()
