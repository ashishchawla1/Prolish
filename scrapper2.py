from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import json
import time
import random

def scrape_linkedin_profile(profile_url, session_cookie):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set headless=False for debugging
        context = browser.new_context()

        # Add LinkedIn session cookie
        context.add_cookies([{
            'name': 'li_at',
            'value': session_cookie,
            'domain': '.linkedin.com',
            'path': '/'
        }])
        
        page = context.new_page()
        retries = 3
        while retries > 0:
            try:
                page.goto(profile_url)
                
                # Wait for a specific element that indicates the page has fully loaded
                page.wait_for_selector('//h1[contains(@class, "text-heading-xlarge")]', timeout=90000)
                
                # Simulate human-like scrolling to load more content
                for _ in range(3):
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(random.uniform(2, 4))  # Random sleep between 2-4 seconds
                    
                break  # Exit the loop if successful
            except PlaywrightTimeoutError:
                print(f"Timeout error on attempt {4 - retries}. Retrying...")
                retries -= 1
                if retries == 0:
                    raise  # Raise the exception after all retries have failed

        profile_data = {}
        profile_data["url"] = profile_url

        def safe_extract(selector, attribute="inner_text", parent=None):
            try:
                elements = (parent or page).query_selector_all(selector)
                if elements:
                    if attribute == "inner_text":
                        return elements[0].inner_text().strip()
                    else:
                        return elements[0].get_attribute(attribute)
                return ""
            except Exception as e:
                print(f"Error extracting {selector}: {e}")
                return ""

        # Extract basic information
        profile_data["name"] = safe_extract("//h1[contains(@class, 'text-heading-xlarge')]")
        profile_data["Cover Page"] = safe_extract('//section[1]//div[1]//div[1]//div//div//img', "src")
        profile_data["Profile Pic"] = safe_extract('//section[1]//div[2]//div[1]//div[1]//div//button//img', "src")
        profile_data["connections"] = safe_extract('//section[1]//div[2]//ul//li//span//span')
        profile_data["headline"] = safe_extract("//div[contains(@class, 'text-body-medium')]")
        profile_data["location"] = safe_extract('//section[1]//div[2]//div[2]//div[2]//span[1]')
        profile_data["Summary"] = safe_extract('//*[@id="about"]/following-sibling::div//span[@aria-hidden="true"]')

        # Extract followers (if available)
        followers_selector = '//div[contains(@class, "pvs-header__container")]//span[contains(@class, "pvs-header__subtitle")]'
        profile_data["followers"] = safe_extract(followers_selector)

        # Extract experiences
        experience_url = f"{profile_url}details/experience/"
        page.goto(experience_url)

        profile_data ["experiences"] = []

        try:
            # Wait for the experience section to be loaded
            page.wait_for_selector('//*[@id="profile-content"]/div/div[2]/div/div/main/section/div[2]/div/div[1]/ul')

            # Get all experience list items
            experience_elements = page.query_selector_all('//*[@id="profile-content"]/div/div[2]/div/div/main/section/div[2]/div/div[1]/ul/li')

            for element in experience_elements:
                experience = {}
                try:
                    # Extract title
                    title_element = element.query_selector(".mr1.t-bold span")
                    experience["title"] = title_element.inner_text().strip() if title_element else ""

                    # Extract company name and link
                    company_element = element.query_selector("a.optional-action-target-wrapper")
                    company_name_element = element.query_selector(".t-14.t-normal span.visually-hidden")
                    experience["company_name"] = company_name_element.inner_text().strip() if company_name_element else ""
                    experience["company_link"] = company_element.get_attribute("href") if company_element else ""

                    # Extract duration
                    duration_element = element.query_selector(".t-14.t-normal.t-black--light span.pvs-entity__caption-wrapper")
                    experience["duration"] = duration_element.inner_text().strip() if duration_element else ""

                    # Extract location
                    location_element = element.query_selector(".t-14.t-normal.t-black--light span.visually-hidden")
                    experience["location"] = location_element.inner_text().strip() if location_element else ""

                    # Extract skills/description
                    skills_element = element.query_selector(".pvs-entity__sub-components span[aria-hidden='true']")
                    experience["skills/description"] = skills_element.inner_text().strip() if skills_element else ""

                    profile_data["experiences"].append(experience)

                except Exception as e:
                    print(f"Error processing experience element: {e}")

        except Exception as e:
            print(f"Error finding experiences: {e}")

        licenses_certifications_url = f"{profile_url}details/certifications/"
        page.goto(licenses_certifications_url)

        profile_data ["licenses_and_certifications"] = []

        try:
            # Wait for the licenses and certifications section to be loaded
            page.wait_for_selector('//*[@id="profile-content"]/div/div[2]/div/div/main/section/div[2]/div/div[1]/ul')

            # Get all licenses and certifications list items
            licenses_certifications_elements = page.query_selector_all('//*[@id="profile-content"]/div/div[2]/div/div/main/section/div[2]/div/div[1]/ul/li')

            for element in licenses_certifications_elements:
                license_certification = {}
                try:
                    # Extract name of the license or certification
                    name_element = element.query_selector(".mr1.t-bold span")
                    license_certification["name"] = name_element.inner_text().strip() if name_element else ""

                    # Extract organization information
                    organization_element = element.query_selector("a.optional-action-target-wrapper")
                    organization_link = organization_element.get_attribute("href") if organization_element else ""
                    organization_name = element.query_selector(".t-14.t-normal span.visually-hidden")
                    license_certification["organization_link"] = organization_link
                    license_certification["organization_name"] = organization_name.inner_text().strip() if organization_name else ""

                    # Extract issue date
                    issue_date_element = element.query_selector(".t-14.t-normal.t-black--light span.pvs-entity__caption-wrapper")
                    license_certification["issue_date"] = issue_date_element.inner_text().strip() if issue_date_element else ""

                    profile_data["licenses_and_certifications"].append(license_certification)

                except Exception as e:
                    print(f"Error processing license/certification element: {e}")

        except Exception as e:
            print(f"Error finding licenses and certifications: {e}")
        education_url = f"{profile_url}details/education/"
        page.goto(education_url)

        profile_data["education"] = []

        try:
            # Wait for the education section to be loaded
            page.wait_for_selector('//*[@id="profile-content"]/div/div[2]/div/div/main/section/div[2]/div/div[1]/ul')

            # Get all education list items
            education_elements = page.query_selector_all('//*[@id="profile-content"]/div/div[2]/div/div/main/section/div[2]/div/div[1]/ul/li')

            for element in education_elements:
                education = {}
                try:
                    # Extract school name
                    school_element = element.query_selector(".mr1.hoverable-link-text.t-bold span")
                    education["school"] = school_element.inner_text().strip() if school_element else ""

                    # Extract degree
                    degree_element = element.query_selector(".t-14.t-normal span[aria-hidden='true']")
                    education["degree"] = degree_element.inner_text().strip() if degree_element else ""

                    # Extract dates attended
                    dates_element = element.query_selector(".t-14.t-normal.t-black--light span.pvs-entity__caption-wrapper")
                    education["dates"] = dates_element.inner_text().strip() if dates_element else ""

                    # Extract grade
                    grade_element = element.query_selector(".t-14.t-normal.t-black span[aria-hidden='true']")
                    education["grade"] = grade_element.inner_text().strip() if grade_element else ""

                    # Extract skills or activities
                    skills_element = element.query_selector('//*[@id="profilePagedListComponent-ACoAAEV128YBUk2Q2pk94NW-HSVHCmM8-RW2A34-EDUCATION-VIEW-DETAILS-profile-ACoAAEV128YBUk2Q2pk94NW-HSVHCmM8-RW2A34-NONE-en-US-0"]/div/div/div[2]/div[2]/ul/li[2]/div/ul')
                    education["skills"] = skills_element.inner_text().strip() if skills_element else ""

                    profile_data["education"].append(education)

                except Exception as e:
                    print(f"Error processing education element: {e}")

        except Exception as e:
            print(f"Error finding education: {e}")

        # Extract skills
        skills_url = f"{profile_url}details/skills/"
        page.goto(skills_url)

        profile_data ["skills"] = []

       
        try:
            # Wait for the skills section to be loaded
            page.wait_for_selector('ul.pvs-list', timeout=10000)

            # Print page content for debugging
            print(page.content())

            # Get all skills list items
            skills_elements = page.query_selector_all('ul.pvs-list li')

            for element in skills_elements:
                try:
                    # Extract skill name
                    skill_element = element.query_selector('.mr1.hoverable-link-text.t-bold span')
                    if skill_element:
                        profile_data["skills"].append(skill_element.inner_text().strip())
                    else:
                        print("Skill element not found")
                except Exception as e:
                    print(f"Error extracting skill: {e}")

        except Exception as e:
            print(f"Error finding skills section: {e}")

        # Extract recommendations
        profile_data["recommendations_received"] = []
        page.goto(f"{profile_url}details/recommendations/?detailScreenTabIndex=0")
        page.wait_for_selector('//main//section//div[2]//div[2]//div//div//ul//li', timeout=90000)
        recommendations_elements = page.query_selector_all('//main//section//div[2]//div[2]//div//div//ul//li')
        for element in recommendations_elements:
            recommendation = {
                "name": safe_extract('.//span[contains(@class, "mr1")]', parent=element),
                "date_and_relationship": safe_extract('.//span[contains(@class, "pvs-entity__caption-wrapper")]', parent=element),
                "content": safe_extract('.//span[@aria-hidden="true"]', parent=element)
            }
            profile_data["recommendations_received"].append(recommendation)

        # Extract posts
        profile_data["posts"] = []
        page.goto(f"{profile_url}recent-activity/all/")
        page.wait_for_selector('//main//div//section//div[2]//div//div//ul//li', timeout=90000)
        
        # Scroll to load more posts
        for _ in range(3):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)
        
        post_elements = page.query_selector_all('//main//div//section//div[2]//div//div//ul//li')
        for post_element in post_elements:
            post_data = {
                "caption": safe_extract(".//div[contains(@class, 'break-words')]", parent=post_element),
                "post_url": safe_extract('.//a[contains(@class, "app-aware-link")]', attribute="href", parent=post_element),
                "time": safe_extract('.//span[contains(@class, "update-components-actor__sub-description")]', parent=post_element),
                "likes": safe_extract('.//span[contains(@class, "social-details-social-counts__reactions")]', parent=post_element),
                "comments": safe_extract('.//span[contains(@class, "social-details-social-counts__comments")]', parent=post_element)
            }
            profile_data["posts"].append(post_data)

        browser.close()

    return profile_data

def save_to_json(profile_data, file_name="linkedin_profile.json"):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(profile_data, f, ensure_ascii=False, indent=4)
    return profile_data
# # Example usage
# session_cookie = "AQEDAUaI1woFjFEHAAABkVtAn18AAAGRf00jX00ALvPq5opddvhs4Tr5xlT9mu1Ag-j6hHgf3eAwpIi4fIdOu-tBW2fhHAAaS6I1kHuy_VM2pciRSfGnnRiAp4xZSHOjp9ePq7cEr1NdZBRdBpyxBnNv"
# profile_name = "parrsam"
# profile_url = f"https://www.linkedin.com/in/{profile_name}/"
# profile_data = scrape_linkedin_profile(profile_url, session_cookie)
# print(profile_data)
# save_to_json(profile_data, f"linkedin_profile_{profile_name}.json")
