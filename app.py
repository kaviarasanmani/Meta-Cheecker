import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd


def get_status_definition(status_code):
    status_definitions = {



        100: "Continue - The server has received the request headers",
        101: "Switching Protocols - The server is switching protocols",
        200: "OK - The request was successful",
        201: "Created - The request resulted in a new resource being created",
        202: "Accepted - The request has been accepted but not yet processed",
        203: "Non-Authoritative Information - The information is not authoritative",
        204: "No Content - The request was successful, but there is no response body",
        205: "Reset Content - The requester should reset the document view",
        206: "Partial Content - The server is delivering part of the resource",
        300: "Multiple Choices - The requested resource corresponds to multiple options",
        301: "Moved Permanently - The requested resource has been permanently moved",
        302: "Found - The requested resource has been found but temporarily moved",
        303: "See Other - The response is found at a different URI",
        304: "Not Modified - The resource has not been modified since the last request",
        307: "Temporary Redirect - The request should be repeated with another URI",
        308: "Permanent Redirect - The request and all future requests should use another URI",
        400: "Bad Request - The server could not understand the request",
        401: "Unauthorized - Authentication is required for the resource",
        403: "Forbidden - The server refuses to authorize the request",
        404: "Not Found - The requested URL was not found on the server",
        405: "Method Not Allowed - The HTTP method in the request is not allowed",
        408: "Request Timeout - The server timed out waiting for the request",
        410: "Gone - The requested resource is no longer available",
        500: "Internal Server Error - The server encountered an error",
        501: "Not Implemented - The server does not support the functionality",
        502: "Bad Gateway - The server received an invalid response from an upstream server",
        503: "Service Unavailable - The server is temporarily unavailable",
        504: "Gateway Timeout - The server timed out while waiting for a response",


        
    }
    return status_definitions.get(status_code, "Unknown Status")

# Function to scrape metadata from a single URL
def scrape_metadata(url):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Enable headless mode
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        driver.get(url)
        driver.implicitly_wait(1)   
        
        product_code = driver.find_element(By.CLASS_NAME, 'style_item_code__4Jtnh').text[15:-1]
        try:
            response = requests.get(url)
            status_code = response.status_code
            status_definition = get_status_definition(status_code)
            soup = BeautifulSoup(response.text, 'html.parser')

            title = ""
            meta_description = ""
            meta_keywords = ""

            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.text.strip()

            meta_description_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_description_tag:
                meta_description = meta_description_tag["content"]

            meta_keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords_tag:
                meta_keywords = meta_keywords_tag["content"]
        except Exception as e:
            pass

        driver.quit()
    
        return {
            "URL": url,
            "Product Code": product_code,
            "Status": f'{status_code} ({status_definition})',
            "Title": title,
            "Meta Description": meta_description,
            "Meta Keywords": meta_keywords,
            
        }
    except Exception as e:
        return {
            "URL": url,
            "Error": str(e)
        }

# Streamlit UI
st.set_page_config(layout="wide")
st.title("Check with your Meta")
# st.footer()
st.write("Enter individual URLs or upload a CSV or Excel file containing a list of URLs to scrape their metadata.")

# Text input for entering individual URLs
url_input = st.text_area("Enter URLs separated by line breaks:")

# File Upload
uploaded_file = st.file_uploader("Upload a file", type=["xlsx", "xls", "csv"])

if st.button("Metadata Checker"):
    metadata_results = []

    # Scrape metadata from individual URLs
    if url_input:
        urls = url_input.split('\n')
        for url in urls:
            url = url.strip()
            if url:
                metadata = scrape_metadata(url)
                metadata_results.append(metadata)

    # Scrape metadata from URLs in the uploaded file
    if uploaded_file is not None:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        urls_to_analyze = df["URL"].tolist()

        for url in urls_to_analyze:
            url = url.strip()
            if url:
                metadata = scrape_metadata(url)
                metadata_results.append(metadata)

    st.write("Get Metadata:")
    result_df = pd.DataFrame(metadata_results)
    st.table(result_df)

    # CSV Download Button
    csv_data = result_df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name="scraped_metadata.csv",
        key="csv_button"
    )
# cd

#         if login_button:
#             redirect_uri = oauth.google.authorize_redirect()
#             return redirect_uri

#     else:
#         st.write(f"Logged in as {st.session_state.user['name']}")
#         logout_button = st.button("Logout")
#         if logout_button:
#             st.session_state.clear()
    
#     st.write("Other app content goes here.")

# if __name__ == "__main__":
#     main()
