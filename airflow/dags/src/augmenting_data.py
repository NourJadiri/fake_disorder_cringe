import os
from dotenv import load_dotenv
import praw
import redis
from pymongo import MongoClient, errors

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
            db_ingestion.reddit_ingestion.update_one({'id': id}, {'$set': {'staged': -1}})
            print(f"Updated document with id: {id}")
        except Exception as e:
            log_errors.append({'id': id,'text':response_mistrale, 'error': e})
            print(f"Error processing document with id: {id}")
            print(e)
            error_nb+=1
        
    print(f"error recorded: {error_nb}/{total}= {(error_nb/total)*100}")
    print(f"error answer recorded: {answer_nb}/{total}= {(answer_nb/total)*100}")
    df=pd.DataFrame(log_errors)
    print(df)
    print("Current working directory:", os.getcwd())
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
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
    documents = db[collection].find({'staged': 1}, {'_id': 0}).limit(limit)
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


# __name__ = '__main__'
# augment_documents(2)x