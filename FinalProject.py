import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns


def dfClean(df):
    # renames latitude and longitude for st.map
    df.rename(columns={"Latitude": "lat", "Longitude": "lon"}, inplace=True)

    # removal of invalid lat/lon rows
    indexLoc = df[(df['lat'] > 44) | (df['lat'] < 30) | (df['lon'] > -115)].index
    df.drop(indexLoc, inplace=True)

    # removal of rows with data outside of California
    indexOutOfState = df[
        (df['Counties'] == "Nevada") | (df['Counties'] == "State of Oregon") | (df['Counties'] == "Mexico") | (
                df['CanonicalUrl'] == '/incidents/2013/8/6/tram-fire/') |
        (df["Location"].str.contains("Nevada") == True)].index
    df.drop(indexOutOfState, inplace=True)

    # removal of possible duplicates
    df.drop_duplicates(inplace=True)
    return df


def IntroText(df):
    st.subheader(f'Welcome to a Streamlit Data Analysis based on the Kaggle dataset'
                 f' "California WildFires (2013-2020)". After cleaning the set of'
                 f' invalid location data, there are {df.shape[0]} entries across {df.shape[1]} rows. Please'
                 f' click the buttons on the left side of the screen to view'
                 f' visuals and text analysis put together to best represent the dataset.')
    st.write("Streamlit created by: Nicholas Ettore")
    st.write("Data collected from https://www.fire.ca.gov/incidents/ by Kaggle user ARES")
    st.image("smokey-bear-forest-fires-gettyimages-50599917.jpg")
    st.write("History Channel/Time Life Pictures/USDA Forest Service/The LIFE Picture Collection/Getty Images")


def MapAndFrame(df):
    st.write("Overview Map with sortable Dataframe. Both filterable by Year and County.")
    col1, col2 = st.columns([1, 4])
    with col1:
        # slider that selects between the lowest and highest Archive Year in the dataset
        hi = max(df['ArchiveYear'])
        lo = min(df['ArchiveYear'])
        values = st.slider('Please select range of years', lo, hi, (lo, hi))

        # checkbox set at default to allow for map/dataframe to use all counties
        check = st.checkbox("Check to view all California counties", True)
        if check is True:
            values2 = df['Counties']

        else:
            # drop down selectbox that lists all the California Counties in the dataset
            counties = df['Counties'].unique()
            counties.sort()
            values2 = st.selectbox('Select a county to view:', counties)

    with col2:
        df2 = df.copy()

        # selects specific columns for dataframe
        df2 = df2.loc[:, ['ArchiveYear', 'Counties', 'Name', 'MajorIncident', 'AcresBurned', 'Location', 'lat', 'lon']]
        df2 = df2.loc[(df['Counties'] == values2)]  # grabs info from counties selectbox

        df2 = df2.loc[df['ArchiveYear'] >= values[0]]  # grabs info from year slider
        df2 = df2.loc[df['ArchiveYear'] <= values[1]]

        # map plugin
        st.map(df2, zoom=4.5)

        df2 = df2.loc[:, ['ArchiveYear', 'Counties', 'Name', 'MajorIncident', 'AcresBurned', 'Location']]
        # makes the column titles more readable
        df2 = df2.rename(columns={'ArchiveYear': 'Year', 'Counties': 'County', 'Name': 'Name of Fire',
                                  'MajorIncident': 'Major Incident', 'AcresBurned': 'Acres Burned',
                                  'Location': 'Location of Fire'})

        st.dataframe(df2, use_container_width=True)


def HumanCost(df):
    # creation of slimmed down dataframe, removes non-fatalities
    df2 = df.loc[:, ['Name', 'ArchiveYear', 'Fatalities', 'Injuries']]
    df2 = df2.loc[(df['Fatalities'] > 0)]
    df2.drop_duplicates(inplace=True)

    st.subheader("The human cost of the California wildfires")

    col1, col2 = st.columns([2, 1])
    # iterrows of fatalities
    with col1:
        for index, row in df2.iterrows():
            if int(row['Fatalities']) == 1:  # singular
                st.write(
                    f"During the {row['Name']} of {row['ArchiveYear']}, {int(row['Fatalities'])} person lost their life.")
            else:  # plural
                st.write(
                    f"During the {row['Name']} of {row['ArchiveYear']}, {int(row['Fatalities'])} people lost their lives.")
    with col2:
        # Big Numbers Injuries, Fatalities, Personal Used
        st.subheader(int(df['Injuries'].sum()))
        st.write("Injured in wildfires between 2013 & 2020")
        st.subheader(int(df2['Fatalities'].sum()))
        st.write("Killed in wildfires between 2013 & 2020")
        st.subheader(int(df['PersonnelInvolved'].sum()))
        st.write("Firefighters needed to fight wildfires")

        # deaths per year scatter plot
        deathSum = df.groupby(by='ArchiveYear').Fatalities.sum()
        deathSum = df.groupby(by='ArchiveYear').Fatalities.sum()
        plt.scatter(deathSum.index, deathSum)
        plt.grid()
        plt.title('Wildfire Deaths per Year')
        st.pyplot(fig=plt)


def FireCost(df):
    st.subheader("The general cost of fires to the State of California")

    # Bar Chart of Number of Fires per Year
    plt.figure(figsize=(8, 2))
    counts = df.ArchiveYear.value_counts().sort_index()
    counts.plot(kind='barh')
    plt.title('California Fires per Year')
    st.pyplot(fig=plt)

    # seaborn box and whisker plot since it is easier to make than matplotlib boxplot
    plt.figure(figsize=(16, 4))
    sns.boxplot(data=df, x='ArchiveYear', y='AcresBurned')
    plt.grid()
    plt.title('Acres Burned per Year')
    st.pyplot(fig=plt)

    # general information about acres burned per year numbers and counties affected
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.subheader("Acres Burned")
        st.write(
            "Year over year the data shows an gradual increase in acres burned, leading up until 2017-2018 when over 5 billion acres of land was subject to forest fires.")
    with col2:
        st.write(df.groupby(by='ArchiveYear').AcresBurned.sum())
    with col3:
        st.subheader("Counties Affected")
        st.write(
            "Overall the data shows that Riverside County is the most affected by forest fires over the course of the dataset timeframe, go back to the overview map to see where Riverside is in California.")
    with col4:
        st.write(df.Counties.value_counts()[0:7])


def runStreamlit():
    df = pd.read_csv("California_Fire_Incidents.csv")
    df = dfClean(df)

    st.set_page_config(layout="wide")
    st.title("CS Python Project: Fire Incidents in California")
    # SideBar Streamlit
    st.sidebar.subheader("Table of Contents")
    sideMenu = st.sidebar.radio("", ("Home Page", "Overview Map", "The Costs of Fire", "The Human Cost"))

    if sideMenu == "Home Page":
        IntroText(df)
    if sideMenu == "Overview Map":
        MapAndFrame(df)
    if sideMenu == "The Human Cost":
        HumanCost(df)
    if sideMenu == "The Costs of Fire":
        FireCost(df)


runStreamlit()
