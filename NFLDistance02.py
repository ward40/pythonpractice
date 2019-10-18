import pandas as pd
import haversine as h
import math as m
import matplotlib.pyplot as plt


stadiums = pd.read_csv('stadiums.csv')
scores = pd.read_csv('2018 scores.csv')
teams = scores.team_home.drop_duplicates()

def gameresult(team,week):
    week = str(week)
    teamwins = scores[(((scores.team_home == team) & (scores.score_home > scores.score_away)) | (
                (scores.team_away == team) & (scores.score_home < scores.score_away)))& (scores.schedule_week == week)]
    teamlosses = scores[(((scores.team_home == team) & (scores.score_home < scores.score_away)) | (
                (scores.team_away == team) & (scores.score_home > scores.score_away)))& (scores.schedule_week == week) ]
    teamties = scores[(((scores.team_home == team) | (scores.team_away == team)) & (
                scores.score_home == scores.score_away)) & (scores.schedule_week == week)]

    wins = len(teamwins.index)
    losses = len(teamlosses.index)
    ties = len(teamties.index)

    if wins == 1:
        return 1
    elif losses == 1:
        return 0
    elif ties == 1:
        return 0.5
    else:
        return "BYE"

#print(gameresult("New England Patriots",5))

def gamegps(team,week):
    week = str(week)
    details = scores.loc[((scores.team_home == team) | (scores.team_away == team)) & (scores.schedule_week == week)]
    mergeddetails = pd.merge(left = details, right = stadiums, left_on = 'stadium', right_on = 'stadium_name')
    dfcoord = mergeddetails[['LATITUDE','LONGITUDE']]
    coord = dfcoord.values.flatten()
    gamecoordinates = tuple(coord)
    if len(gamecoordinates) < 2:
        return "BYE"
    else:
        return (gamecoordinates)

#print(gamegps("Chicago Bears",5))

def teamhomegps(team):
    if team in ('New York Giants','New York Jets'):
        homedetails = stadiums.loc[(stadiums.stadium_team == 'NEW YORK')]
    else:
        homedetails = stadiums.loc[(stadiums.stadium_team == team)]
    homecoordinates = homedetails['LATITUDE'].tolist()[0],homedetails['LONGITUDE'].tolist()[0]
    return (homecoordinates)

#teamhomegps("New England Patriots")


def weekdistance(team,week):
    gamecoordinates = gamegps(team,week)
    if gamecoordinates == 'BYE':
        return "BYE"
    else:
        teamcoordinates = teamhomegps(team)
        #print("Game GPS:",gamecoordinates,"Team GPS:",teamcoordinates)
        distance_miles = h.Haversine(gamecoordinates,teamcoordinates).miles
        return(distance_miles)

#print(weekdistance("Chicago Bears",5))

def compile_distance_data (team,week):
    distance = weekdistance(team,week)
    result = gameresult(team,week)
    data = distance,result
    return data
    #print(data)

#compile_distance_data("Chicago Bears",1)


#teams2 = ("New England Patriots","Chicago Bears")


#compile data into list format
result = []
for team in teams:
    for week in range (20):
        weeklydata = compile_distance_data(team, week)
        if weeklydata == ('BYE', 'BYE'):
            x=1
        else:
            result.append(weeklydata)


#create aggregate data
resultdf = pd.DataFrame(result,columns = ("Distance","Result")).sort_values("Distance").reset_index(drop=True)
resultdf["Group"] = ""

distanceincrement = 300
distancecap = 2000

for i in resultdf.index:
    if resultdf.get_value(i, 'Distance') == 0:
        resultdf.set_value(i, 'Group', 0)
    else:
        num = resultdf.get_value(i, 'Distance')
        distancegroup = num - (num % distanceincrement) + distanceincrement
        if distancegroup > distancecap:
            resultdf.set_value(i, 'Group', distancecap)
        else:
            resultdf.set_value(i, 'Group', distancegroup)

#resultdfdistance = resultdf.groupby('Group',as_index=False)['Result'].mean()
#resultdfcount = resultdf.groupby('Group',as_index=False)['Distance'].count()
#grouplabel = list(resultdfcount['Group'])

#create graph data
resultplotdata = resultdf.groupby(
   'Group').agg(
    {
    'Group': "count",    # count of groups
    'Result': "mean"  # get the count of Distance
    })

resultplotdata.plot.bar(y='Result',legend = None)

#Create labels
countlabel = list(resultplotdata['Group'])
distancelabel = list(resultplotdata['Result'])
grouplabel = list(resultplotdata.index.values)

#Text on the top of each barplot
for i in range(len(countlabel)):
    plt.text(x=i, y=0.025, s=countlabel[i], size=6)

plt.title("NFL Win % vs Distance Traveled")
plt.xlabel("Distance (miles)")
plt.ylabel("Win %")
plt.subplots_adjust(bottom= 0.17)
plt.show()


#export_csv = resultdf.to_csv(r'/Users/jeremyward/PycharmProjects/NFL/test_results.csv', index = None, header=True)
#export_csv = resultdf.to_csv(r'/Users/jeremyward/PycharmProjects/NFL/distance_results.csv', index = None, header=True)

