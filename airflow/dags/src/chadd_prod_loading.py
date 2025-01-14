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
        print("Connected to MongoDB successfully.")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return "Failed to connect to MongoDB."

    try:
        # Connect to the production database
        prod_db = client['chadd_production_db']
        prod_post_collection = prod_db['posts']

        # Migrate and modify posts
        posts = post_collection.find({}, {
            'post_id': 1, 'title': 1, 'body': 1, 'author': 1,
            'date_created': 1, 'total_responses': 1, 'responses': 1,
            'sentiment': 1, 'self-diagnosed': 1, 'self-medicated': 1
        })

        modified_posts = []
        for post in posts:
            post['source'] = 'chadd'  # Add the new field
            modified_posts.append(post)

        if modified_posts:
            prod_post_collection.insert_many(modified_posts)
        print(f"{len(modified_posts)} posts migrated successfully.")

        return "Migration completed successfully."
    except Exception as e:
        print(f"Error during migration: {e}")
        return "Migration failed."

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
            prod_members_collection.insert_many(members)
            print(f"{members_count} members migrated successfully.")
        else:
            print("No members found in the staging database.")

    except Exception as e:
        print(f"Error during migration: {e}")
