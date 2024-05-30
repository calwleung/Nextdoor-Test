from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import csv
from lxml import html
from dotenv import load_dotenv

# Load environment variables from .env.sample file
load_dotenv(dotenv_path='.env.sample')

# Get path to Geckodriver and credentials from .env.sample file
geckodriver_path = os.getenv("geckodriver_path")
email = os.getenv("email")
password = os.getenv("password")

# Set up Firefox options
options = Options()
# Comment out the headless option to see the browser window
# options.headless = True

# Initialize the WebDriver
service = FirefoxService(executable_path=geckodriver_path)
driver = webdriver.Firefox(service=service, options=options)

try:
    driver.get("https://nextdoor.com/login/")

    # Wait for the email and password fields to be present
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "id_email"))
    )
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "id_password"))
    )

    # Log In
    username_field = driver.find_element(By.ID, "id_email")
    password_field = driver.find_element(By.ID, "id_password")

    # Enter credentials
    username_field.send_keys(email)
    password_field.send_keys(password)

    # Click the sign-in button
    driver.find_element(By.XPATH, '//button[@id="signin_button"]').click()
    
    # Wait for some time after login
    time.sleep(10)  # Adjust the sleep time if needed

    # Click the pop-up, if one appears
    try:
        pop_up_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@class='channels-bulk-join-close-button']"))
        )
        pop_up_button.click()
    except Exception as e:
        print(f"No pop-up appeared: {e}")

    # Use Selenium to scroll 'range' number of times to load more posts
    for i in range(1, 10):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

    # Find all comment buttons and click them twice to show comments
    comment_buttons = driver.find_elements(By.XPATH, '//div[@class="post-action-reply-button blocks-r95dx8"]')
    for button in comment_buttons:
        if button.is_displayed():
            try:
                # Click the comment button twice
                time.sleep(1.5)
                driver.execute_script("arguments[0].click();", button)
                time.sleep(1.5)
                driver.execute_script("arguments[0].click();", button)
            except Exception as e:
                print(f"Error clicking comment button: {e}")

    # Click on "See previous comments" to load all comments
    while True:
        try:
            see_previous_buttons = driver.find_elements(By.XPATH, '//div[contains(@class, "see-previous-comments-button-paged")]//div[@role="button"]')
            if not see_previous_buttons:
                break  # No more "See previous comments" buttons
            for button in see_previous_buttons:
                if button.is_displayed():
                    try:
                        time.sleep(1)
                        driver.execute_script("arguments[0].click();", button)
                    except Exception as e:
                        print(f"Error clicking 'see previous comments' button: {e}")
        except Exception as e:
            print(f"Error finding 'see previous comments' buttons: {e}")
            break
    
    # Click "See more" buttons to expand longer comments
    while True:
        try:
            see_more_buttons = driver.find_elements(By.XPATH, '//div[contains(@class, "Styled_display-xs__zpop7k91 Touchable__1e74q6p0 BaseLink__kjvg670 Link_linkRecipeStyles__16mae970 Link_linkRecipeStyles_variant_primary__16mae971 Link_linkRecipeStyles_deprecatedVariant_blue__16mae974 reset__1m5uu6e0") and @role="button"]')
            if not see_more_buttons:
                break  # No more "See more" buttons
            for button in see_more_buttons:
                if button.is_displayed():
                    try:
                        time.sleep(1)
                        driver.execute_script("arguments[0].click();", button)
                    except Exception as e:
                        print(f"Error clicking 'see more' button: {e}")
        except Exception as e:
            print(f"Error finding 'see more' buttons: {e}")
            break

    time.sleep(1)

    ########################################################
    # Scrape the page source returned from Firefox driver for posts
    html_source = driver.page_source
    readable_html = html_source.encode('utf-8')
    tree = html.fromstring(readable_html)

    # Debug: Save the HTML source to a file for inspection
    with open("page_source.html", "wb") as f:
        f.write(readable_html)

    # Check if the posts are found correctly
    postNodes = tree.xpath('//div[contains(@class, "js-media-post")]')

    # Debug: Output the number of posts found
    print(f"Number of posts found: {len(postNodes)}")

    # Extract post and reply data
    posts = []
    for post in postNodes:
        post_id_raw = post.xpath('./ancestor::div[starts-with(@id, "feedItem_")]/@id')[0] if post.xpath('./ancestor::div[starts-with(@id, "feedItem_")]/@id') else 'Unknown'
        post_id = post_id_raw.replace("feedItem_", "") if post_id_raw != 'Unknown' else 'Unknown'
        author = post.xpath('.//a[contains(@class, "_3I7vNNNM E7NPJ3WK")]/text()')
        location = post.xpath('.//a[contains(@class, "post-byline-redesign post-byline-truncated")]/text()')
        title = post.xpath('.//div[@data-testid="post-body"]//div[contains(@class, "blocks-1yg8new")]/span[@data-testid="styled-text"]/text()')
        category = post.xpath('.//a[contains(@class, "post-byline-redesign")]/text()')
        date = post.xpath('.//div[contains(@class, "post-byline-redesign blocks-1wvf4u1")]/text()')
        content = post.xpath('.//span[@class="postTextBodySpan"]//div[@data-testid="styled-text-wrapper"]//span[@data-testid="styled-text"]//span[@class="Linkify"]/text()')
        if not content:
            content = post.xpath('.//span[@class="postTextBodySpan"]//div[@data-testid="styled-text-wrapper"]//span[@data-testid="styled-text"]/text()')
        if not content:
            content = post.xpath('.//span[@class="postTextBodySpan"]//div[@class="blocks-mlmhkr"]//span[@data-testid="styled-text"]/text()')
        if not content:
            content = post.xpath('.//div[@data-testid="post-body"]//div[@data-testid="styled-text-wrapper"]//span[@data-testid="styled-text"]//span[@class="Linkify"]/text()')
        if not content:
            content = post.xpath('.//div[@data-testid="post-body"]//div[@data-testid="styled-text-wrapper"]//span[@data-testid="styled-text"]/text()')
        if not content:
            content = post.xpath('.//div[@data-testid="post-body"]//div[@class="blocks-1yg8new"]//span[@data-testid="styled-text"]/text()')

        num_replies = post.xpath('.//div[contains(@class, "post-comment-count-text")]//span[contains(@class, "blocks-1na46b4")]/text()')
        num_likes = post.xpath('.//span[contains(@class, "_3CRR2ygJ blocks-8kzcgf") and @data-testid="reaction-button-text"]/text()')
        
        # Find the comment container associated with the post
        comment_container = post.xpath('./following-sibling::div[contains(@class, "comment-container")]')
        
        # Check if comment container is found
        if comment_container:
            comment_container = comment_container[0]
        
            # Extract replies within the nested js-media-comment structure inside the comment container
            replies = comment_container.xpath('.//div[contains(@class, "js-media-comment")]')
            reply_data = []
            for reply in replies:
                comment_id = reply.xpath('./@id')[0] if reply.xpath('./@id') else 'Unknown'
                reply_author = reply.xpath('.//a[contains(@class, "BaseLink__kjvg670 Link_linkRecipeStyles__16mae970 Link_linkRecipeStyles_variant_subtle__16mae972")]/text()')
                reply_content = reply.xpath('.//span[@data-testid="styled-text"]/span[@class="Linkify"]/text()')
                if not reply_content:
                    reply_content = reply.xpath('.//span[@data-testid="styled-text"]/text()')
                if not reply_content:
                    reply_content = reply.xpath('.//span[@data-testid="truncate-text"]/text()')
                comment_author_geo = reply.xpath('.//a[contains(@class, "comment-detail-scopeline-neighborhood-name _2CC8ezgv")]/span/text()')
                comment_author_time = reply.xpath('.//span[contains(@class, "comment-detail-scopeline-timestamp")]/text()')
                reply_data.append((comment_id, reply_author, reply_content, comment_author_geo, comment_author_time))
        else:
            reply_data = []

        posts.append((post_id, author, location, title, category, date, content, num_replies, num_likes, reply_data))

    # Debug: Output the number of posts after filtering
    print(f"Number of posts with authors found: {len(posts)}")

    # Create CSV Writer for first document (Posts)
    with open('posts.csv', "w", newline='', encoding='utf-8') as ofile:
        writer = csv.writer(ofile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Create CSV Writer for second document (Replies)
        with open('replies.csv', "w", newline='', encoding='utf-8') as rfile:
            rWriter = csv.writer(rfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

            # Output to csv files
            for post in posts:
                # Posts
                post_id = post[0]
                author = post[1][0] if post[1] else 'Unknown'
                location = post[2][0] if post[2] else 'Unlisted'
                title = post[3][0] if post[3] else 'No Title'
                category = post[4][0] if post[4] else 'No Category'
                date = post[5][0] if post[5] else 'No Date'
                content = post[6][0] if post[6] else 'No Content'
                numReplies = post[7][0] if post[7] else '0'
                numLikes = post[8][0] if post[8] else '0'
                
                writer.writerow([post_id, author, location, title, category, date, content, numReplies, numLikes])

                # Debug: Output the number of replies found
                print(f"Number of replies found for post {post_id}: {len(post[9])}")

                # Replies
                # Iterate through all replies with an author (post[9])
                for count in range(len(post[9])):
                    try:
                        comment_id = post[9][count][0]
                        reply_author = post[9][count][1][0] if post[9][count][1] else 'Unknown'
                        reply_content = post[9][count][2][0] if post[9][count][2] else 'No Content'
                        comment_author_geo = post[9][count][3][0] if post[9][count][3] else 'Unknown'
                        comment_author_time = post[9][count][4][0] if post[9][count][4] else 'Unknown'
                        rWriter.writerow([post_id, comment_id, reply_author, reply_content, comment_author_geo, comment_author_time])
                    except Exception as e:
                        print(f"Could not extract reply: {e}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    if driver:
        driver.quit()
