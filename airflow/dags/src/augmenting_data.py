import os
from dotenv import load_dotenv
import praw
import redis
from pymongo import MongoClient, errors
import re
import datetime
import pandas as pd
import datetime
import requests






def test_mongo():

    try:
        print('working_directory:', os.getcwd())
        client = MongoClient("mongodb://mongo:27017/")  # Replace with your URI
        client.server_info()  # Force connection to the server
        print("Connected to MongoDB!")
    except errors.ServerSelectionTimeoutError as err:
        print(f"Connection failed: {err}")
        return False


def connect_to_mongo():
    # Load environment variables from .env file
    os.chdir('../../') 
    print(os.getcwd())
         
   
      # MongoDB connection details
    mongo_host = 'mongo'  # Docker service name for MongoDB
    mongo_port = 27017

    try:
        # Establish connection to MongoDB
        print('connecting to mongo')
        client = MongoClient("mongodb://mongo:27017/")  # Replace with your URI
        client.server_info()  # Force connection to the server

    
        return client
    
    except Exception as e:
        print("An error occurred while connecting to MongoDB:", e)
        raise e





def augment_documents(limit):
    print('starting augmentation')
    client = connect_to_mongo()
    log_errors=[]
    if client is None:
        print("Error connecting to MongoDB")
        return False
    db_ingestion=client['Ingestion_db']
    db_staging=client['Staging_db']
    documents=get_documents(db_ingestion, 'reddit_ingestion', limit)
    answer_nb=0
    error_nb=0
    total=0
    for document in documents:
        del document['staged']
        response_mistrale=None
        total+=1
        id=document['id']
        title=document['title']
        text=document['self_text']
        try:
            prompt=create_prompt(title, text)
            response_mistrale=get_mistral_response(prompt)
            response=augmented_json_data(response_mistrale)
            if response['Sentiment']=='[answer]':
                print(f"Error [answer] processing document with id: {id}")
                answer_nb+=1
                continue
            db_staging.reddit_llm.insert_one(document)
            db_staging.reddit_llm.update_one({'id': id}, {'$set': response})
            db_ingestion.reddit_ingestion.update_one({'id': id}, {'$set': {'staged': 1}})
            print(f"Updated document with id: {id}")
        except Exception as e:
            log_errors.append({'id': id,'text':response_mistrale, 'error': e})
            print(f"Error processing document with id: {id}")
            print(e)
            error_nb+=1
    
    if total==0:
        print("No documents to process")
        return False
    
    print(f"error recorded: {error_nb}/{total}= {(error_nb/total)*100}")
    print(f"error answer recorded: {answer_nb}/{total}= {(answer_nb/total)*100}")
    df=pd.DataFrame(log_errors)
    print(df)
    print("Current working directory:", os.getcwd())
    timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    day=datetime.datetime.now().strftime("%Y%m%d")
    # Create the directory if it doesn't exist
    os.makedirs(f'/opt/airflow/dags/error_logs/{day}', exist_ok=True)
    df.to_csv(f'/opt/airflow/dags/error_logs/{day}/logs_{timestamp}.csv')

def create_prompt(title, text):
    prompt = f'''
        Analyze the following Reddit post and provide concise answers to these features. 
        Use "Yes" or "No" for binary questions, and specify "Null" if information is unclear or not mentioned. Avoid explanations.

        Features to extract:

        Sentiment: positive/negative/neutral (if unclear put null)
        Topic: Technology/medication/education/social 
        Personal Experience Shared: Yes/No
        Mention of Solutions: Yes/No (if any solutions, advice, or recommendations are discussed just answer no explanation)
        Gender of the Author: Male/Female/Null
        Self-Diagnosis: Yes/No (keyword 'self-diagnosis')
        Self-Medication: Yes/No (keyword 'self-medication' exits in this text ?)
        Post for analysis:
    
        {text}



        Provide the answers in a structured format like the following:
        Sentiment: [answer]
        Topic:  [answer]
        Personal Experience Shared:  [answer]
        Mention of Solutions:  [answer]
        Gender of the Author:  [answer]
        Self-Diagnosis:  [answer]
        Self-Medication:  [answer]
        
        
        Do not leave "[answer]" as a response. Always replace it with one of the specified valid answers or "Null.
        '''
    return prompt

def get_documents(db, collection, limit=10):
    # Get the documents from the specified collection
    documents = db[collection].find({'staged': 0}, {'_id': 0}).limit(limit)
    return documents

def augmented_json_data(text):
    
    # generated_text = parsed_data[0]['generated_text']
    # generated_text_splitten = list(filter(None, generated_text_splitten))
    # # Remove strings that are only whitespace characters
    # generated_text_splitten = [line for line in generated_text_splitten if not line.isspace()]
    # generated_text_splitten = generated_text.split('\n\n')[-1].split('\n')
    # print('generated_text_splitten',generated_text_splitten)
    # # Remove leading and trailing spaces from each element
    # generated_text_splitten = [line.strip() for line in generated_text_splitten]

    # if(test_results('1',generated_text_splitten)):
    #     print('True')
    #     #continue
    # else:
    #     #refix the generated text
    #     print('False')
    #     flas_text=generated_text.split('\n\n')[-2].split('\n')
    #     flas_text = [line.strip() for line in flas_text]
    #     print(flas_text)
        
    response=text
    response=response[0]['generated_text'].split('\n\n')[-1].split('\n')[-7:]
    response = [line.strip() for line in response]
            
    try:    
        extracted_features = {
        "Sentiment": response[0].split(':')[1].strip().split(' ')[0],
        "Topic": response[1].split(':')[1].strip().split(' ')[0],
        "Personal_Experience": response[2].split(':')[1].strip().split(' ')[0],
        "Mention of Solutions": response[3].split(':')[1].strip().split(' ')[0],
        "Gender": response[4].split(':')[1].strip().split(' ')[0],
        "Self-Diagnosis": response[5].split(':')[1].strip().split(' ')[0],
        "Self-Medication": response[6].split(':')[1].strip().split(' ')[0],
        "augmented": 0
        }
    except Exception as e:
        print('second apprach to extract features')
        secondresponse=text
        secondresponse=secondresponse[0]['generated_text']
        secondresponse=secondresponse.split('\n\n')[-2].split('\n')
        secondresponse = [line.strip() for line in secondresponse]
        
        extracted_features = {
        "Sentiment": secondresponse[0].split(':')[1].strip().split(' ')[0],
        "Topic": secondresponse[1].split(':')[1].strip().split(' ')[0],
        "Personal_Experience": secondresponse[2].split(':')[1].strip().split(' ')[0],
        "Mention of Solutions": secondresponse[3].split(':')[1].strip().split(' ')[0],
        "Gender": secondresponse[4].split(':')[1].strip().split(' ')[0],
        "Self-Diagnosis": secondresponse[5].split(':')[1].strip().split(' ')[0],
        "Self-Medication": secondresponse[6].split(':')[1].strip().split(' ')[0],
        "augmented": 0
        }
        

    return extracted_features
    


    

def get_mistral_response(prompt):
    
        # Replace with your Hugging Face API token
    HUGGING_FACE_API_TOKEN = os.getenv("Mistrale_Token")

    # The API endpoint for the Mistral model
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"

    #Limit to 1000 requests per day hence 1000 document per day 


    # Headers for authorization
    headers = {
        "Authorization": f"Bearer {HUGGING_FACE_API_TOKEN}"
    }

    # Data to send to the model
    data = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 256,
            "temperature": 0.7
        }
    }

    # Send the POST request
    response = requests.post(API_URL, headers=headers, json=data)

    # Check the response
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}, {response.text}")


#---------------Functions related to cleanning the data after LLM-------------------#


#----main functions----#

def clean_data(limit):
    print('starting cleanning data ')
    client = connect_to_mongo()
    if client is None:
        print("Error connecting to MongoDB")
        return False
    db_staging=client['Staging_db']
    db_production=client['Production_db']
    
    # get the posts that are not cleaned yet
    documents=db_staging.reddit_llm.find({'augmented': 0}, {'_id': 0}).limit(limit)
    documents_df=pd.DataFrame(list(documents))
    
    # start clean the data
    documents_df=clean_df(documents_df)
    
    #now the data is cleaned so it will be stored in the production db
    db_production.posts.insert_many(documents_df.to_dict('records'))
    
    #update the staging db
    ids=documents_df['id'].tolist()
    for el in ids:
        db_staging.reddit_llm.update_one({'id': el}, {'$set': {'augmented': 1}})
    
    print('data cleaned and stored in the production db')    
   



#----helper functions----#


import datetime
import re
def get_month(datetime):
    return datetime.month

def get_year(datetime):
    return datetime.year

def get_utc_time(timestamp):
    # Convert timestamp to UTC datetime
    utc_time = datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S')
    return utc_time

def fix_gender_errors(text):
    text=clean_text(text)
    text=text.lower()
    
    if text.startswith('male'):
        return 'male'
    elif text.startswith('female'):
        return 'female'
    elif text in ['nonbinary']:
        return 'non-binary'
    else:
        return 'unknown'
    
    

def clean_text(text):
    # Remove punctuation and additional spaces
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
    return text.strip()  # Remove leading and trailing spaces





def clean_df(posts_registered_df):
    # fix binary values 
    list_col=['Mention of Solutions', 'Personal_Experience', 'Self-Diagnosis',
       'Self-Medication', 'Topic']
    for col in list_col:
        posts_registered_df[col] = posts_registered_df[col].apply(lambda x: 1 if x.lower() == 'yes' else 0)
    # fix Gender values into 'male', 'female' or 'null'
    posts_registered_df['Gender'] = posts_registered_df['Gender'].apply(fix_gender_errors)
    
    # fix the date format
    posts_registered_df['created_at']=posts_registered_df['created_at'].apply(get_utc_time)
    
    # keep the necessary columns
    list_col_porduction=['id', 'created_at', 'Gender','Self-Diagnosis',
       'Self-Medication','Sentiment','self_text','author']
    
    posts_registered_df=posts_registered_df[list_col_porduction]
    posts_registered_df.rename(columns={'self_text':'Text'}, inplace=True)
    posts_registered_df['Sentiment'] = posts_registered_df['Sentiment'].apply(lambda x: x.lower())
    
    posts_registered_df.rename(columns={'author':'Author'}, inplace=True)
    posts_registered_df['Author'] = 'u/' + posts_registered_df['Author']
    
    # add the source 
    posts_registered_df['Source'] = 'Reddit'
    
    return posts_registered_df


    


    
    