
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df['Day'] = pd.to_datetime(df['Day'], errors='coerce')
    df = df.dropna(subset=['Day'])
    return df

def main():
    st.set_page_config(page_title='COVID-19 Vaccination Dashboard', layout='wide')
    st.title('COVID-19 Vaccination Dashboard')

    data_path = "daily-covid-19-vaccine-doses-administered.csv"
    df = load_data(data_path)

    # KPIs
    latest_date = df['Day'].max().date()
    total_doses = int(df['COVID-19 doses (daily)'].sum())
    avg_daily = int(df.groupby('Day')['COVID-19 doses (daily)'].sum().mean())

    col1, col2, col3 = st.columns(3)
    col1.metric('Latest Date in Data', str(latest_date))
    col2.metric('Total Doses Administered', f"{total_doses:,}")
    col3.metric('Avg Daily Doses (overall)', f"{avg_daily:,}")

    # Global time series
    global_daily = df.groupby('Day', as_index=False)['COVID-19 doses (daily)'].sum().sort_values('Day')
    global_daily['7d_avg'] = global_daily['COVID-19 doses (daily)'].rolling(7, min_periods=1).mean()

    st.subheader('Global Daily Doses (with 7-day rolling average)')
    fig = px.line(global_daily, x='Day', y='COVID-19 doses (daily)', labels={'Day':'Date','COVID-19 doses (daily)':'Doses'}, title='Global Daily Doses')
    fig.add_trace(go.Scatter(x=global_daily['Day'], y=global_daily['7d_avg'], mode='lines', name='7-day average'))
    st.plotly_chart(fig, use_container_width=True)

    # Top entities selector
    st.subheader('Top Entities by Total Doses Administered')
    top_entities = df.groupby('Entity', as_index=False)['COVID-19 doses (daily)'].sum().sort_values('COVID-19 doses (daily)', ascending=False)
    top_n = st.slider('Number of top entities to show', min_value=5, max_value=50, value=10)
    top_to_show = top_entities.head(top_n)
    fig2 = px.bar(top_to_show, x='Entity', y='COVID-19 doses (daily)', labels={'Entity':'Entity','COVID-19 doses (daily)':'Total Doses'}, title=f'Top {{top_n}} Entities by Total Doses')
    st.plotly_chart(fig2, use_container_width=True)

    # Entity time series
    st.subheader('Entity-specific Time Series')
    entities = df['Entity'].unique().tolist()
    chosen = st.selectbox('Select an entity (country/region)', options=sorted(entities), index=0)
    ent_df = df[df['Entity'] == chosen].groupby('Day', as_index=False)['COVID-19 doses (daily)'].sum().sort_values('Day')
    ent_df['7d_avg'] = ent_df['COVID-19 doses (daily)'].rolling(7, min_periods=1).mean()
    fig3 = px.line(ent_df, x='Day', y='COVID-19 doses (daily)', labels={'Day':'Date','COVID-19 doses (daily)':'Doses'}, title=f'Daily Doses - {{chosen}}')
    fig3.add_trace(go.Scatter(x=ent_df['Day'], y=ent_df['7d_avg'], mode='lines', name='7-day average'))
    st.plotly_chart(fig3, use_container_width=True)

    # Download processed data
    st.subheader('Download Processed Data')
    csv = global_daily.to_csv(index=False)
    st.download_button('Download global daily CSV', data=csv, file_name='global_daily_vaccinations.csv', mime='text/csv')

    st.markdown('---')
    st.caption('Dashboard generated from uploaded dataset: daily-covid-19-vaccine-doses-administered.csv')

if __name__ == '__main__':
    main()
