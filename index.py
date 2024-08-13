import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt

#######################
# Configurações gerais da página
st.set_page_config(
    page_title="Meu dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded")

#######################
# Estilização CSS 
# Crie o seu arquivo .css
with open('style.css', 'r') as fp:
    st.markdown(f"<style>{fp.read()}</style>", unsafe_allow_html=True)

#######################
# Carregamento de dados com Pandas
df = pd.read_csv('city_temperature.csv') 


#######################
# Sidebar (barra lateral)
# inclua elementos de interatividade
# fornecidos pelo Streamlit e/ou
# informações sobre os dados
with st.sidebar:
    st.title('📊 Temperatures Around the World')
    region_list = list(df.Region.unique())[::-1]
    selected_region = st.selectbox('Select a region', region_list)
    df_selected_region = df[df.Region == selected_region]

    country_list = list(df_selected_region.Country.unique())
    selected_country = st.selectbox('Select a country', country_list)

    year_list = list(df.Year.unique())[::-1]
    selected_year = st.selectbox('Select a year',year_list )
    df_selected_year = df[df.Year == selected_year]
    st.sidebar.markdown('Alysson Faria Santos')
    st.sidebar.markdown('PDBD008')


#######################
# Criando Plots
# crie uma função para cada gráfico
# a função deve retornar o objeto do gráfico.
# Use e abuse do Plotly!

def plot1(input_country, input_year):
    filtered_df = df[(df['Country'] == input_country) & (df['Year'] == input_year)]
    monthly_avg_temp = filtered_df.groupby('Month')['AvgTemperature'].mean().reset_index()
    p1 = px.line(monthly_avg_temp, x='Month', y='AvgTemperature', 
                 title=f'Average temperature in {input_country} in {input_year}')
    return p1

def plot2():
    global_avg_temp = df.groupby('Year')['AvgTemperature'].mean().reset_index()
    global_avg_temp = global_avg_temp[:-1]
    p2 = px.line(global_avg_temp, 'Year', 'AvgTemperature')
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
        autosize = False,
        width = 800,
        height = 500
    )
    return fig


#######################
# Apresentando plots no painel 
# principal do dashboard 

# criando colunas e suas larguras
col = st.columns((6, 3.5), gap='medium')

# preencha as colunas incorporando seus
# dados e plots como elementos Streamlit
with col[0]:
    st.markdown(f'#### Temperatures Around the World in {selected_year}')
    choropleth = make_choropleth(selected_year)
    st.plotly_chart(choropleth, use_container_width=True)

    # plot 2
    st.markdown('#### Global Temperatures Over the Years')
    p2 = plot2()
    st.plotly_chart(p2, use_container_width=True)
      


with col[1]:
    st.markdown(f'#### Top 10 Hottest Countries in {selected_year}')

    df_ordered = df_selected_year.groupby('Country')['AvgTemperature'].mean().round(1).reset_index()
    df_ordered = df_ordered.sort_values(by = 'AvgTemperature', ascending = False)[:10]

    st.dataframe(df_ordered,
                 column_order=("Country", "AvgTemperature"),
                 hide_index=True,
                 width=None,
                 column_config={
                    "Country": st.column_config.TextColumn(
                        "Countries",
                    ),
                    "AvgTemperature": st.column_config.ProgressColumn(
                        "Average Temperature (°F)",
                        format="%f",
                        min_value=0,
                        max_value=max(df_selected_year.AvgTemperature),
                     )}
                 )
    
    # plot 1
    p1 = plot1(selected_country, selected_year)
    st.plotly_chart(p1, use_container_width=True)



    

