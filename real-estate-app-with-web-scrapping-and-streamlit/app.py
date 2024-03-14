import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import base64

from PIL import Image
from functions import *



def load_image(file_path):
    try:
        img = Image.open(file_path)
        return img
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return None



st.title("Lets get🧐 some insights📊 from AqarMap🏠 (عقار ماب) website")


st.divider()


with open("etl.gif", "rb") as file_:
    data_url = base64.b64encode(file_.read()).decode("utf-8")

image_width = 700

st.markdown(
    f'<img src="data:image/gif;base64,{data_url}" alt="ETL" style="width: {image_width}px;">',
    unsafe_allow_html=True,
)


st.divider()


st.title("Data Overview🔍")

n_of_pages = st.number_input("حدد عدد الصفحات التي سيتم استخراج الداتا منها", value=2, min_value=2, max_value=50)

df = etl_pipline(n_of_pages)


drop_null = st.checkbox('Drop Null Values', value=True)

if drop_null:
    df.dropna(inplace=True)

st.sidebar.header("الفلاتر")


selected_rooms = st.sidebar.multiselect("حدد عدد الغرف", sorted(df['الغرف'].unique()), default=sorted(df['الغرف'].unique()))
selected_bathrooms = st.sidebar.multiselect("حدد عدد الحمامات", sorted(df['الحمامات'].unique()))
selected_finish_type = st.sidebar.multiselect("حدد نوع التشطيب", sorted(df['نوع التشطيب'].unique()))

payment_options = df['طريقة الدفع'].astype(str).unique()
selected_payment_method = st.sidebar.multiselect("حدد طريقة الدفع", sorted(payment_options))

selected_property_type = st.sidebar.multiselect("حدد نوع العقار", sorted(df['نوع العقار فى السوق'].unique()))
selected_location = st.sidebar.multiselect("حدد الموقع", sorted(df['الموقع'].unique()))
selected_floor = st.sidebar.multiselect("حدد الدور", sorted(df['الدور'].unique()))

default_area_range = (int(df['المساحات (متر²)'].min()), int(df['المساحات (متر²)'].max()))
area_range = st.sidebar.slider("حدد نطاق المساحة (متر مربع)", min_value=int(df['المساحات (متر²)'].min()), max_value=int(df['المساحات (متر²)'].max()), value=default_area_range)

default_price_range = (df['السعر (جنيه)'].min(), df['السعر (جنيه)'].max())
price_range = st.sidebar.slider("حدد نطاق السعر (جنيه)", min_value=df['السعر (جنيه)'].min(), max_value=df['السعر (جنيه)'].max(), value=default_price_range)

apply_filters = st.sidebar.button("تطبيق الفلاتر")


st.sidebar.divider()

filtered_data = df.copy()

if apply_filters:

    if selected_rooms:
        filtered_data = filtered_data[filtered_data['الغرف'].isin(selected_rooms)]
    if selected_bathrooms:
        filtered_data = filtered_data[filtered_data['الحمامات'].isin(selected_bathrooms)]
    if selected_finish_type:
        filtered_data = filtered_data[filtered_data['نوع التشطيب'].isin(selected_finish_type)]
    if selected_payment_method:
        filtered_data = filtered_data[filtered_data['طريقة الدفع'].astype(str).isin(selected_payment_method)]
    if selected_property_type:
        filtered_data = filtered_data[filtered_data['نوع العقار فى السوق'].isin(selected_property_type)]
    if selected_location:
        filtered_data = filtered_data[filtered_data['الموقع'].isin(selected_location)]
    if selected_floor:
        filtered_data = filtered_data[filtered_data['الدور'].isin(selected_floor)]

    filtered_data = filtered_data[
        (filtered_data['المساحات (متر²)'].between(area_range[0], area_range[1])) &
        (filtered_data['السعر (جنيه)'].between(price_range[0], price_range[1]))
    ]

    st.write(filtered_data)
else:
    st.write(df)


st.divider()


st.title("Data Summary📋")

st.write(df.describe())


st.divider()


st.title("Data Visualization📊")


df = filtered_data

fig = px.histogram(df, x='السعر (جنيه)', title='Distribution of Prices')
st.plotly_chart(fig, theme="streamlit", use_container_width=True)


st.divider()


finish_price = df.groupby('نوع التشطيب')['السعر (جنيه)'].mean().reset_index()

fig = go.Figure(data=[go.Bar(
    x=finish_price['نوع التشطيب'],
    y=finish_price['السعر (جنيه)'],
    marker_color='lightblue'
)])

fig.update_layout(title='Average Price based on Type of Finish',
                  xaxis_title='نوع التشطيب',
                  yaxis_title='متوسط السعر (جنيه)',
                  showlegend=False)

st.plotly_chart(fig, theme="streamlit", use_container_width=True)


st.divider()


payment_method_counts = df['طريقة الدفع'].value_counts()

fig = px.pie(payment_method_counts, values=payment_method_counts.values, names=payment_method_counts.index,
             title='Distribution of Payment Method', hole=0.5)
fig.update_traces(textinfo='percent+label', showlegend=False)
st.plotly_chart(fig, theme="streamlit", use_container_width=True)


st.divider()


room_price = df.groupby('الغرف')['السعر (جنيه)'].mean().reset_index()

fig = px.bar(room_price, x='الغرف', y='السعر (جنيه)', title='Average Price based on Number of Rooms')
st.plotly_chart(fig, theme="streamlit", use_container_width=True)


st.divider()


property_type_counts = df['نوع العقار فى السوق'].value_counts()

fig = px.pie(property_type_counts, values=property_type_counts.values, names=property_type_counts.index,
             title='Distribution of Property Types', hole=0.5)
fig.update_traces(textinfo='percent+label', showlegend=False)
st.plotly_chart(fig, theme="streamlit", use_container_width=True)


st.divider()


view_price = df.groupby('تطل على')['السعر (جنيه)'].mean().reset_index()

fig = px.bar(view_price, x='تطل على', y='السعر (جنيه)', title='Average Price based on View')
st.plotly_chart(fig, theme="streamlit", use_container_width=True)


st.divider()


advertiser_type_counts = df['نوع المعلن'].value_counts()

fig = go.Figure(data=[go.Pie(labels=advertiser_type_counts.index, values=advertiser_type_counts.values)])
fig.update_layout(title='Distribution of Advertisers Types')
st.plotly_chart(fig, theme="streamlit", use_container_width=True)


st.divider()


fig = px.scatter(df, x='المساحات (متر²)', y='السعر (جنيه)', size='الغرف', color='الغرف',
                 hover_name='رقم الإعلان', title='Price vs Area vs Number of Rooms')

st.plotly_chart(fig, theme="streamlit", use_container_width=True)


st.divider()


fig = px.scatter(df, x='المساحات (متر²)', y='السعر (جنيه)', size='السعر (جنيه)', color='نوع التشطيب',
                 hover_name='رقم الإعلان', title='Price vs Area with Type of Finish')

st.plotly_chart(fig, theme="streamlit", use_container_width=True)


st.divider()


st.title("Contact Me 📧")

name = "Abdullah Khaled"
email = "dev.abdullah.khaled@gmail.com"
phone = '+201557504902'

st.write(f"Name: {name}")
st.write(f"Email: {email}")
st.write(f"Phone: {phone}")

