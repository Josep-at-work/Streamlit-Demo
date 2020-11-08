#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import math
import base64

import json
import streamlit as st
st.set_option('deprecation.showPyplotGlobalUse', False)


def main():
    
    #Download data
    filename = 'https://raw.githubusercontent.com/Josep-at-work/Streamlit-Demo/main/tv_shows.csv'
    data = download_file(filename)
    search_by = st.sidebar.selectbox('What do you want to do?', options=['Go to App description','Search by title', 'Compare Platforms', 'Filter TV Shows'])
    
    #Plots settgins
    fig_size = (20,12)
    title_size = 24
    label_size = 18
    legend_size = 22
    tick_size = 18
    plot_prop = [fig_size, title_size, label_size, legend_size, tick_size]
    
    #SideBar Selection
    if search_by == 'Go to App description':   #Initial Page
        initial_page(data, plot_prop)
    elif search_by == 'Search by title':
        by_title(data,)
    elif search_by == 'Compare Platforms':
        by_gen_char(data, plot_prop)  
    elif search_by == 'Filter TV Shows':
        by_filter(data)        
        

def download_file(filename):
    data = pd.read_csv(filename, index_col=0)
    
    columns_to_drop = ['type', 'Rotten Tomatoes']
    data.drop(columns_to_drop, axis=1, inplace=True)
    
    data.columns = ['Title', 'Year', 'Target Age', 'Rating', 'Netflix', 'Hulu', 'Prime Video', 'Disney+']

    
    platforms = ['Netflix', 'Hulu', 'Prime Video', 'Disney+']
    
    #Add a feature informing all platforms where the specific tv_show is available
    def get_platform(row):
        l = list()
        for platform in platforms:
            if row[platform] == 1:
                l.append(platform)
        return list(l)

    data['Platforms'] = data.apply(get_platform, axis=1)
    
    def obj_to_int(x):
        '''
        Converts a string value into a number.
        x is a string value
        '''
        if isinstance(x, str):
            if x[-1] == '+':
                return int(x.strip('+'))
            elif x=='all':
                return int(0)
        else:
            return int(150)
    data['Age'] = data['Target Age'].apply(obj_to_int) #Necessary for the filter 
    
    data['Target Age'] = data['Target Age'].apply(lambda x: 'Not Defined' if not isinstance(x,str) else x)
    data['Target Age'] = data['Target Age'].apply(lambda x: 'All Ages' if x=='all' else x)
    data['Rating to show'] = data['Rating'].apply(lambda x: 'Not Rated' if math.isnan(x) else round(x,2))   
    return data 


def initial_page(data, plot_prop):
    #Purpouse of the app
    readme_title = '# The most popular TV Shows and Platforms'
    readme_text = 'Here you will find information on the best TV Shows such as, the **rating**, **release year**, **target age**,                 and even the **platform** in which you can find them.                                    This App allows you to **find a TV Show by it\'s title**, you can go with the whole title,                 a  key word or even a piece of the title. Awesome, right?!?!                If you\'re thinking on subscribing to a platform but not sure which to choose,                 with this app you can **compare the most popular platforms**, by its general characteristics                 and even with a deeper analysis if you wish.                Lastly, you can also **filter the TV Shows** in order to find your next TV Show marathon for the weekend!.'
    #Initial Plot
    fig_size, title_size, label_size, legend_size, tick_size = plot_prop
    def rating_evolution(data, grid=False):
            '''
            Visualizes the evolution of the quality(i.e. Ratings) of TV Shows from 1934 to 2020. As it is an scatter plot
                we can also the evolution of the volume of TV Shows released over the past decades
            The grid option can be activated with a checkbox right above the plot.
            '''
            rated = data[data.Rating.notnull()] #I think is better to not plot the evolutions of ratigns over the years with the not ratted movies
            years = rated.Year.unique()
            years.sort()
            num_years = len(years)                        #number of unique years
            year_space = 6                                #controls the density of xticks
            sns.catplot(data=rated, x="Year", y="Rating", alpha=0.5,
                        size=5, height=6, aspect=2.7)    #height and aspect control the size of the figure 
            plt.xticks(range(0,num_years,year_space), years[::year_space])
            plt.title('Evolution of the quality and volume of TV Shows from 1934 to 2020', size=title_size)
            plt.xlabel('Released Year', size=label_size)
            plt.xlim(-2,76)
            plt.ylabel('Rating', size=label_size)
            plt.xticks(fontsize=tick_size)
            plt.yticks(fontsize=tick_size)
            plt.grid(grid)
            return plt.show()
    #App Display
    st.markdown(readme_title)
    st.markdown(readme_text)
    grid1 = st.checkbox('Show grid', key='evolution')
    st.pyplot(rating_evolution(data, grid1))    


def by_title(data):
    
    #Option to find serie by title
    def key_word(user_input):
        '''
        function used to find a serie by a key word from it's title
        user_input is a text variable it can be a single word half a word or even the whole title
        return a json file with all series that contain the piece of text in its title
        '''
        user_input.strip(' ') #In case the user writes some spaces
        data['lowcase_title'] = data['Title'].apply(lambda x: x.lower())
        df_to_display = data[data['lowcase_title'].str.contains(user_input.lower())]
        data.drop('lowcase_title', axis=1, inplace=True)
#         df_to_display.Rating = df_to_display.Rating.round(2)
        df_to_display.rename(columns={'Rating to show': 'IMDb Rating'}, inplace=True)
        result = df_to_display[['Title', 'Year', 'Target Age','Rating', 'IMDb Rating', 'Platforms']].to_json(orient="split")
        df_to_display.set_index('Title', inplace=True)
        parsed = json.loads(result)
        return parsed, df_to_display[['Year', 'Target Age', 'Rating', 'IMDb Rating', 'Platforms']]
    
    #App Display
    st.markdown('### By typing a key word from its title, a table describing the\
        main characteristics of the TV Shows will show up')
    user_input = st.text_input("Type in here", '')
    st.markdown('Sort TV Shows by:')
    p1,p2 = st.beta_columns(2)
    with p1:
        sort_rating = st.checkbox('Rating')
    with p2:
        sort_year = st.checkbox('Realeased Year')
    show_json = st.checkbox('Show the the table in a json file format')
    if user_input != '':
        parsed, df = key_word(user_input)
        if show_json:                       #json file will be sorted by index
            st.json(parsed)
        else:                         
            sorted_data = sort_by(df,sort_rating,sort_year) #you can sort the table
            st.table(sorted_data.drop('Rating', axis=1))

            
def by_gen_char(data, plot_prop):
    
    #Option to visualize the platforms' characteristics 
    #Obtain the general characteristics. 
    #If an additional interesting feature has to be added,
        #first creat the functions and then add a new column to the dictionary(i.e. d)
    def num_series(platform):
        '''Total number of TV Shows of an specific platform'''
        return platform.shape[0]

    def mean_rating(platform):
        return platform.Rating.mean()

    def most_frequent_TA(platform):
        '''Most frequent target age of an specific platform'''
        targets = platform['Target Age'].value_counts().sort_values(ascending=False)
        dictionary = dict(targets)
        TA = list(dictionary.keys())
        if TA[0] == 'Not Defined':
            return TA[1]
        else:
            return TA[0]        
    
    netflix = data[data['Netflix'] == 1]
    prime = data[data['Prime Video'] == 1]
    disney = data[data['Disney+'] == 1]
    hulu = data[data['Hulu'] == 1]

    platforms = [netflix, prime, disney, hulu]
    #Creatio of the table
    d = dict()
    d['Platform'] = ['Netflix', 'Prime Video', 'Disney+', 'Hulu']
    d['Number of Series'] = [num_series(platform) for platform in platforms]
    d['Mean Rating'] = [mean_rating(platform) for platform in platforms]
    d['Most Frequente Target age'] = [most_frequent_TA(platform) for platform in platforms]
    gen_char = pd.DataFrame(d)
    #App Display
    st.markdown('### Main Characteristics of the Platforms')
    st.table(gen_char) #Visualize the data in a table
    
    #Depper Analysis: Violin plot Histogram and Density Functoin aproximation
    fig_size, title_size, label_size, legend_size, tick_size = plot_prop 

    #Violinplot
    def violinplot(data, platform, grid=False, split=False):
        '''
        Creates a violinplot with seaborn
        grid: can be selected from the appweb with a checkbox
        platform: will be the first platform selected
        split: If two platforms are selected, it allows to have both violin distributions in the same plot
        returns a violin plot of the distribution of ratings per target age. 
        '''
        target_order = ['All Ages', '7+', '13+', '16+', '18+', 'Not Defined']
        fig=plt.figure(figsize=fig_size)
        ax=sns.violinplot(data=data, x="Target Age", y="Rating", hue=platform,
                            order=target_order, split=split,
                           inner='box', saturation=20)
        sns.despine(offset=10, trim=True)
        plt.grid(grid)
        plt.title('Distribution of Ratings by Target Age', size=title_size)
        plt.xlabel('Target Age', size=label_size)
        plt.ylabel('Rating', size=label_size)
        plt.legend(prop={'size': legend_size})
        plt.xticks(fontsize=tick_size)
        plt.yticks(fontsize=tick_size)
        return plt.show()
    #Histogram
    def histogram(data, platforms, grid=False):
        '''
        
        '''
        fig = plt.figure(figsize=fig_size)
        plat1 = data[data[platforms[0]]==1]
        plt.hist(x=plat1.Rating, bins=20, rwidth=0.9, align='mid', alpha=0.3, label=platforms[0])
        if len(platforms)==2:
            plat2 = data[data[platforms[1]]==1]
            plt.hist(x=plat2.Rating, bins=20, rwidth=0.9, align='mid', alpha=0.3, label=platforms[1])
        plt.legend(prop={'size': legend_size})
        plt.grid(grid)
        plt.title('TV Shows Count by Rating', size=title_size)
        plt.xlabel('Rating', size=label_size)
        plt.ylabel('Number of TV Shows', size=label_size)
        plt.xticks(fontsize=tick_size)
        plt.yticks(fontsize=tick_size)
        return plt.show()
    #Density Funtion aproximation of the histogram
    def density(data, platforms, grid=False):
        '''
        
        '''
        plt.figure(figsize=fig_size)
        # Iterate through the platforms
        for platform in platforms:
            subset = data[data[platform] == 1]
            # Draw the density plot
            sns.distplot(subset['Rating'], hist = False, kde = True,
                         kde_kws = {'shade':'fill'},
                         label = platform)

        # Plot formatting
        plt.legend(prop={'size': legend_size})
        plt.grid(grid)
        plt.title('Proportional amount of TV Shows by Rating', size=title_size)
        plt.xlabel('Rating', size=label_size)
        plt.ylabel('Density', size=label_size)
        plt.xticks(fontsize=tick_size)
        plt.yticks(fontsize=tick_size)
        plt.show()
    
    #App Display
    st.markdown('### Visual Comparisons')
    st.markdown('Now select **up to two platforms** and choose which **information to visualize** for a deeper analysis.')
    #Divide the screen in two columns one for each platform selection
    p1, p2 = st.beta_columns(2)
    with p1:
        selected_platform1 = st.radio('Select First Platform',
                    options=['---','Netflix', 'Prime Video', 'Hulu', 'Disney+'])
    with p2:
        selected_platform2 = st.radio('Select Second Platform',
                    options=['---','Netflix', 'Prime Video', 'Hulu', 'Disney+'])
        
    p1, p2, p3 = st.beta_columns(3)
    with p1:
        plot1 = st.checkbox('Distribution of Ratings by Target Age', key='plot1')
    with p2:
        plot2 = st.checkbox('Number of TV Shows by Rating', key='plot2')
    with p3:
        plot3 = st.checkbox('Proportion of TV Shows by Rating', key='plot3')
    grid2 = st.checkbox('Show grid', key='violin')
    p1, p2 = st.beta_columns(2)
    #Main block of plots appearence and checkbox option
    if selected_platform1 != '---':                                 #First selection of Platform 1
        with p1:
            st.markdown('Platform1: {}'.format(selected_platform1))
        plat=list()                                                 #histogram
        plat.append(selected_platform1)                              
        d = data[data[selected_platform1]==1]                       #violin plot
        d['Platform'] = selected_platform1
        if selected_platform2 == selected_platform1:
            st.error('Select two diferent platform to compare!')    #error message if both platform are the same
        elif selected_platform2 != '---':                           #Allow now to select a platform 2
            with p2:
                st.markdown('Platform2: {}'.format(selected_platform2))
            plat.append(selected_platform2)                                         #histogram
            d = data[(data[selected_platform1]==1) | (data[selected_platform2]==1)] #violin plot
            d['Platform'] = d[selected_platform1].apply(lambda x: selected_platform1 if x==1 else selected_platform2)
            if plot1:
                st.pyplot(violinplot(d, 'Platform', grid2, True))             #violin plot, split option True
            if plot2:
                st.pyplot(histogram(d,plat, grid2))                                  #histogram
            if plot3:
                st.pyplot(density(d,plat, grid2))                                   #density plot
        else:
            if plot1:
                st.pyplot(violinplot(d, 'Platform', grid2))            #violin plot
            if plot2:
                st.pyplot(histogram(d,plat, grid2))                           #histogram    
            if plot3:
                st.pyplot(density(d,plat, grid2))                             #density plot
    else:
        if selected_platform2 != '---':
            st.error('Select a first platform!')        #error message when a first platform is not selected
    
    st.markdown('Now that you have more information go to the *Filter TV Shows*                 option on the sidebar and filter your next TV Show by platform!')

#Search by Filters    
def by_filter(data):
    
    st.markdown('### Filter the TV Shows by rating, target age, year of release and finally select your platform')
    
    years = data.Year.unique()
    years.sort()
    min_y, max_y = years.min(), years.max()
    rating_filter = st.sidebar.slider('Rating', min_value=0.0, max_value=10.0, value=2.0, step=0.5)
    age_filter = st.sidebar.slider('Minimum Age Recommendation', min_value=0, max_value=18, value=3)
    year_filter = st.sidebar.slider('Released Year', min_value=int(min_y), max_value=int(max_y), value=1980, step=1)
    platform_filter = st.sidebar.selectbox('Platform',options=['All','Netflix', 'Prime Video', 'Hulu', 'Disney+'])
    
    #Checkbox to select whether the not rated movies should be displayed to the user or not
    st.sidebar.markdown('Some TV Shows are **not rated yet** click here to include them in your search')
    include_not_rated = st.sidebar.checkbox('Include not rated series')
    
    #The conditions that a serie must pass in order to be displayed after the slider filters are set
    if include_not_rated:
        condition_rating = (data['Rating'] >= rating_filter) | (data['Rating'].isna()) 
    else:
        condition_rating = data['Rating'] >= rating_filter
    
    condition_age = (data['Age'] <= age_filter) | (data['Age']==0)
    condition_year= (data['Year'] >= year_filter)
    if platform_filter != 'All':
        condition_platform = (data[platform_filter]==1)
        platform_filter = ', you can find them in {}'.format(platform_filter)
        filtered_data = data[(condition_rating) & (condition_age) & (condition_year) & (condition_platform)]

    else: 
        platform_filter = '.'
        filtered_data = data[(condition_rating) & (condition_age) & (condition_year)]

    filtered_data.set_index('Title', inplace=True)
    
    #Checkbox to confirm that the user has setted the filters and whants to see the table of series
#     show = st.sidebar.checkbox('Show the filtered TV Shows')
    
    csv = st.checkbox('Download table in a .csv file', key='csv')
    if csv:
        st.markdown(get_table_download_link(data), unsafe_allow_html=True)
    num_series = filtered_data.shape[0]
    filtered_data.rename(columns={'Rating to show': 'IMDb Rating'}, inplace=True)
    st.success('The are {} TV Shows with a rating of    at least {} and with a target age of +{}{}'.format(num_series, rating_filter, age_filter, platform_filter))
    #Sorting Option, if both options are selected the sort by Rating goes first
    st.markdown('Sort TV Shows by:')
    p1,p2 = st.beta_columns(2)
    with p1:
        sort_rating = st.checkbox('Rating')
    with p2:
        sort_year = st.checkbox('Realeased Year')
    sorted_data = sort_by(filtered_data,sort_rating,sort_year)
        
    st.table(sorted_data[['Platforms','IMDb Rating', 'Target Age', 'Year']])
    

def sort_by(data, sort_rating=False, sort_year=False):
    #Sorting Option, if both options are selected the sort by Rating goes first
    if sort_rating and sort_year:
        sorted_data = data.sort_values(by=['Rating','Year'], ascending=[False,False])
    elif sort_rating:
        sorted_data = data.sort_values(by=['Rating'], ascending=[False])
    elif sort_year:
        sorted_data = data.sort_values(by='Year', ascending=False)
    else:
        sorted_data=data
    return sorted_data


def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=True)
    b64 = base64.b64encode(
        csv.encode()
    ).decode()  # some strings <-> bytes conversions necessary here
    return f'<a href="data:file/csv;base64,{b64}" download="myfilename.csv">Download csv file</a>'


if __name__ == "__main__":
    main()

