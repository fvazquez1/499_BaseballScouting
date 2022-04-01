# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 23:43:59 2022

All analysis will be done in this file via different functions. 
The different functions will be called from main.py

@author: Francisco Vazquez
"""
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.metrics import mean_squared_error
from fast_ml.model_development import train_valid_test_split
from datetime import datetime
import os
import pandas as pd
import joblib
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt

def split_data(dataframe,target_col,train_perc=.6,test_perc=.2,val_perc=.2):
    data = dataframe
    keep_col = data[target_col]
    # get rid of unecessary columns
    data = data[data.columns.drop(list(data.filter(regex='ncaa')))]
    
    data[target_col] = keep_col
    
    X_train, y_train, X_valid, y_valid, X_test, y_test = train_valid_test_split(data, 
                                                                                target = target_col,
                                                                                train_size=train_perc,
                                                                                valid_size=val_perc, 
                                                                                test_size=test_perc,
                                                                                random_state=2022)
    print(X_train.shape), print(y_train.shape)
    print(X_valid.shape), print(y_valid.shape)
    print(X_test.shape), print(y_test.shape)
    
    return X_train,y_train,X_valid,y_valid,X_test,y_test

def generateBestModel(X_train,y_train,X_valid,y_valid):
    lin = LinearRegression()
    lin.fit(X=X_train, y=y_train)
    ran_for = RandomForestRegressor(random_state=2022).fit(X_train,y_train)
    ext_for = ExtraTreesRegressor(random_state=2022).fit(X_train,y_train)
    
    lin_preds = lin.predict(X_valid)
    ran_for_preds = ran_for.predict(X_valid)
    ext_for_preds = ext_for.predict(X_valid)
    
    lin_mse = mean_squared_error(y_valid,lin_preds)
    ran_for_mse = mean_squared_error(y_valid,ran_for_preds)
    ext_for_mse = mean_squared_error(y_valid,ext_for_preds)
    
    print("MSE for...")
    print("Linear Model: "+ str(lin_mse))
    print("Random Forest Model: " + str(ran_for_mse))
    print("Extra Trees Model: " + str(ext_for_mse))
    
    if (lin_mse < ran_for_mse) & (lin_mse < ext_for_mse):
        print("Linear Model is best")
        best_model = "Linear"
        return best_model, lin
    elif (ran_for_mse < lin_mse) & (ran_for_mse < ext_for_mse):
        print("Random Forest is best")
        best_model = "Random Forest"
        return best_model, ran_for
    else:
        print("Extra Trees Model is best")
        best_model = "Extra Trees"
        return best_model, ext_for

def getRSquared(model,X_test,y_test):
    print("R^2: " + str(model.score(X_test,y_test)))    
    
def useModelToPredict(model,model_name,var_name,X_test,y_test):
    preds = model.predict(X_test)
    df = pd.DataFrame()
    df["Preds"] = preds
    df.reset_index(inplace=True)
    df["Actual"] = y_test.values
    #df.plot.scatter(x="Preds",y="Actual",title=(model_name + " for " + var_name))
    plt.figure()
    plt.scatter(df['Preds'],df['Actual'])
    plt.plot(df['Preds'],df['Preds'],color='black')
    plt.title(model_name + " for " + var_name)
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    
    print(df)
    
    print("MSE for Test Set: " + str(mean_squared_error(y_test,preds)))
    return(mean_squared_error(y_test,preds))
    
def fit_models_to_data(data,hit_pitch,train_perc=.7,test_perc=.2,val_perc=.1):
    mses = []
    for stat in data.keys():
        if 'ncaa' in stat:
            print(stat)
            X_train,y_train,X_valid,y_valid,X_test,y_test = split_data(data,
                                                                       str(stat),
                                                                       train_perc=train_perc,
                                                                       test_perc=test_perc,
                                                                       val_perc=val_perc)
    
            model_name,model = generateBestModel(X_train,y_train,X_valid,y_valid)
            getRSquared(model,X_test,y_test)
            mse = useModelToPredict(model,model_name,stat,X_test,y_test)
            mses.append(mse)
            
            model_path = '../SavedModels/'+str(hit_pitch)+'/'+str(stat)+'.joblib'
            if not os.path.exists(model_path):
                joblib.dump(model,model_path,compress=3)
            else:
                os.remove(model_path)
                joblib.dump(model,model_path,compress=3)
    return mses

def getRadarPlot(hit_pitch = 'Hit'):
    currentYear = datetime.now().year
    directory = '../SavedModels/'+str(hit_pitch)
    if hit_pitch == 'Hit':
        new_player_file = '../CapstoneBaseballData/New_JUCO_Data/HitTemplate.csv'
    else:
        new_player_file = '../CapstoneBaseballData/New_JUCO_Data/PitchTemplate.csv'
    new_player_df = pd.read_csv(new_player_file)
    new_player_df = new_player_df.drop('Name',axis=1)
    print(new_player_df.keys())
    print(new_player_df.head())
    for stat in new_player_df.keys():
        for filename in os.listdir(directory):
            f = os.path.join(directory, filename)
            # checking if it is a file
            if os.path.isfile(f):
                    if stat in f:
                        print(f)
                        model = joblib.load(f)
                        pred = model.predict(new_player_df[new_player_df.columns.drop(list(new_player_df.filter(regex='pred_')))])
                        pred_col = 'pred_'+str(stat)
                        new_player_df[pred_col] = pred
    stat1 = []
    stat2 = []
    stat3 = []
    stat4 = []
    stat5 = []
    if hit_pitch == 'Hit':
        directory = '../CapstoneBaseballData/Hitting'
        cols = ['AVG','RBI','OBP','SLG','SO%']
    else:
        directory = '../CapstoneBaseballData/Pitching'
        cols = ['ERA','WHIP','H9','BB9','SO9']
    
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        # checking if it is a file
        if os.path.isfile(f):
            if str(currentYear-1) in f:
                data = pd.read_csv(f)
                stat1.extend(data[str(cols[0])].to_list())
                stat2.extend(data[str(cols[1])].to_list())
                stat3.extend(data[str(cols[2])].to_list())
                stat4.extend(data[str(cols[3])].to_list())
                stat5.extend(data[str(cols[4])].to_list())
    
    percentiles = pd.DataFrame(columns=['stat','percentile'])
    percentiles['stat']=cols
    pec_ls = []
    for stat in cols:
        val = new_player_df[str('pred_'+stat)]
        count = sum(i < val for i in stat1)
        percentile = (count/len(stat1))*100
        pec_ls.append(percentile)
    percentiles['percentile'] = pec_ls
    
    print(percentiles.head())
    # percentiles = percentiles.reset_index(drop=True)
    # fig = px.line_polar(percentiles, r='percentile', theta='stat', line_close=True)
    # fig.show()
    
    make_radar_chart('Predicted Percentile\n(Using Predicted NCAA Stats & Last Year MVC Stats)',
                     stats = pec_ls, attribute_labels=cols,
                     plot_markers=[0,10,20,30,40,50,60,70,80,90,100],
                     plot_str_markers=["0","10","20","30","40","50","60","70","80","90","100"])

def make_radar_chart(name, stats, attribute_labels,
                     plot_markers, plot_str_markers):

    labels = np.array(attribute_labels)

    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False)
    stats = np.concatenate((stats,[stats[0]]))
    angles = np.concatenate((angles,[angles[0]]))

    fig = plt.figure(figsize=(10,10))
    ax = fig.add_subplot(111, polar=True)
    ax.plot(angles, stats, 'o-', linewidth=2)
    ax.fill(angles, stats, alpha=0.25)
    ax.set_thetagrids(angles * 180/np.pi, labels)
    plt.yticks(plot_markers)
    ax.set_title(name)
    ax.grid(True)

    # fig.savefig("static/images/%s.png" % name)

    return plt.show()