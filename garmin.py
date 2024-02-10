import json 
import requests
import collections
import progressbar
import bing_image_urls

# Opening JSON file 
f = open('exercises.json',)
# GarminURl = 'https://connect.garmin.com/web-data/exercises/Exercises.json'
# returns JSON object as a dictionary 
data = json.load(f) 
#Close file
f.close() 

translationWeb = requests.get('https://connect.garmin.com/web-translations/exercise_types/exercise_types_es.properties')
translation = {}

if translationWeb.status_code == 200:
    for line in translationWeb.text.split('\n'):
        if line.find("="):
            vars = line.split("=")
            if len(vars) == 2:
                translation [vars[0]] = vars[1]

exercises = []
display1 = ""

bar1 = progressbar.ProgressBar(
    max_value=len(data['categories']),
    variables={'category': '-'},
    prefix='{variables.category}',
    line_offset=1
    )
print('\n')
# Iterating through the json list 
for category in data['categories']: 
    bar2 = progressbar.ProgressBar(
        max_value=len(data['categories'][category]['exercises']),
        variables={'exercise': '-'},
        prefix='{variables.exercise}',
        line_offset=2
        )
    bar1.update(bar1.value, category=category.replace('_',' ').title())
    for exercise in data['categories'][category]['exercises']:
        bar2.update(bar2.value, exercise=exercise.replace('_',' ').title())
        exercise_dict = collections.defaultdict(lambda : '')
        exercise_dict["NAME_GARMIN"] = exercise
        exercise_dict["CATEGORY_GARMIN"] = category
        try:
            exercise_dict["Name"] = translation[category+'_'+exercise]
        except:
            exercise_dict["Name"] = exercise.replace('_',' ').title()
        try:    
            exercise_dict["Category"] = translation["category_type_"+category]
        except:
            exercise_dict["Category"] = ""
        for k,v in data['categories'][category]['exercises'][exercise].items():
            if isinstance(v, list):
                for v2 in v:
                    if isinstance(v2, dict):
                        for k3,v3 in v2.items():
                            exercise_dict[k3]=v3
                    else:
                        if k in ['primaryMuscles','secondaryMuscles']:
                            try:
                                v2 = translation["muscle_type_"+v2]
                            except:
                                v2 = v2
                        if exercise_dict.get(k) is not None:
                            if not isinstance(exercise_dict[k],list): exercise_dict[k] = [exercise_dict[k]]
                            exercise_dict[k].append(v2)
                        else: 
                            exercise_dict[k]=v2
            elif isinstance(v, dict):
                for k2, v2 in v.items():
                    exercise_dict[k2]=v2
            else:
                exercise_dict[k]=v
    
        #URL based on known path and exercice name
        URLjson = 'https://connect.garmin.com/web-data/exercises/es-ES/' + category+"/"+exercise + '.json'
        page = requests.get(URLjson)

        #if page exists (200), then there are details for the exercice
        if page.status_code == 200:
            exdata = json.loads(page.text)
            for k, v in exdata.items():
                if k not in ['primaryMuscles','secondaryMuscles']:
                    if isinstance(v, list):
                        for v2 in v:
                            if isinstance(v2, dict):
                                for k3,v3 in v2.items():
                                    if k3 in exercise_dict:
                                        if isinstance(exercise_dict[k3], list):
                                            exercise_dict[k3].append(v3)
                                        elif isinstance(exercise_dict[k3], str):
                                            exercise_dict[k3] = [exercise_dict[k3]]
                                            exercise_dict[k3].append(v3)
                                    else:
                                        exercise_dict[k3]=v3
                            else:
                                if exercise_dict.get(k) is not None:
                                    if not isinstance(exercise_dict[k],list): exercise_dict[k] = [exercise_dict[k]]
                                    exercise_dict[k].append(v2)
                                else: 
                                    exercise_dict[k]=v2
                    elif isinstance(v, dict):
                        for k2, v2 in v.items():
                            exercise_dict[k2]=v2
                    else:
                        exercise_dict[k]=v
            exercise_dict["URL"] = "https://connect.garmin.com/modern/exercises/"+category+"/"+exercise
        else:
            imageUrl = bing_image_urls.bing_image_urls(exercise.replace('_',' ').title(), limit=1)[0]
            exercise_dict['heroImage'] = imageUrl
        exercises.append(exercise_dict)
        bar2.next()
    bar1.next()
export_data = {}
export_data["data"]=exercises

# Output:
# This will create a file named 'data.json' and write the JSON data into it.
with open('../web/garmin/data.json', 'w') as f:
    json.dump(export_data, f)