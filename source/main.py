# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 13:12:16 2021

@author: Francisco Vazquez

This file will be the place that runs the scraping function in an automated 
fashion. It begins by grabbing the yearly statistics for each team that Valpo
was in conference with every year going back to 2008. 

It then takes all the players that data was gathered for and searches 
thebaseballcube.com for that player's career stats. This is done to check to see
if that player had played for a Junior College before. 
"""
from BaseballCube_WebScrape import scrapeYearlyStats

start_Year = 2008
end_Year = 2021

scrapeYearlyStats(start_Year,end_Year)
    