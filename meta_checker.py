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

def check_url(url):
    try:
        response = requests.get(url)
        status_code = response.status_code
        status_definition = get_status_definition(status_code)

        title = ""
        meta_description = ""
        meta_keywords = ""

        soup = BeautifulSoup(response.text, 'html.parser')

        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.text.strip()

        meta_description_tag = soup.find('meta', attrs={'name': 'description'})
        if meta_description_tag:
            meta_description = meta_description_tag["content"]

        meta_keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords_tag:
            meta_keywords = meta_keywords_tag["content"]

        return {
            "URL": url,
            "Status": f'{status_code} ({status_definition})',
            "Title": title,
            "Meta Description": meta_description,
            "Meta Keywords": meta_keywords,
        }

    except Exception as e:
        st.write(f'Error occurred while analyzing {url}: {str(e)}')
        return None

# Streamlit UI
st.title("Meta checker")
st.write("Choose an option to analyze URLs:")

option = st.radio("Select an option:", ["Bulk URL Analysis (Excel/CSV)", "Individual URL Analysis"])

if option == "Bulk URL Analysis (Excel/CSV)":
    st.write("Upload an Excel or CSV file containing a list of URLs to analyze their titles, meta descriptions, and meta keywords.")

    # File Upload
    uploaded_file = st.file_uploader("Upload a file", type=["xlsx", "xls", "csv"])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            urls_to_analyze = df["URL"].tolist()

            data = []

            for url in urls_to_analyze:
                url = url.strip()
                if url:
                    url_info = check_url(url)
                    if url_info:
                        data.append(url_info)

            if data:
                st.write("Analysis Results:")
                result_df = pd.DataFrame(data)
                st.table(result_df)

                # CSV Download Button
                csv_data = result_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name="web_scraping_results.csv",
                    key="csv_button"
                )

        except Exception as e:
            st.write(f"Error reading the uploaded file: {str(e)}")

else:
    st.write("Enter multiple URLs separated by commas to analyze their titles, meta descriptions, and meta keywords simultaneously.")

    url_input = st.text_area("Enter URLs separated by commas:")

    if st.button("Analyze URLs"):
        urls_to_analyze = url_input.split(',')
        data = []

        for url in urls_to_analyze:
            url = url.strip()
            if url:
                url_info = check_url(url)
                if url_info:
                    data.append(url_info)

        if data:
            st.write("Analysis Results:")
            result_df = pd.DataFrame(data)
            st.table(result_df)

            # CSV Download Button
            csv_data = result_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name="web_scraping_results.csv",
                key="csv_button"
            )

