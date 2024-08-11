import json
import ast
import pandas as pd
from openai import OpenAI


client=''

def categorise_posts(post):
    # Analyze the post using OpenAI
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a professional LinkedIn post analyzer. Your task is to categorize the post as wide, deep, warm, and whether it is organic or not."},
            {"role": "user", "content": f"Analyze this LinkedIn post: {post}"},
            {"role": "system", "content": "Return into this fdictionary format: 'warm':True/False,'deep':True/False,'wide':True/False,'orginic':True'False"}
        ],
        temperature=0.4
    )
    analysis = response.choices[0].message.content
    return ast.literal_eval(analysis)

def analyze_image(image_url,categories):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                # {"role": "system", "content": f"You are a professional image analyzer. Analyze the given image and categorise it to one of the categories {categories}"},
                {"role": "user", "content": [
                    {"type":"text","text":f"You are a professional image analyzer. Analyze the given image and categorise it to one of the categories {categories} \n directly return the category"},
                    {"type":"image_url","image_url":{"url":image_url}}
                ]}
            ]
        )
    except:
        print("Invalid Image")
        return None

    analysis = response.choices[0].message.content
    return analysis

def manipulate_profile(linkedin_profile,grading_parameters):
    #Warm
    warm_profile={}
    deep_profile={}
    wide_profile={}
    profile_pic_categories = grading_parameters.loc[(grading_parameters['Type'] == 'Warm') & (grading_parameters['Category'] == 'Profile Pic'), 'Description'].unique()
    cover_page_categories = grading_parameters.loc[(grading_parameters['Type'] == 'Warm') & (grading_parameters['Category'] == 'Cover Page'), 'Description'].unique()
    profile_pic=analyze_image(linkedin_profile['Profile Pic'],profile_pic_categories)
    cover_page=analyze_image(linkedin_profile['Cover Page'],cover_page_categories)
    warm_profile.update({'Profile Pic':profile_pic})
    warm_profile.update({'Cover Page':cover_page})
    for i in range(len(linkedin_profile['posts'])):
        linkedin_profile['posts'][i].update({"Type":categorise_posts(linkedin_profile['posts'][i])})
    warm_profile.update({"posts":[]})
    wide_profile.update({"posts":[]})
    for post in linkedin_profile['posts']:
        if post["Type"]['warm'] or post["Type"]['organic']:
            warm_profile['posts'].append(post)
        if post["Type"]['wide'] or post["Type"]['organic']:
            wide_profile['posts'].append(post)

    #Deep
    deep_profile.update({'posts':linkedin_profile['posts']})
    deep_profile.update({'publications':linkedin_profile['publications']})
    
    #Wide
    wide_profile.update({'connections':linkedin_profile['connections']})
    wide_profile.update({'followers':linkedin_profile['followers']})
    wide_profile.update({'headline':linkedin_profile['headline']})
    wide_profile.update({'Summary':linkedin_profile['Summary']})
    wide_profile.update({'experiences':linkedin_profile['experiences']})
    wide_profile.update({'education':linkedin_profile['education']})
    wide_profile.update({'licenses_and_certifications':linkedin_profile['licenses_and_certifications']})
    wide_profile.update({'groups':linkedin_profile['groups']})
    wide_profile.update({'recommendations_received':linkedin_profile['recommendations_received']})
    wide_profile.update({'recommendations_given':linkedin_profile['recommendations_given']})
    wide_profile.update({'skills':linkedin_profile['skills']})
    wide_profile.update({'projects':linkedin_profile['projects']})
    
    return warm_profile,deep_profile,wide_profile

def analyse_profile(profile, parameters,Type,temperature):
    scoring_categories = parameters['Category'].unique()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a professional LinkedIn profile grader. Your task is to grade this LinkedIn profile and provide a numeric average score rounder upto 1 decimal."},
            {"role": "system", "content": f"Analyze the LinkedIn profile based on the following parameters and give a total score according to the scoring column:\n{parameters}"},
            {"role": "user", "content": f"Here is the LinkedIn profile:\n{profile}"},
            {"role": "user", "content": f"These are the categories you need to score based on the above dataframe:\n{scoring_categories}."},
            {"role":"system","content":f"don't give in markdown format"}
            
        ],
        temperature=temperature
    )
    grade = response.choices[0].message.content
    return grade

def grade_linkedin_profile(parameters,profile,api_key):
    global client
    client= OpenAI(api_key=api_key)
    
    warm_parameters=parameters[parameters['Type']=='Warm']
    deep_parameters=parameters[parameters['Type']=='Deep']
    wide_parameters=parameters[parameters['Type']=='Wide']
    
    warm_profile,deep_profile,wide_profile=manipulate_profile(profile,parameters)
    
    grade_warm=analyse_profile(warm_profile,warm_parameters,'Warm',0.2)
    grade_deep=analyse_profile(deep_profile,deep_parameters,'Deep',0.4)
    grade_wide=analyse_profile(wide_profile,wide_parameters,'Wide',0.2)
        
    return grade_warm,grade_deep,grade_wide


# with open('1729digital/profiles/linkedin_profile_dipzgupta.json', 'r') as file:
#     linkedin_profile = json.load(file)

# # Load grading parameters from Excel
# grading_parameters = pd.read_excel('1729digital/gradin_parameters1.xlsx')

# warm,deep,wide=grade_linkedin_profile(grading_parameters,linkedin_profile)
# print("Warm\n",warm)
# print("Deep\n",deep)
# print("Wide\n",wide)