# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 12:56:32 2021

@author: Francisco Vazquez

Located in this file is the web-scraping function and JUCO player-check function.
The scraper is called by main.py, and it scrapes thebaseballcube.com for the years 
provided and only pulls data for Valparaiso University and the teams it was in 
conference with for the given years. Currently, there is only information on 
Valpo's conference going back to 2008 in this file. 

The scraper will go year by year, and after it pulls hitting and pitching data 
for a team for a given year, it will check that roster for any JUCO players. 
"""

import time
import requests
import re
import os
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

checked_JUCO_players = {}

def scrapeYearlyStats(yearStart,yearEnd=2021):
    ''' 
        Parameters
        ----------
        yearStart : INT
            What year to start scraping statistics.
        yearEnd : INT
            DEFAULT = 2021. What year to stop scraping statistics.
    
        Returns
        -------
        None.
    
        From yearStart to yearEnd, scrape thebaseballcube.com for yearly team 
        data for each team Valpo was in conference with. 
    '''    
    team_codes = {"Valpo":20503,
                  "Bradley": 20242,
                  "Evansville":20176,
                  "Illinois State":20129,
                  "Indiana State":20256,
                  "Missouri State":20219,
                  "Southern Illinois": 20005,
                  "Dallas Baptist":20117,
                  "Butler":20705,
                  "Cleveland State":20741,
                  "Illinois-Chicago":20891,
                  "Wisconsin-Milwaukee":20911,
                  "Wright State":20030,
                  "Youngstown State":20488,
                  "Oakland":21632,
                  "Northern Kentucky":20860}
    
    # set up adblocker
    chop = webdriver.ChromeOptions()
    chop.add_extension('/Users/Public/anaconda3/bin/ADBLOCK4.40.0-Crx4Chrome.com.crx')
    # set the web driver
    driver = webdriver.Chrome('/Users/Public/anaconda3/bin/chromedriver.exe',chrome_options=chop)
    
    for year in range(yearStart,yearEnd+1):
        schools=["Valpo"]
        if year<=2017:
            schools.extend(["Illinois-Chicago","Wisconsin-Milwaukee",
                            "Wright State","Youngstown State"])
            if year<=2011:
                schools.extend(["Cleveland State"])
            if year<=2012:
                schools.extend(["Butler"])
            if year>=2014:
                schools.extend(["Oakland"])
            if year>=2016:
                schools.extend(["Northern Kentucky"])
        else:
            schools.extend(["Bradley","Evansville","Illinois State",
                            "Indiana State","Missouri State","Southern Illinois",
                            "Dallas Baptist"])
        for team_name in schools:
            
            # Navigate to the baseballcube website
            team_url = "http://www.thebaseballcube.com/college/schools/stats.asp?Y="+str(year)+"&T="+str(team_codes[team_name])
    
            driver.get(team_url)
            # Locate the csv button by it's ID
            csv_button = driver.find_element_by_id("csv_text_grid1")
            # Click the csv button to convert the table
            csv_button.click()
            # Locate the csv button for the pitching statistics
            csv_button_pitch = driver.find_element_by_id("csv_text_grid2")
            # Click the csv button to convert the table
            csv_button_pitch.click()
            # Wait for html to update
            time.sleep(6)
        
            # Get the page source so we can utilize the fact that we converted the table to a csv
            team_pagesource = driver.page_source
        
            # Parse the table, now in csv format
        
            soup = BeautifulSoup(team_pagesource, 'html5lib')
            
        
            # find the hitting table by it's "grid1" id 
            hitting_table_html = soup.find('table',attrs={'id':'grid1'})
        
            # find all of the rows of this table
            hitting_table = hitting_table_html.find_all('tr')
            # create an empty string that will house all of the data from the table
            hitting_data = ""
            # for each row in the table:
            for row in hitting_table:
                # find all data in that row & get rid of the <td> tags
                row_data = str(row.find_all('td')).replace('<td>','')
                # get rid of the close tags
                row_data = row_data.replace('</td>','')
                # get rid of the open and close brackets
                row_data = row_data.replace('[','')
                row_data = row_data.replace(']','\n') # also put a new line at the end 
            
                # append the row to the entire data set
                hitting_data = hitting_data + row_data
        
            # find the pitching table by it's "grid2" id 
            pitching_table_html = soup.find('table',attrs={'id':'grid2'})
        
            # find all of the rows of this table
            pitching_table = pitching_table_html.find_all('tr')
            # create an empty string that will house all of the data from the table
            pitching_data = ""
            # for each row in the table:
            for row in pitching_table:
                # find all data in that row & get rid of the <td> tags
                row_data = str(row.find_all('td')).replace('<td>','')
                # get rid of the close tags
                row_data = row_data.replace('</td>','')
                # get rid of the open and close brackets
                row_data = row_data.replace('[','')
                row_data = row_data.replace(']','\n') # also put a new line at the end 
                # print(row_data)
                # append the row to the entire data set
                pitching_data = pitching_data + row_data
            hit_file_path = '../CapstoneBaseballData/Hitting/'+str(team_name).replace(" ","_")+'_'+str(year)+'_Hitting.csv'
            pitch_file_path = '../CapstoneBaseballData/Pitching/'+str(team_name).replace(" ","_")+'_'+str(year)+'_Pitching.csv'
            if not os.path.exists(hit_file_path):
                # Create a file to write the parsed data to 
                hit_save_file = open(hit_file_path,'w')
                # write to that newly created file
                hit_save_file.write(hitting_data)
                #close that file
                hit_save_file.close()
            
                # Create a file to write the parsed data to 
                pitch_save_file = open(pitch_file_path,'w')
                # write to that newly created file
                pitch_save_file.write(pitching_data)
                #close that file
                pitch_save_file.close()
            # check this current team for any JUCO players
            checkForJUCO(hit_file_path,driver,team_url)
            checkForJUCO(pitch_file_path,driver,team_url)
    # Close the window
    driver.quit()

def checkForJUCO(file_path,driver,team_url):
    # Open the yearly hitting or pitching data
    team_data = pd.read_csv(file_path)
    roster = list(team_data['Player Name'])
    
    # refresh the page that the scraper just pulled the data from 
    driver.refresh()
    time.sleep(3)
    for name in roster:
        
        player_link = driver.find_element_by_link_text(str(name))
        player_link.click()
        # save the player id
        player_id = str(driver.current_url)[-6:]
        player_id = re.findall(r'[0-9]+',player_id)[0]
        # see if this player has already been checked
        if player_id in checked_JUCO_players:
            driver.get(team_url)
            continue
        else:
            try:
                csv_button = driver.find_element_by_id("csv_text_grid1")
            except BaseException:
                csv_button = driver.find_element_by_id("csv_text_grid2")
            csv_button.click()
            time.sleep(5)
            #find the player's full data 
            player_pagesource = driver.page_source
            soup = BeautifulSoup(player_pagesource, 'html5lib')
            try:
                # find the hitting table by it's "grid1" id 
                player_table_html = soup.find('table',attrs={'id':'grid1'})
            except BaseException:
                player_table_html = soup.find('table',attrs={'id':'grid2'})
            # find all of the rows of this table
            player_table = player_table_html.find_all('tr')
            # create an empty string that will house all of the data from the table
            player_data = ""
            # for each row in the table:
            for row in player_table:
                # find all data in that row & get rid of the <td> tags
                row_data = str(row.find_all('td')).replace('<td>','')
                # get rid of the close tags
                row_data = row_data.replace('</td>','')
                # get rid of the open and close brackets
                row_data = row_data.replace('[','')
                row_data = row_data.replace(']','\n') # also put a new line at the end 
            
                # append the row to the entire data set
                player_data = player_data + row_data
            
            # Create a file to write the parsed data to 
            player_save_file = open('../CapstoneBaseballData/PlayerHistory/'+str(name).replace(" ","_")+'_Career.csv','w')
            # write to that newly created file
            player_save_file.write(player_data)
            #close that file
            player_save_file.close()    
            # check to see that a player played in JUCO
            temp_data = pd.read_csv('../CapstoneBaseballData/PlayerHistory/'+str(name).replace(" ","_")+'_Career.csv')
            temp_data.drop(temp_data.tail(2).index,inplace = True)
            confs = temp_data.Lvl.unique()
            keep_file = False
            for conf in confs:
                if conf == "NJCAA":
                    keep_file = True
            if not keep_file:
                os.remove('../CapstoneBaseballData/PlayerHistory/'+str(name).replace(" ","_")+'_Career.csv')
            
            # save newly checked player to the dictionary of already checked players
            checked_JUCO_players[player_id] = name
            
            driver.get(team_url)

# def checkForJUCO(data_directory):
    
#     #will search for players from the home page
#     home_page = "http://www.thebaseballcube.com"
#     # set up adblocker
#     chop = webdriver.ChromeOptions()
#     chop.add_extension('/Users/Public/anaconda3/bin/ADBLOCK4.40.0-Crx4Chrome.com.crx')
#     # set the web driver
#     driver = webdriver.Chrome('/Users/Public/anaconda3/bin/chromedriver.exe',chrome_options=chop)
    
#     # loop over each file I have data for
#     for file in os.scandir(data_directory):
#         # read it into a pandas data frame
#         data = pd.read_csv(file.path)
#         # get a list of the names
#         names = list(data["Player Name"])
#         for name in names:
#             print(name)
#             # check if this player has already been found to have JUCO data
#             if not os.path.exists('../CapstoneBaseballData/PlayerHistory/'+str(name).replace(" ","_")+'_Career.csv'):
#                 # Navigate to the baseballcube website
#                 driver.get(home_page)
#                 # find the search bar
#                 search = driver.find_element_by_name("search")
#                 search.click()
#                 # search for player
#                 search.send_keys(str(name),Keys.ENTER)
#                 try:
#                     # Locate the csv button by it's ID
#                     csv_button = driver.find_element_by_id("csv_text_grid1")
#                 except BaseException:
#                     try:
#                         link = driver.find_element_by_link_text(name)
#                         link.click()
#                         # Locate the csv button by it's ID
#                         csv_button = driver.find_element_by_id("csv_text_grid1")
#                     except BaseException:
#                         try:
#                             first_last = str(name).split()
#                             first = first_last[0]
#                             last = first_last[1]
#                             last = last[0] + str(last[1:]).lower()
#                             full_name = first + " " + last
#                             link = driver.find_element_by_link_text(full_name)
#                             link.click()
#                             # Locate the csv button by it's ID
#                             csv_button = driver.find_element_by_id("csv_text_grid1")
#                         except BaseException:
#                             continue
#                 # Click the csv button to convert the table
#                 csv_button.click()
#                 # wait for html to update
#                 time.sleep(10)
#                 #find the player's full data 
#                 player_pagesource = driver.page_source
#                 soup = BeautifulSoup(player_pagesource, 'html5lib')
#                 # find the hitting table by it's "grid1" id 
#                 player_table_html = soup.find('table',attrs={'id':'grid1'})
            
#                 # find all of the rows of this table
#                 player_table = player_table_html.find_all('tr')
#                 # create an empty string that will house all of the data from the table
#                 player_data = ""
#                 # for each row in the table:
#                 for row in player_table:
#                     # find all data in that row & get rid of the <td> tags
#                     row_data = str(row.find_all('td')).replace('<td>','')
#                     # get rid of the close tags
#                     row_data = row_data.replace('</td>','')
#                     # get rid of the open and close brackets
#                     row_data = row_data.replace('[','')
#                     row_data = row_data.replace(']','\n') # also put a new line at the end 
                
#                     # append the row to the entire data set
#                     player_data = player_data + row_data
                
#                 # Create a file to write the parsed data to 
#                 player_save_file = open('../CapstoneBaseballData/PlayerHistory/'+str(name).replace(" ","_")+'_Career.csv','w')
#                 # write to that newly created file
#                 player_save_file.write(player_data)
#                 #close that file
#                 player_save_file.close()    
#                 # check to see that a player played in JUCO
#                 temp_data = pd.read_csv('../CapstoneBaseballData/PlayerHistory/'+str(name).replace(" ","_")+'_Career.csv')
#                 temp_data.drop(temp_data.tail(2).index,inplace = True)
#                 confs = temp_data.Lvl.unique()
#                 keep_file = False
#                 for conf in confs:
#                     if conf == "NJCAA":
#                         keep_file = True
#                 if not keep_file:
#                     os.remove('../CapstoneBaseballData/PlayerHistory/'+str(name).replace(" ","_")+'_Career.csv')
#     driver.quit()
                
                