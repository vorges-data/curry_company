# Libraries
import pandas as pd
import re
import plotly.express as px
import folium
from haversine import haversine
import plotly.graph_objects as go
from PIL import Image
import streamlit as st
from streamlit_folium import folium_static
import numpy as np


# CSS Style
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

#st.set_page_config( page_title='Visão Restaurantes', page_icon='🍽', layout='wide')

#========================================================================
#========================== Funções =====================================
#========================================================================

def avg_std_time_on_traffic( df5 ):   
    cols = ['Time_taken(min)','City','Road_traffic_density']
    df_aux02 = df5.loc[:, cols].groupby( ['City','Road_traffic_density'] ).agg({'Time_taken(min)': ['mean','std']} )
    df_aux02.columns = ['avg_time', 'std_time']
    df_aux02 = df_aux02.reset_index()
    fig = px.sunburst( df_aux02, path=['City','Road_traffic_density'], values='avg_time',
          color='std_time', color_continuous_scale='RdBu',
          color_continuous_midpoint=np.average(df_aux02['std_time'] ) )
    
    return fig
            
            
def avg_std_time_graph( df5 ):
    cols = ['Time_taken(min)','City']
    agg_time = df5.loc[:, cols].groupby( 'City' ).agg({'Time_taken(min)': ['mean','std']})
    
    agg_time.columns = ['avg_time', 'std_time']
    
    agg_time = agg_time.reset_index()
    
    fig = go.Figure()
    fig.add_trace( go.Bar( name='Control',
                           x=agg_time['City'],
                           y=agg_time['avg_time'],
                           error_y=dict( type='data', array=agg_time['std_time'] ) ) )
    
    fig.update_layout(barmode='group')
    
    return fig



def avg_std_time_delivery(df5, festival, op):
    """
        Esta função calcula o tempo médio e desvio padrão do tempo de entrega.
        Parâmetros:
            Input:
                - df: Dataframe com os dados necessários para o cálculo
                - op: Tipo de operação que precisa ser calculado
                    'avg_time': Calcula o tempo médio
                    'std_time': Calcula o desvio padrão do tempo.
            
            Output:
                - df: Dataframe com 2 colunas e 1 linha
    
    """
    cols = ['Time_taken(min)','Festival']
    df_aux03 = df5.loc[:, cols].groupby( 'Festival' ).agg({'Time_taken(min)': ['mean','std']})
    
    df_aux03.columns = ['avg_time', 'std_time']
    df_aux03 = df_aux03.reset_index()
    
    
    linhas_selecionadas = df_aux03['Festival'] == festival
    df_aux03 = np.round( df_aux03.loc[linhas_selecionadas, op], 2)
    
    return df_aux03



def distance( df5, fig ):
    if fig == False:
        col = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
        df5['distance'] = ( df5.loc[:, col].apply( lambda x: 
                        haversine(
                              (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                              (x['Delivery_location_latitude'], x['Delivery_location_longitude'])
                          ),axis=1 ) )
        avg_distance = np.round(df5['distance'].mean(), 2)
        return avg_distance
    
    else:
        col = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
        df5['distance'] = ( df5.loc[:, col].apply( lambda x: 
                        haversine(
                              (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                              (x['Delivery_location_latitude'], x['Delivery_location_longitude'])
                          ),axis=1 ) )

        avg_distance = df5.loc[:, ['City', 'distance']].groupby( 'City' ).mean().reset_index()
        fig = go.Figure( data=[ go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])
        
        return fig
    
            

def clean_code ( df1 ):
    """ Esta função tem a responsabilidade de limpar o dataframe
        
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de data
        5. Limpeza da coluna de tempo ( remoção do texto da variável numérica )
        
        Input: DataFrame
        Output: Dataframe
        
    """
    # excluindo NaN
    linhas_selecionadas = ( df1['Delivery_person_Age'] != 'NaN ') 
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    # excluindo NaN
    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ') 
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    # excluindo NaN
    linhas_selecionadas = (df1['City'] != 'NaN ') 
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    # excluindo NaN
    linhas_selecionadas = (df1['Festival'] != 'NaN ') 
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    
    # 1. convertendo a coluna age de objeto para numero
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    
    # 2. convertendo a coluna Ratings de texto para numero decimal (float)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    
    # 3. convertendo a coluna order_date de texto para data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')
    
    # 4. convertendo multiple_deliveries de texto para numero inteiro (int)
    linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)
    
    # 5. Removendo os espacos dentro de string/object/texto
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    
    # Limpar para retirar (min) e converter em número
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1] )
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )
    
    return df1

# import dataset
df1 = pd.read_csv('dataset/train.csv')

# Cleaning Code
df2 = clean_code( df1 )

#===========================
# Cópias dos DataFrames
#===========================
#df1 = df.copy()
df3 = df2.copy()
df4 = df3.copy()
df5 = df4.copy()

#========================================================================
#========================== Menu Lateral ================================
#========================================================================
st.header('Marketplace - Visão Restaurantes')

#===========================
# Criar o menu lateral
#===========================

# Importar uma imagem
#image_path = '/home/vinicius/repos/ftc_programacao_python/Logo Preto Sem Fundo.png'
image = Image.open( 'Logo Preto Sem Fundo.png' )
st.sidebar.image(image, width=160)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## A mais rápida entrega da cidade')
st.sidebar.markdown("""---""") #Colocar um divider

# filtro
st.sidebar.markdown('## Selecione uma data limite' )

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value = pd.datetime(2022, 4, 13),
    min_value = pd.datetime(2022, 2, 11),
    max_value = pd.datetime(2022, 4, 6),
    format='DD-MM-YYYY')

st.sidebar.markdown("""---""") #Colocar um divider

# filtro 2
traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito:',
    ['Low', 'Medium', 'High', 'Jam'],
    default = ['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""---""") #Colocar um divider

weather_options = st.sidebar.multiselect(
       'Quais as condições climáticas:',
        ['conditions Cloudy','conditions Fog','conditions Sandstorms','conditions Stormy','conditions Sunny','conditions Windy'],
        default = ['conditions Cloudy','conditions Fog','conditions Sandstorms','conditions Stormy','conditions Sunny','conditions Windy']
)

st.sidebar.markdown("""---""") #Colocar um divider

st.sidebar.markdown('### Powered by Vorges Data')


#===========================
# Filtros interativos
#===========================

# Filtro de Data
linhas_selecionadas = df4['Order_Date'] < date_slider
df5 = df5.loc[linhas_selecionadas, :]

#Filtro de trânsito
linhas_selecionadas = df4['Road_traffic_density'].isin( traffic_options )
df5 = df5.loc[linhas_selecionadas, :]

#Filtro de condições climáticas
linhas_selecionadas = df5['Weatherconditions'].isin( weather_options )
df5 = df5.loc[linhas_selecionadas, :]


#========================================================================
#========================== Layout no Streamlit =========================
#========================================================================
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '', ''])

#===========================
# TAB I
#===========================
with tab1:
    
    #============================
    #Container 1
    #============================
    with st.container():
        st.title('Métricas')
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            delivery_unique = len(df5.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Entregadores únicos', delivery_unique)
            
        with col2:
            avg_distance = distance( df5, fig=False )
            col2.metric('A distância média das entregas', avg_distance)
            
    
        with col3:
            df_aux03 = avg_std_time_delivery(df5, 'Yes', 'avg_time')
            st.metric('Tempo médio de entrega c/ Festival', df_aux03 )      
    
                        
        with col4:
            df_aux03 = avg_std_time_delivery(df5, 'Yes', 'std_time')
            st.metric('Desvio Padrão médio de entrega c/ Festival', df_aux03 )
                       
            
            
        with col5:
            df_aux03 = avg_std_time_delivery(df5, 'No', 'avg_time')
            st.metric('Tempo médio de entrega c/ Festival', df_aux03 )
            
    
            
        with col6:
            df_aux03 = avg_std_time_delivery(df5, 'No', 'std_time')
            st.metric('Desvio Padrão médio de entrega c/ Festival', df_aux03 )
                                 
        
    #============================
    #Container 2
    #============================
    with st.container():
        st.markdown("""---""")
        st.title('Tempo médio de entrega por cidade')
        
        fig = distance( df5, fig=True )
        st.plotly_chart(fig)

    
    #============================
    #Container 3
    #============================
    with st.container():
        st.markdown("""---""")
        st.title('Distribuição do Tempo')
        
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = avg_std_time_graph( df5 )
            st.plotly_chart( fig )

            
        with col2:    
            fig = avg_std_time_on_traffic( df5 )
            st.plotly_chart( fig )
            
    #============================
    #Container 4
    #============================
    with st.container():
        
        st.markdown("""---""")
        st.title('Distribuição da Distância')
        cols = ['Time_taken(min)','City','Road_traffic_density']
        df_aux02 = df5.loc[:, cols].groupby( ['City','Road_traffic_density'] ).agg({'Time_taken(min)': ['mean','std']})
        
        df_aux02.columns = ['avg_time', 'std_time']
        
        df_aux02 = df_aux02.reset_index()
        
        st.dataframe(df_aux02)
    