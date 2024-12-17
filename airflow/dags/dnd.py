import airflow
import datetime
import requests
import pandas as pd
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.postgres_operator import PostgresOperator
import os

default_args_dict = {
    'start_date': airflow.utils.dates.days_ago(0),
    'concurrency': 1,
    'schedule_interval': '0 0 * * 0-4',
    'retries': 0,
    'retry_delay': datetime.timedelta(minutes=5),
}

dnd_dag = DAG(
    dag_id='dnd_dag',
    default_args=default_args_dict,
    catchup=False,
)

#----------------------
#Start of functions
#----------------------


def cleanup_task():
    # Only clean up if it's Monday
    if datetime.today().weekday() == 0:  # Monday is represented by 0
        print("Cleaning up values from the previous week...")
    else:
        return

def create_jsonFile(character,indent,file):
    import json
    json_string = json.dumps(character, indent=indent)
    with open(file, 'w') as json_file:
        json_file.write(json_string)
    
def open_jsonFile(file):
    import json
    with open(file) as json_file:
        data = json.load(json_file)
        return (data)


def init_character():
    import random
    import json
    from faker import Faker
    import pandas as pd
    name=Faker().name()
    attributes=[]
    level=random.randint(1,4)
    for i in range(6):
        attributes.append(random.randint(2,18))
    attributes=attributes
    character={
        'name':name,
        'level':level,
        'attributes':attributes
    }
    
    create_jsonFile(character,len(character),'/opt/airflow/dags/charactor.json')
    

def fetch_dnd(url):
    import pandas as pd
    import requests
    headers = {'Accept': 'application/json'}
    response=requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data['count']<=0:
            return None
        data=data['results']
        #print(data)
        df=pd.DataFrame(data)
        df.drop(['url'],axis=1,inplace=True)
        return df
        #df.to_csv(outputfile)

def create_character():
    import random
    import pandas as pd
    stdUrl="https://www.dnd5eapi.co/api/"
    character=open_jsonFile('/opt/airflow/dags/charactor.json')
    classes=fetch_dnd(str(stdUrl+'classes'))
    races=fetch_dnd(str(stdUrl+'races'))
    languages=fetch_dnd(str(stdUrl+'languages'))   

    race=races.iloc[[random.randint(0,len(races)-1)]]
    race=race.iloc[0,0]
    classe=classes.iloc[[random.randint(0,len(classes)-1)]]['index']
    classe=classe.iloc[0]
    language=languages.iloc[[random.randint(0,len(languages)-1)]]['index']
    language=language.iloc[0]
    
    character['race']=race
    character['classe']=classe
    character['language']=language

    create_jsonFile(character,len(character),'/opt/airflow/dags/charactor.json')


def finalize_character():
    import random
    import pandas as pd
    stdUrl="https://www.dnd5eapi.co/api/"
    character=open_jsonFile('/opt/airflow/dags/charactor.json')
    classe=character['classe']
    race=character['race']
    if classe=='fighter':
        character['spell']=None
    else:
        spells=fetch_dnd(str(stdUrl+'spells'))
        spells=spells[spells['level']<=2]
        spell=spells.iloc[[random.randint(0,len(spells)-1)]]['index']
        spell=spell.iloc[0]
        character['spell']=spell
    
    proficencies=fetch_dnd(str(stdUrl+'/races/:'+race+'/proficiencies'))
    proficiency=[]
    if proficencies:
        for i in range(len(proficencies)):
            proficiency.append(proficencies.iloc[i]['index'])
    else:
        proficiency=None
    
    character['proficiency']=proficiency
    create_jsonFile(character,len(character),'/opt/airflow/dags/charactor.json')

def create_character_query(file,outputfile):
    character=open_jsonFile(file)
    attributes=character['attributes']
    with open(outputfile, "w") as f:
        f.write(
            "CREATE TABLE IF NOT EXISTS DnDCharacter (\n"
            "name VARCHAR(255),\n"
            "race VARCHAR(255),\n"
            "attributes VARCHAR(255),\n"
            "languages VARCHAR(255),\n"
            "class VARCHAR(255),\n"
            "proficiency VARCHAR(255),\n"
            "level VARCHAR(255),\n"
            "spells VARCHAR(255)\n"
            ");\n"
        )
       
        f.write(
            "INSERT INTO DnDCharacter VALUES ("
            f"'{character['name']}',"
            f"'{character['race']}',"
        #)
        # f.write(
        #     "'"
        # )
        # for i in range(0,len(attributes)):
        #     if(i==len(attributes)-1):
        #          f.write(
        #             f"{attributes[i]}"
        #         )
        #     else:
        #         f.write(
        #         f"{attributes[i]},"
        #         )
        # f.write(
        #     f"',"
        # )
            f"'{attributes}',"
            f"'{character['language']}',"
            f"'{character['classe']}',"
        )
        if character['proficiency']:
            f.write(
                f"'{character['proficiency']}',"
           )
        else:
              f.write(
                f"NULL,"
           )
        f.write(
            f"'{character['level']}',"
        )
        if character['spell']:
            f.write(
            f"'{character['spell']}'"
            )
        else:
            f.write(
            f"NULL"
           )
        f.write(
            ");\n"
        )
#----------------------
#End of functions
#----------------------

#----------------------
#Start of tasks
#----------------------


task_zero = BashOperator(
    task_id='delete_from_postgres',
    bash_command="""
    if [ "$(date +\%u)" -eq 7 ] && [ "$(date +\%H:\%M)" = "00:00" ]; then
        psql "host=localhost dbname=airflow user=airflow password=airflow" -c "DELETE FROM DnDCharacter;"
    else
        echo "Not Monday midnight, skipping task."
    fi
    """
)



task_zero= BashOperator(
    task_id='cleanup_task',
    dag=dnd_dag,
    bash_command='echo "Cleanup task"',
)




task_one = PythonOperator(
    task_id='init_character',
    dag=dnd_dag,
    python_callable=init_character,
    trigger_rule='all_success', 
    depends_on_past=False,
)



task_Two = PythonOperator(
    task_id='create_character',
    dag=dnd_dag,
    python_callable=create_character,
    trigger_rule='all_success', 
    depends_on_past=False,
)


task_Three = PythonOperator(
    task_id='finalize_character',
    dag=dnd_dag,
    python_callable=finalize_character,
    trigger_rule='all_success', 
    depends_on_past=False,
)


task_Four = PythonOperator(
    task_id='create_character_query',
    dag=dnd_dag,
    python_callable=create_character_query,
    op_kwargs={
        "file": "/opt/airflow/dags/charactor.json",
        "outputfile":"/opt/airflow/dags/query.sql"
        },
    trigger_rule='all_success', 
    depends_on_past=False,
)

task_Five = PostgresOperator(
    task_id='insert_Character_query',
    dag=dnd_dag,
    postgres_conn_id='postgres_default',
    sql='query.sql',
    trigger_rule='all_success',
    autocommit=True
)

task_Six = BashOperator(
    task_id='cleanup',
    dag=dnd_dag,
    bash_command='rm /opt/airflow/dags/charactor.json /opt/airflow/dags/query.sql',
    trigger_rule='all_success'
)


#----------------------
#End of tasks
#----------------------

#----------------------
#Task Dependencies
#----------------------

task_zero >> task_one >> task_Two >> task_Three >> task_Four >> task_Five >> task_Six