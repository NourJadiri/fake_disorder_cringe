# Data Collection, Augmentation, and Ingestion Process for ADHD Reddit Posts Analysis

This document outlines the steps followed to collect, augment, and process Reddit posts related to **ADHD**. The data pipeline is fully automated using **Apache Airflow**, with the integration of **Reddit API**, **Redis**, **MongoDB**, and **Mistral LLM (via API)** for efficient data processing and enrichment.

The project aims to gather relevant Reddit posts from the **r/adhd** subreddit, analyze them using a large language model (LLM) for feature extraction, and augment the collected data with insights that will be useful for further analysis.

## 1. **Automated Data Collection Pipeline Using Airflow**

All tasks involved in data collection and processing are automated using **Apache Airflow**. The Airflow DAG (Directed Acyclic Graph) orchestrates the following sequence of tasks:

1. **Scrape Reddit**: The Reddit API is queried to fetch posts from the **r/adhd** subreddit. The posts are filtered based on predefined keywords related to ADHD, such as **self_diagnosis**, **self_medication**, and **personal_experience**.

2. **Check Redis for Duplicates**: Each post’s unique **ID** is checked against **Redis** to ensure it hasn’t already been processed. If the post ID is found in Redis, it is skipped to prevent duplication in the database.

3. **Store in MongoDB**: If a post is new, it is processed and stored in **MongoDB**. The post data includes:
   - **Post id**: The post id (id related to Reddit)
   - **Post Score**: The score of the post
   - **Post Comments**: The number of comments on the post
   - **Post Upvotes**: The number of upvotes the post recieved
   - **Post Url**
   - **Post Subreddit**: the subreddit to which the post belonged (for the moment only '/adhd' is considered)

   - **Post Title**: The title of the Reddit post.
   - **Post Content**: The text of the Reddit post.
   - **Post Author**: The author of the Reddit post.
   - **Timestamp**: The timestamp when the post was created.
   - **Keywords**: The keyword used in the search that led to the retrieval of the post.
 

## 2. **Data Augmentation and Enrichment**

Once the posts have been ingested into **MongoDB**, the next step involves moving the data into a **staging database** for augmentation. In this step, the text of the posts is passed to a **Large Language Model (LLM)**, such as **Mistral**, via an **API call** for further analysis and feature extraction. This allows us to enrich the collected data with additional insights that are valuable for analysis.

### 2.1 **Using Mistral for Data Augmentation**

To analyze the posts and extract interesting features, the **Mistral LLM** is used via an API call. The **Mistral** model can help extract various insights from the text, such as sentiment analysis, keyword extraction, and other important features that will enhance the richness of the dataset.

To access Mistral’s capabilities, we utilize **Hugging Face**, which provides free API access for up to **1,000 requests per day**. This free tier is a great resource for performing data augmentation without incurring costs in the initial stages of the project. You can learn more about Hugging Face’s API offerings [here](https://huggingface.co).

### 2.2 **Struggles in Automating LLM Analysis**

One of the key challenges encountered when automating the analysis of Reddit posts with an LLM is ensuring that the output is consistently structured in a usable format. **Mistral** or similar LLMs return responses that need to be formatted in a way that can be automatically parsed and integrated into the existing data pipeline.

In particular, improving the **prompting strategy** is crucial for ensuring that the LLM’s output aligns with the desired structure for data augmentation. The goal is to refine the prompt given to the model so that the response is in a structured, consistent format, making it easier to parse and extract useful features.

For instance, when asking the model to perform sentiment analysis, a well-structured prompt may look like:


The challenge is ensuring that the LLM responds in the correct format, where each feature is clearly identified and no extraneous text is included. If the LLM’s response is not in the desired format, manual intervention or additional parsing steps may be required to process the data.

### 2.3 **Automating the Data Augmentation Process**

After receiving the analysis results from **Mistral**, the system attempts to automatically format and store the augmented data into the staging database. However, due to the variability in the LLM’s output, some additional work may be needed to refine the results. For instance:

- **Parsing the model output**: The response may need to be cleaned and processed to match the structure required by the database.
- **Handling inconsistent responses**: Occasionally, the LLM may return answers in formats that need adjustment (e.g., missing sentiment labels or misinterpreted keywords). The response is adjusted through post-processing logic.

## 3. **Technologies Used**

### 3.1 **Reddit API**

The **Reddit API** is used to perform searches in the **r/adhd** subreddit based on predefined keywords related to ADHD, such as **self-diagnosis**, **self-medication**, and **personal experiences**. This allows for the collection of relevant posts that are further analyzed in later stages.

### 3.2 **Redis**

**Redis** is used to track processed post IDs and prevent duplicate posts from being ingested into the database. Each post ID is checked against Redis to ensure that it hasn’t been processed previously, improving data quality and efficiency.

### 3.3 **MongoDB**

**MongoDB** serves as the storage system for the collected Reddit posts. Each post is stored in MongoDB with relevant metadata, including the **post content**, **author**, **timestamp**, and **keywords**.

### 3.4 **Apache Airflow**

**Apache Airflow** is used to automate the entire data collection and ingestion pipeline, including querying Reddit, checking Redis for duplicates, storing the posts in MongoDB, and triggering data augmentation tasks.

### 3.5 **Mistral LLM via Hugging Face API**

The **Mistral LLM** is used for analyzing the text of the Reddit posts and extracting relevant features (such as sentiment, keywords, and mentions of self-diagnosis and self-medication). The Hugging Face platform provides access to the **Mistral model** through its API, with **1,000 free requests per day**. For more information, visit [Hugging Face](https://huggingface.co).

## 4. **Conclusion**

By utilizing **Apache Airflow**, **Reddit API**, **Redis**, **MongoDB**, and **Mistral LLM**, the project automates the process of collecting and enriching Reddit posts related to ADHD. The integration of Mistral’s capabilities enables the extraction of valuable features from Reddit posts, which are then stored in a staging database for further analysis. The free access to the Hugging Face API makes it an ideal solution for augmenting the dataset without additional costs in the initial stages of the project.

The challenges faced in automating the analysis of the LLM responses—such as improving the prompting strategy and ensuring structured output—are key areas of focus for improving the accuracy and efficiency of the data augmentation process.
