from sqlalchemy import create_engine, text
from app.core.config import settings
import os
from dotenv import load_dotenv

def transfer_data():
    # Load environment variables
    load_dotenv()
    
    # Local database connection - using the same configuration as the backend
    local_db_url = settings.DATABASE_URL
    local_engine = create_engine(local_db_url)
    
    # Render database connection - using the Render database URL
    if not settings.RENDER_DATABASE_URL:
        raise ValueError("RENDER_DATABASE_URL environment variable is not set")
    
    render_engine = create_engine(settings.RENDER_DATABASE_URL)
    
    print("Starting data transfer...")
    print(f"Local DB URL: {local_db_url}")
    print(f"Render DB URL: {settings.RENDER_DATABASE_URL}")
    
    try:
        with local_engine.connect() as local_conn, render_engine.connect() as render_conn:
            print("Connected to both databases")
            
            # Drop existing tables in reverse order of dependencies
            render_conn.execute(text("DROP TABLE IF EXISTS user_plants CASCADE;"))
            render_conn.execute(text("DROP TABLE IF EXISTS plants CASCADE;"))
            render_conn.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
            print("Dropped existing tables")
            
            # Create users table
            render_conn.execute(text("""
                CREATE TABLE users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    hashed_password VARCHAR(255) NOT NULL
                );
            """))
            print("Users table created")
            
            # Create plants table
            render_conn.execute(text("""
                CREATE TABLE plants (
                    id SERIAL PRIMARY KEY,
                    common_name VARCHAR(255) NOT NULL,
                    scientific_name VARCHAR(255),
                    other_names TEXT,
                    family VARCHAR(255),
                    type VARCHAR(255),
                    description TEXT,
                    growth_rate VARCHAR(255),
                    maintenance VARCHAR(255),
                    hardiness_zone VARCHAR(255),
                    image_url TEXT,
                    cycle VARCHAR(255),
                    watering VARCHAR(255),
                    is_evergreen BOOLEAN,
                    edible_fruit BOOLEAN
                );
            """))
            print("Plants table created")
            
            # Create user_plants table
            render_conn.execute(text("""
                CREATE TABLE user_plants (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    plant_id INTEGER REFERENCES plants(id),
                    section VARCHAR(255)
                );
            """))
            print("User_plants table created")
            
            # First, ensure we have the default user in Render
            render_conn.execute(text("""
                INSERT INTO users (id, email, hashed_password)
                VALUES (1, 'default@example.com', 'temporary_hashed_password')
                ON CONFLICT (id) DO NOTHING;
            """))
            print("Default user created/verified")
            
            # Get plants from local database
            plants = local_conn.execute(text("""
                SELECT 
                    common_name, scientific_name, other_names, family, type,
                    description, growth_rate, maintenance, hardiness_zone,
                    image_url, cycle, watering, is_evergreen, edible_fruit
                FROM plants;
            """)).fetchall()
            
            print(f"Found {len(plants)} plants to transfer")
            
            # Insert plants into Render database
            for plant in plants:
                # Convert Row object to dictionary
                plant_dict = {
                    'common_name': plant.common_name,
                    'scientific_name': plant.scientific_name,
                    'other_names': plant.other_names,
                    'family': plant.family,
                    'type': plant.type,
                    'description': plant.description,
                    'growth_rate': plant.growth_rate,
                    'maintenance': plant.maintenance,
                    'hardiness_zone': plant.hardiness_zone,
                    'image_url': plant.image_url,
                    'cycle': plant.cycle,
                    'watering': plant.watering,
                    'is_evergreen': plant.is_evergreen,
                    'edible_fruit': plant.edible_fruit
                }
                
                render_conn.execute(text("""
                    INSERT INTO plants (
                        common_name, scientific_name, other_names, family, type,
                        description, growth_rate, maintenance, hardiness_zone,
                        image_url, cycle, watering, is_evergreen, edible_fruit
                    ) VALUES (
                        :common_name, :scientific_name, :other_names, :family, :type,
                        :description, :growth_rate, :maintenance, :hardiness_zone,
                        :image_url, :cycle, :watering, :is_evergreen, :edible_fruit
                    );
                """), plant_dict)
            
            print("Plants transferred successfully")
            
            # Get user_plants from local database
            user_plants = local_conn.execute(text("""
                SELECT user_id, plant_id, section
                FROM user_plants;
            """)).fetchall()
            
            print(f"Found {len(user_plants)} user-plant relationships to transfer")
            
            # Insert user_plants into Render database
            for user_plant in user_plants:
                user_plant_dict = {
                    'user_id': user_plant.user_id,
                    'plant_id': user_plant.plant_id,
                    'section': user_plant.section
                }
                render_conn.execute(text("""
                    INSERT INTO user_plants (user_id, plant_id, section)
                    VALUES (:user_id, :plant_id, :section);
                """), user_plant_dict)
            
            render_conn.commit()
            print("Data transfer completed successfully!")
            
    except Exception as e:
        print(f"Error during data transfer: {str(e)}")
        raise

if __name__ == "__main__":
    transfer_data() 