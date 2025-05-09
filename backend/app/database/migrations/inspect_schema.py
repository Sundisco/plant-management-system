from sqlalchemy import create_engine, text
from app.core.config import settings

def inspect_schema():
    # Use your local database URL
    local_engine = create_engine("postgresql://postgres:your_password@localhost/plant_management")
    
    with local_engine.connect() as conn:
        # Get plants table structure
        result = conn.execute(text("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'plants'
            ORDER BY ordinal_position;
        """))
        
        print("\nPlants table structure:")
        for row in result:
            print(f"Column: {row[0]}, Type: {row[1]}")
        
        # Get a sample row to see all columns
        result = conn.execute(text("SELECT * FROM plants LIMIT 1"))
        if result.rowcount > 0:
            row = result.fetchone()
            print("\nSample row columns:")
            for key in row.keys():
                print(f"Column: {key}")

if __name__ == "__main__":
    inspect_schema() 