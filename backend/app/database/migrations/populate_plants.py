from sqlalchemy import text
from app.database import engine
import json
import os

def populate_plants():
    with engine.connect() as conn:
        # Check if plants table is empty
        result = conn.execute(text("SELECT COUNT(*) FROM plants"))
        count = result.scalar()
        
        if count == 0:
            print("Populating plants table...")
            
            # Read plants data from JSON file
            plants_file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'plants.json')
            
            try:
                with open(plants_file, 'r', encoding='utf-8') as f:
                    plants_data = json.load(f)
                
                # Insert plants
                for plant in plants_data:
                    conn.execute(
                        text("""
                            INSERT INTO plants (
                                common_name, scientific_name, other_names, type,
                                image_url, description, growth_rate, maintenance,
                                hardiness_zone, cycle, watering, is_evergreen,
                                edible_fruit, attracts, sunlight
                            ) VALUES (
                                :common_name, :scientific_name, :other_names, :type,
                                :image_url, :description, :growth_rate, :maintenance,
                                :hardiness_zone, :cycle, :watering, :is_evergreen,
                                :edible_fruit, :attracts, :sunlight
                            )
                        """),
                        {
                            'common_name': plant.get('common_name'),
                            'scientific_name': plant.get('scientific_name', []),
                            'other_names': plant.get('other_names', []),
                            'type': plant.get('type'),
                            'image_url': plant.get('image_url'),
                            'description': plant.get('description'),
                            'growth_rate': plant.get('growth_rate'),
                            'maintenance': plant.get('maintenance'),
                            'hardiness_zone': plant.get('hardiness_zone'),
                            'cycle': plant.get('cycle'),
                            'watering': plant.get('watering'),
                            'is_evergreen': plant.get('is_evergreen', False),
                            'edible_fruit': plant.get('edible_fruit', False),
                            'attracts': plant.get('attracts', []),
                            'sunlight': plant.get('sunlight', [])
                        }
                    )
                
                conn.commit()
                print("Plants data populated successfully!")
                
            except FileNotFoundError:
                print("Error: plants.json file not found!")
            except json.JSONDecodeError:
                print("Error: Invalid JSON format in plants.json!")
            except Exception as e:
                print(f"Error populating plants data: {str(e)}")
        else:
            print("Plants table already has data. Skipping population.")

if __name__ == "__main__":
    populate_plants() 