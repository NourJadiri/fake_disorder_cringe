# DataEng 2024 Template Repository

![Insalogo](./images/logo-insa_0.png)

Project [DATA Engineering](https://www.riccardotommasini.com/courses/dataeng-insa-ot/) is provided by [INSA Lyon](https://www.insa-lyon.fr/).

Students: **Youssef Sidhom, Nour Eljadiri**

### Abstract

Since 2018, awareness of mental health issues like ADHD has grown, influenced by social media trends on platforms like **Reddit** or even specialised website such as **HealthUnlocked**. This project will explore whether rising diagnosis rates align with increased social media discussions or if social media is reacting to these rates. Additionally, we will investigate the demographics of those medically diagnosed and self-diagnosed.

A major focus is to compare the rates of self-diagnosis with formal diagnoses.

## Datasets Description

The datasets for this project include:

* **Posts from Reddit** : Reddit is a social media platform and online community where users can share, discuss, and vote on content in the form of posts, links, images, and videos. Organized into thousands of user-created forums called "subreddits," each dedicated to specific topics or interests, Reddit fosters diverse discussions on everything from news and technology to niche hobbies and personal experiences. Content is ranked based on user upvotes and downvotes, and its open, anonymous format encourages both knowledge sharing and community engagement.







* **Posts from HealthUnlocked** : HealthUnlocked is a global online health community platform that connects individuals with shared health concerns, enabling them to seek advice, share experiences, and access relevant resources. It operates through condition-specific forums or communities where users can discuss topics ranging from chronic illnesses to mental health conditions.

  Key features include:
  
  * Community-Based Support: Users can join specific communities tailored to their health conditions (e.g., ADHD, diabetes, cancer) and interact with others facing similar challenges.
  Resource Sharing: Members and moderators often share valuable resources, including articles, research findings, and links to professional advice.
  * Collaboration with Healthcare Organizations: HealthUnlocked partners with healthcare organizations, charities, and patient advocacy groups to provide credible information and moderate discussions.
  * Anonymous Interaction: Users can participate anonymously, fostering open and honest communication without fear of stigma.
  For this project, HealthUnlocked was used exclusively to study discussions about ADHD within the Adult ADHD community. This community focuses on the experiences, challenges, and treatment options for adults living with ADHD. Data collected from this source provided insights into demographics, sentiment trends, and key topics such as self-diagnosis and self-medication, contributing to a deeper understanding of how ADHD is perceived and discussed online.



## Queries

### Assessing the Population Diagnosed with ADHD in Comparison with Social Media Mentions to Underline a Potential Link

*Objective:* To explore the potential correlation between formal ADHD diagnoses and the frequency of ADHD mentions on social media platforms.

Questions:

1. Annual Comparison:

* Detect the rise of adhd mentions in social media


2. Demographic Breakdown:

* What are the demographic profiles (age groups and gender) of individuals diagnosed with ADHD compared to those frequently discussing ADHD on social media?

    *Do certain demographics show a stronger correlation between diagnosis rates and social media mentions?*

4. Monthly Trends and Spikes:

* Are there specific months or seasons where spikes in ADHD diagnoses align with increased mentions of ADHD on social media platforms?

    *Could external factors (like awareness campaigns or events) be influencing these spikes?*

### Understanding the Trend of #self-diagnosis and #self-medication in the ADHD Context on Social Media

*Objective:* To analyze the prevalence and growth of the hashtags #self-diagnosis and #self-medication related to ADHD on social media platforms, and understand their implications.

Questions:

1. Trend Over Time:

* How has the number of social media posts containing the hashtags #self-diagnosis and #self-medication in the context of ADHD changed over time (e.g., monthly or yearly)?

    *Is there a significant increase or decrease in these mentions, and what might be influencing these trends?*

2. Proportion of Total Mentions:

* What percentage of all ADHD-related social media posts include references to self-diagnosis or self-medication?

    *How has this proportion evolved over time, and what does it suggest about changing attitudes or behaviors?*

3. Geographic Distribution:

* Which regions or countries have the highest number of social media mentions of #self-diagnosis and #self-medication related to ADHD?

    *Are there cultural, societal, or healthcare factors that might explain regional differences?*

4. Comparison with Professional Diagnoses Mentions:

* How do the trends in mentions of self-diagnosis compare to mentions of professional diagnoses on social media platforms?

    *Is there a shift in how people are discussing their ADHD diagnoses, and what might this indicate about trust in medical professionals or access to healthcare?*

## Requirements

This project requires will require quite some power from your machine, as it is running two lightweight llms in containers, so make sure you have enough memory and cpu to run the project.

Local models have been run in two distinct configuration, one with an AMD Ryzen 7 CPU, and a second one with an Intel Core 9 Ultra with GPU acceleration **(Nvidia RTX 4070)**

In case you doubt about your machine capabilities, it is better to run directly the migration script that will populate the databases with some data.

### 1. Prequirements:
* Make sure you have docker installed 


### 2. Clone the Repository

Start by cloning the repository to your local machine:

```bash
git clone https://https://github.com/NourJadiri/mental_health_disorders_analysis
```
### 3. Initiate the docker containers
Once the git cloned just go to the airflow directory and run docker compose up

```bash
# for linux users
cd airflow
docker compose up 
```
```bash
# for windows users
cd airflow
docker-compose up
```
### 4. Populate the databases for the offline use
In order to populate the databases for offline testing, make sure to run the migration-mongo.sh migration script from the host machine (Make sure the mongo container is running !!!)
This script with populate all the databases (Ingestion - Staging - Production).
```bash
cd dags/migration/mongo/
#migration of mongodb
sh dags/migration/mongo/migration_mongo.sh
#migration of redis
sh dags/migration/redis/migration_redis.sh
```

In case there is a need to run the migration for a specific database, you can run the following commands individually :
```bash
cd dags/migration/mongo/

# migration of ingestion_dbs
sh dags/migration/mongo/migration_ingestion_dbs.sh

# migration of staging_dbs
sh dags/migration/mongo/migration_staging_dbs.sh

# migration of production_db
sh dags/migration/mongo/migration_prod_db.sh
```

→ Now everything should be running

## Data Engineering 
* In the following section, we will outline the entire pipeline we implemented to collect and clean the data, preparing it for effective analysis.*


![Pipeline](./images/pipeline.png)


## Ingestion phase
We will be detailling for each source the steps used in order to scrap get data.
### Reddit:
1. **Scrape Reddit**: The Reddit API is queried to fetch posts from the **r/adhd** subreddit. The posts are filtered based on predefined keywords related to ADHD, such as **self_diagnosis**, **self_medication**, and **personal_experience**.

2. **Check Redis for Duplicates**: Each post’s unique **ID** is checked against **Redis** to ensure it hasn’t already been processed. If the post ID is found in Redis, it is skipped to prevent duplication in the database.

3. **Store in MongoDB**: If a post is new, it is processed and stored in **MongoDB**. 
<details>
    <summary>The data collected</summary>

- **Post ID**: The unique identifier for the Reddit post.
- **Post Score**: The score assigned to the post, indicating its popularity.
- **Post Comments**: The number of comments on the post, reflecting engagement.
- **Post Upvotes**: The number of upvotes the post received, showing approval.
- **Post URL**: The URL of the Reddit post, providing direct access.
- **Post Subreddit**: The subreddit to which the post belongs (currently only considering '/adhd').
- **Post Title**: The title of the Reddit post, summarizing its content.
- **Post Content**: The text content of the Reddit post, detailing the discussion.
- **Post Author**: The author of the Reddit post, identifying the contributor.
- **Timestamp**: The timestamp when the post was created, indicating its recency.
- **Keywords**: The keywords used in the search that led to the retrieval of the post, highlighting relevant terms.

</details>

### HealthUnlocked

1. **Scraping Post IDs**

We begin by scraping post IDs for the month using requests to the HealthUnlocked API. This allows us to gather the relevant posts for analysis based on specific ADHD-related discussions.

  * **Rate Limit Management:**
  The API is designed for private use and has rate limits that can restrict the number of requests sent in a given time frame. To handle this, our pipeline implements session rotation. After sending a predefined batch of requests (e.g., 50 or 100), the active session is replaced with a new one, using a fresh set of cookies or headers. This ensures that the pipeline operates seamlessly without triggering API limits or bans. Additionally, dynamic backoff strategies are employed to adapt to changes in API behavior, reducing the risk of disruptions.
  
  
  * **API Access Details:**
  Despite being a private API, the HealthUnlocked API is relatively open in its design:
  It only requires a single cookie for authentication, which can be obtained through initial browser sessions or automated tools.
  The absence of a CORS (Cross-Origin Resource Sharing) policy means requests can be made from any IP address, removing restrictions on origin domains. This makes the pipeline more flexible and easier to deploy across different machines or environments, such as cloud-based systems.


2. **Fetching Post Details and Author Information**

Next, we fetch the details of each post, including the title, body, and author information. we also collect any available author data, such as demographics, to enrich the dataset for deeper analysis.

3. **Storing in MongoDB**

Finally, all collected data, including post content, metadata, and author details, is stored in MongoDB for easy querying and efficient processing in subsequent analysis stages.


## Staging phase

### Reddit
Once the posts have been ingested into **MongoDB**, the next step involves moving the data into a **staging database** for augmentation. In this step, the text of the posts is passed to a **Large Language Model (LLM)**, such as **Mistral**, via an **API call** for further analysis and feature extraction. This allows us to enrich the collected data with additional insights that are valuable for analysis.

1. **Using Mistral for Data Augmentation**

To analyze Reddit posts and extract key features, we use the **Mistral** LLM through an API call. Mistral helps with tasks like sentiment analysis, keyword extraction, and other valuable insights to enrich the dataset.

2. **Cleaning Augemented data**

After receiving analysis results from Mistral, the system formats and stores the augmented data in the staging database, with Pandas used for cleaning and ensuring consistency. Due to variability in the LLM’s output, additional adjustments may be required, such as:

Parsing the model output: Cleaning the response to match the database structure.
Handling inconsistent responses: Adjusting missing labels or misinterpreted keywords through post-processing.

### HealthUnlocked:

In the staging phase, several data processing tasks are carried out to enrich the dataset using LLM (Large Language Model) agents. These models help extract and augment the raw data obtained from the ingestion phase, providing valuable insights that enhance the subsequent analysis. We implemented a setup leveraging three distinct Ollama 1B LLMs, each tailored to perform a specific task:

1. **Gender Inference from Biography:**

A dedicated LLM agent is employed to infer gender information based on user biographies.

Extensive prompt engineering was conducted to fine-tune the model and mitigate biases. For example, during early trials, the model incorrectly classified users with gaming-related keywords as male, regardless of other context. This issue was addressed by incorporating nuanced examples into the prompt and refining the input structure.

This process enriches the dataset with demographic information, allowing for more granular analysis.

2. **Sentiment Analysis:**

A second LLM agent classifies the emotional tone of each post into three categories: positive, negative, or neutral.
This helps provide insights into the emotional context of discussions surrounding ADHD, revealing potential patterns of user sentiment over time or across regions.

3. **Self-Diagnosis and Self-Medication Detection:**

A third LLM agent detects mentions of self-diagnosis or self-medication in posts, highlighting key concerns related to ADHD management and user behavior.
By analyzing these mentions, the dataset is enriched with indicators of potential trends, such as the increasing prevalence of self-diagnosis narratives on social media.

    Note: The staging pipeline for `chadd` is computationally intensive (LLM agents are run locally) and can be quite slow due to the nature of the API queries, duplicate checks, and data processing steps. 
    For testing purposes, it is recommended to run the migration script instead, as it populates the databases with preprocessed data much faster.


**Why Use Multiple LLMs?**

Each LLM is optimized for a specific task, ensuring high accuracy and minimizing cross-task interference.
This modular approach allows for easier debugging and scalability, as improvements in one LLM do not affect the others.

4. **Challenges and Mitigations:**

* **Biases in Predictions:** Heavy prompt engineering and iterative testing were necessary to reduce biases in tasks like gender inference.
* **Model Output Variability:** Additional post-processing steps using Pandas were applied to handle inconsistent outputs and ensure data alignment with the database schema.
### Production phase

Once all the data cleaned it is transfered to the prodcution_db ready for analysis.
The main work done here is to have a common db schema that will serve later for visualisation purposes.


