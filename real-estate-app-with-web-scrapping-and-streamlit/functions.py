import requests
import pandas as pd
import streamlit as st

from bs4 import BeautifulSoup



def extract(listing_url):
    response = requests.get(listing_url)

    soup = BeautifulSoup(response.content, 'html.parser')

    title = soup.find('h1', class_='listing-details-page__title-section__title').text.strip()
    price = soup.find('span', class_='integer').text.strip()
    currency = soup.find('span', class_='mx-2').text.strip()
    address = soup.find('p', class_='listing-details-page__title-section__address').text.strip().replace('\n', '')


    details_dict = {}
    list_group = soup.find('ul', class_='list-group')
    if list_group:
        items = list_group.find_all('li', class_='list-group-item')
        for item in items:
            label = item.find('span', class_='col-md-3').text.strip()
            value = item.find('span', class_='col-md-9').text.strip()
            details_dict[label] = value


    description_element = soup.find('div', class_='listing-text')
    description = description_element.text.strip() if description_element else "N/A"
    details_dict['Description'] = description

    details_dict['Title'] = title
    details_dict['Price'] = f"{price} {currency}"
    details_dict['Address'] = address

    return details_dict




def transform_and_load(df):

    rename_cols = {
    'المساحات': 'المساحات (متر²)',
    'سعر المتر': 'سعر المتر (جنيه/متر²)',
    'Description': 'الوصف',
    'Title': 'العنوان',
    'Price': 'السعر (جنيه)',
    'Address': 'الموقع'
    }

    df.rename(columns=rename_cols, inplace=True)

    df = df.replace('\n', ' ')

    df['المساحات (متر²)'] = df['المساحات (متر²)'].str.replace('متر²', '').str.strip().astype(int)
    df['سعر المتر (جنيه/متر²)'] = df['سعر المتر (جنيه/متر²)'].str.replace(',', '').str.replace('جنيه/متر²', '').str.strip().astype(float)
    df['السعر (جنيه)'] = df['السعر (جنيه)'].str.replace('جنيه', '').str.replace(',', '').str.strip().astype(float)
    df['سنة البناء / التسليم'] = df['سنة البناء / التسليم'].str.replace('\\4', '').astype('category')
    df['الحمامات'] = df['الحمامات'].astype('Int8')
    df['الغرف'] = df['الغرف'].astype('Int8')


    categorical_columns = ['نوع التشطيب', 'تطل على', 'طريقة الدفع', 'نوع المعلن', 'نوع العقار فى السوق']
    df[categorical_columns] = df[categorical_columns].astype('category')

    str_columns = ['نوع التشطيب', 'رقم الإعلان', 'الموقع', 'الوصف', 'العنوان']
    df[str_columns] = df[str_columns].astype('str')

    return df



@st.cache_data
def etl_pipline(n_of_pages):

    listing_urls = []
    all_listing_details = []

    for page_number in range(1, n_of_pages + 1):
        url = f'https://aqarmap.com.eg/ar/for-sale/property-type/?default=1&page={page_number}'
        
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        listing_links = soup.find_all('a', class_='search-listing-card__container__link')
        for link in listing_links:
            href = link.get('href')
            if href:
                listing_urls.append(f"https://aqarmap.com.eg{href}")


    for url in listing_urls:
        listing_details = extract(url)
        all_listing_details.append(listing_details)



    extract_data = pd.DataFrame(all_listing_details)
    trans_load_data = transform_and_load(extract_data)

    return trans_load_data

