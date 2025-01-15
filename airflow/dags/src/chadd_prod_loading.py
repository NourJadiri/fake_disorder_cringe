from pymongo import MongoClient


def check_staging_db():
    try:
        client = MongoClient('mongo', 27017)
        db = client['chadd_staging_db']
        post_collection = db['posts']
        members_collection = db['members']
        print("Connected to MongoDB successfully.")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")

    post_count = post_collection.count_documents({})
    members_count = members_collection.count_documents({})
    if post_count > 0 and members_count > 0:
        return True
    else:
        return False

def load_posts_to_prod_db():
    try:
        client = MongoClient('mongo', 27017)
        db = client['chadd_staging_db']
        post_collection = db['posts']
        members_collection = db['members']
        print("Connected to MongoDB successfully.")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return "Failed to connect to MongoDB."

    try:
        # Connect to the production database
        prod_db = client['chadd_production_db']
        prod_post_collection = prod_db['posts']


        # Migrate and modify posts
        posts = post_collection.find({})

        modified_posts = []
        for post in posts:
            author = members_collection.find_one({'author_id': post['author']['author_id']})
            author_username = f'ch/{author["username"]}'
            modified_post = {
                'id': post['post_id'],
                'created_at': post['date_created'],
                'Author': author_username,
                'Gender': author['gender'],
                'Self-Diagnosis': 1 if post['self-diagnosed'] == 'Yes' else 0,
                'Self-Medication': 1 if post['self-medicated'] == 'Yes' else 0,
                'Sentiment': post['sentiment'],
                'Text': post['body'],
                'Source': 'HealthUnlocked',
            }
            modified_posts.append(modified_post)

        if modified_posts:
            try:
                prod_post_collection.insert_many(modified_posts, ordered=False)
            except Exception as e:
                print(f"Error during migration: {e}")

        print(f"{len(modified_posts)} posts migrated successfully.")
    except Exception as e:
        print(f"Error during migration: {e}")


def load_members_to_prod_db():
    try:
        client = MongoClient('mongo', 27017)
        db = client['chadd_staging_db']
        members_collection = db['members']
        print("Connected to MongoDB successfully.")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return "Failed to connect to MongoDB."

    try:
        # Connect to the production database
        prod_db = client['chadd_production_db']
        prod_members_collection = prod_db['members']

        members_count = members_collection.count_documents({})
        print(f"Found {members_count} members in the staging database.")

        if members_count > 0:
            members = members_collection.find({})
            prod_members_collection.insert_many(members, ordered=False)
            print(f"{members_count} members migrated successfully.")
        else:
            print("No members found in the staging database.")

    except Exception as e:
        print(f"Error during migration: {e}")


def clean_prod_db():
    try:
        client = MongoClient('mongo', 27017)
        db = client['chadd_production_db']
        db.drop_collection('posts')
        db.drop_collection('members')
        print("Production database cleaned successfully.")
    except Exception as e:
        print(f"Error cleaning production database: {e}")
