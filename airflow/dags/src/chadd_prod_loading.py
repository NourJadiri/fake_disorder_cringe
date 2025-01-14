from pymongo import MongoClient


def load_to_prod_db():
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
        prod_members_collection = prod_db['members']

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
        print("Posts migrated successfully.")

        # Migrate members as is
        members = members_collection.find()
        members_count = members_collection.count_documents({})
        if members_count > 0:
            prod_members_collection.insert_many(members)
        print("Members migrated successfully.")

        return "Migration completed successfully."
    except Exception as e:
        print(f"Error during migration: {e}")
        return "Migration failed."