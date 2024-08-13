import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go

#######################
# Configurações gerais da página
st.set_page_config(
    page_title="Global Temperatures",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

#######################
# Estilização CSS 
with open('style.css', 'r') as fp:
    st.markdown(f"<style>{fp.read()}</style>", unsafe_allow_html=True)

#######################
# Carregamento de dados com Pandas
df = pd.read_csv('city_temperature.csv')

#######################
# Funções para criação dos gráficos
def plot1(input_country, input_year):
    filtered_df = df[(df['Country'] == input_country) & (df['Year'] == input_year)]
    monthly_avg_temp = filtered_df.groupby('Month')['AvgTemperature'].mean().reset_index()
    p1 = px.line(monthly_avg_temp, x='Month', y='AvgTemperature')
    return p1

def plot2():
    global_avg_temp = df.groupby('Year')['AvgTemperature'].mean().reset_index()
    global_avg_temp = global_avg_temp[:-1]  # Remove último ano se incompleto
    p2 = go.Figure()
    p2.add_trace(go.Scatter(
    x=global_avg_temp['Year'], 
    y=global_avg_temp['AvgTemperature'], 
    mode='markers',  # Apenas pontos
    name='Average Temperature',
    marker=dict(color='red', size=8)
    ))
    z = np.polyfit(global_avg_temp['Year'], global_avg_temp['AvgTemperature'], 1)
    p = np.poly1d(z)
    print(p)
    p2.add_trace(go.Scatter(x=global_avg_temp['Year'], y=p(global_avg_temp['Year']), mode='lines', name='Trend Line'))
    p2.update_layout(width= 500, title = 'Global Temperature Over The Years', xaxis_title = 'Year', yaxis_title = 'Avg Temp (°F)')

    return p2

def make_choropleth(input_year):
    filtered_df = df[df['Year'] == input_year]
    avg_temp_by_country = filtered_df.groupby('Country')['AvgTemperature'].mean().reset_index()
    fig = px.choropleth(
        avg_temp_by_country,
        locations='Country',             
        locationmode='country names',    
        color='AvgTemperature',          
        color_continuous_scale='Reds',
        range_color=(avg_temp_by_country['AvgTemperature'].min(), avg_temp_by_country['AvgTemperature'].max()),
        labels={'AvgTemperature': 'Avg Temperature (°F)'}
    )   
    fig.update_layout(
        title= f'Temperatures Around the World in {selected_year}'
    )
    return fig

def calc_average(input_year, input_country):
    filtered_df = df[(df['Country'] == input_country) & (df['Year'] == input_year)]
    average = filtered_df['AvgTemperature'].mean()
    return average

def calc_temp_difference(input_year, input_country):
    filtered_df = df[(df['Country'] == input_country) & (df['Year'] == input_year)]
    average = filtered_df['AvgTemperature'].mean()
    filtered_df_year_before = df[(df['Country'] == input_country) & (df['Year'] == input_year - 1)]
    average_year_before = filtered_df_year_before['AvgTemperature'].mean()
    difference = average - average_year_before
    return difference

def calc_amplitude(input_year, input_country):
    filtered_df = df[(df['Country'] == input_country) & (df['Year'] == input_year)]
    max_temp = filtered_df['AvgTemperature'].max()
    min_temp = filtered_df['AvgTemperature'].min()
    amplitude = (max_temp - min_temp).round(2)
    return amplitude, max_temp, min_temp



#######################
# Menu de navegação
page = st.sidebar.selectbox("Choose a page", ["Temperatures Overview", "Country Analysis"])

if page == "Temperatures Overview":
    # Sidebar para seleção de ano
    st.sidebar.title('🌎 Temperatures Around the World')
    year_list = list(df.Year.unique())[::-1]
    selected_year = st.sidebar.selectbox('Select a year', year_list)
    with st.sidebar:
        st.markdown("Alysson Faria Santos\n\nPDBD008",unsafe_allow_html=True)
    
    # Colunas para exibição dos gráficos
    col = st.columns((9, 4.5), gap='small')

    with col[0]:
        choropleth = make_choropleth(selected_year)
        st.plotly_chart(choropleth, use_container_width=True)

        p2 = plot2()
        st.plotly_chart(p2, use_container_width=False)

    with col[1]:
        st.markdown(f'#### Top 10 Hottest Countries in {selected_year}')
        df_selected_year = df[df.Year == selected_year]
        df_ordered = df_selected_year.groupby('Country')['AvgTemperature'].mean().round(1).reset_index()
        df_ordered = df_ordered.sort_values(by='AvgTemperature', ascending=False)[:10]

        st.dataframe(df_ordered,
                     column_order=("Country", "AvgTemperature"),
                     hide_index=True,
                     width=None,
                     column_config={
                         "Country": st.column_config.TextColumn("Countries"),
                         "AvgTemperature": st.column_config.ProgressColumn(
                             "Average Temperature (°F)",
                             format="%f",
                             min_value=0,
                             max_value=max(df_selected_year.AvgTemperature),
                         )}
                     )
        
        st.markdown("""
        <div style="margin-top: 130px; margin-bottom: 40px">
            \n- Total Variation: +1.7 °F\n\n- Avg ΔTemp/Year: +0.08 °F 
        </div>
        """, unsafe_allow_html=True)
        with st.expander('About', expanded=True):
            st.write('''
                - Data from [Kaggle](https://www.kaggle.com/datasets/sudalairajkumar/daily-temperature-of-major-cities).
                - Data is representative. It does not contain all cities from all countries in the world.''')
        
        
        

elif page == "Country Analysis":
    # Sidebar para seleção de região e país
    st.sidebar.title('📊 Country Temperature Analysis')
    region_list = list(df.Region.unique())[::-1]
    selected_region = st.sidebar.selectbox('Select a region', region_list)
    df_selected_region = df[df.Region == selected_region]

    col2 = st.columns((4,2), gap='large')

    with col2[0]:
        country_list = list(df_selected_region.Country.unique())
        selected_country = st.sidebar.selectbox('Select a country', country_list)

        year_list = list(df.Year.unique())[::-1]
        selected_year = st.sidebar.selectbox('Select a year', year_list)

        st.markdown(f'#### Monthly Temperature in {selected_country} in {selected_year}')
        p1 = plot1(selected_country, selected_year)
        p1.update_layout(
        autosize=False,
        width=1000,
        height=500
    )
        st.plotly_chart(p1, use_container_width=True)

    with col2[1]:
        average = calc_average(selected_year,selected_country)
        difference = calc_temp_difference(selected_year,selected_country)  
        amplitude, max_temp, min_temp = calc_amplitude(selected_year,selected_country)
        st.metric(label = 'Average Year Temperature',value = f'{average.round(1)}°F', delta = f'{difference.round(1)}°F', delta_color='inverse')
        st.metric(label='Max Average Temperature in a day', value=f'{max_temp}°F')
        st.metric(label='Min Average Temperature in a day', value=f'{min_temp}°F')
        st.metric(label = 'Amplitude',value = f'{amplitude}°F')

