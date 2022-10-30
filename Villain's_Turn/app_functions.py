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

def initiative_based_group_assignment(groups:pd.DataFrame):
    df = groups.copy()
    df['total_initiative'] = df['initiative']+df['initiative_bonus']
    df.sort_values(by='total_initiative',ascending=False,inplace=True)
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
    return df.drop(columns="total_initiative")

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

def df_match_slice(df:pd.DataFrame,column,match):
    return df[df[column]==match]

def df_set_match_slice(df:pd.DataFrame,column,match,new_data):
    df_slice = df[df[column] == match].copy()
    df_slice[column] = new_data
    df_copy = df.copy()
    df_copy.update(df_slice)
    return df_copy

def change_group_assignment(groups:pd.DataFrame,new_value):
    return

def remove_group_assignments(groups:pd.DataFrame):
    df = groups.copy()
    df['group']=np.nan
    return df

def individual_groups(groups:pd.DataFrame):
    df = groups.copy()
    df['group']=df['name']
    return df