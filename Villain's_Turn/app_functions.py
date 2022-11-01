# Imports
import pandas as pd
import numpy as np
import random

def read_import(path,import_groups=True):
    party = pd.read_csv(path)
    if import_groups and ('group' in list(party)):
        return party
    else:
        party["group"] = np.nan
        return party

def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')

def sort_by_initiatives(groups:pd.DataFrame):
    df = groups.copy()
    df['total_initiative'] = df['initiative']+df['initiative_bonus']
    df.sort_values(by='total_initiative',ascending=False,inplace=True)
    return df.drop(columns="total_initiative")

def initiative_based_group_assignment(groups:pd.DataFrame):
    df = sort_by_initiatives(groups)
    df_count = {}
    team_order = df['team']
    group_placement = []
    lastTeam = None
    for team in team_order:
        if team != lastTeam :
            if team in df_count.keys() :
                df_count[team]+=1
            else :
                df_count[team]=1
            lastTeam = team
        group_placement.append(f"{team} {df_count[team]}")
    df['group']=group_placement
    return df

def roll(sided=20):
    return random.randint(1,sided)

def auto_initiative(groups:pd.DataFrame):
    df = groups.copy()
    df['initiative'] = df['initiative'].apply(lambda x: roll(20))
    return df

def groups_list(turn_track:pd.DataFrame):
    return(turn_track['group'].unique())

def character_list(turn_track:pd.DataFrame):
    return(turn_track['name'].unique())

def team_list(turn_track:pd.DataFrame):
    return(turn_track['team'].unique())

def df_match_slice(df:pd.DataFrame,column,match):
    return df[df[column]==match]

def df_set_match_slice(df:pd.DataFrame,column,match,new_data):
    df_slice = df[df[column] == match].copy()
    df_slice[column] = new_data
    df_copy = df.copy()
    df_copy.update(df_slice)
    return df_copy

def remove_group_assignments(groups:pd.DataFrame):
    df = groups.copy()
    df['group']=np.nan
    return df

def individual_groups(groups:pd.DataFrame):
    df = groups.copy()
    df['group']=df['name']
    return df

def move_group(groups:pd.DataFrame,group_to_move,before_or_after,group_to_place):
    df = groups.copy()
    slice_group_to_move = df[df['group']==group_to_move].copy()
    df.drop(slice_group_to_move.index,inplace=True)
    if before_or_after == "Before" :
        index_split_point = (df[df['group']==group_to_place].index[0]) #first index
    else :
        index_split_point = df[df['group']==group_to_place].index[-1]+1 #last index
    return pd.concat([df.iloc[:index_split_point],slice_group_to_move,df.iloc[index_split_point:]])