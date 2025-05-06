from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.services import pruning as pruning_service
from app.schemas.pruning import Pruning as PruningSchema, PruningCreate
from app.database import get_db
from sqlalchemy import and_
from app.models.user_plants import UserPlant
from app.models.plants import Plant
from app.models.pruning import Pruning

router = APIRouter()

@router.post("/", response_model=PruningSchema)
def create_pruning(pruning: PruningCreate, db: Session = Depends(get_db)):
    return pruning_service.create_pruning(db, pruning)

@router.get("/current-pruning", response_model=dict)
async def get_current_pruning(db: Session = Depends(get_db)):
    try:
        # Get all pruning data with plant names
        pruning_data = (
            db.query(Pruning, Plant.common_name, UserPlant.section)
            .join(Plant, Pruning.plant_id == Plant.id)
            .join(UserPlant, and_(
                UserPlant.plant_id == Plant.id,
                UserPlant.user_id == 1
            ))
            .all()
        )

        result = [{
            'plant_id': p.Pruning.plant_id,
            'name': p.common_name,
            'section': p.section,
            'months': p.Pruning.months
        } for p in pruning_data]

        print("\nCurrent pruning data:", result)
        return {"pruning_data": result}
    except Exception as e:
        print(f"Error getting current pruning: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{pruning_id}", response_model=PruningSchema)
def read_pruning(pruning_id: int, db: Session = Depends(get_db)):
    db_pruning = pruning_service.get_pruning(db, pruning_id)
    if db_pruning is None:
        raise HTTPException(status_code=404, detail="Pruning not found")
    return db_pruning

@router.get("/plant/{plant_id}", response_model=PruningSchema)
def read_plant_pruning(plant_id: int, db: Session = Depends(get_db)):
    db_pruning = pruning_service.get_plant_pruning(db, plant_id)
    if db_pruning is None:
        raise HTTPException(status_code=404, detail="Pruning not found for this plant")
    return db_pruning

@router.put("/{pruning_id}", response_model=PruningSchema)
def update_pruning(pruning_id: int, pruning: PruningCreate, db: Session = Depends(get_db)):
    db_pruning = pruning_service.update_pruning(db, pruning_id, pruning)
    if db_pruning is None:
        raise HTTPException(status_code=404, detail="Pruning not found")
    return db_pruning

@router.delete("/{pruning_id}")
def delete_pruning(pruning_id: int, db: Session = Depends(get_db)):
    if not pruning_service.delete_pruning(db, pruning_id):
        raise HTTPException(status_code=404, detail="Pruning not found")
    return {"message": "Pruning deleted successfully"}

@router.get("/schedule/{user_id}")
async def get_pruning_schedule(user_id: int, db: Session = Depends(get_db)):
    try:
        print("\n=== DEBUG: Pruning Schedule Data Flow ===")
        
        # Month name to number mapping
        month_to_number = {
            'January': '1',
            'February': '2',
            'March': '3',
            'April': '4',
            'May': '5',
            'June': '6',
            'July': '7',
            'August': '8',
            'September': '9',
            'October': '10',
            'November': '11',
            'December': '12'
        }

        # 1. Check user plants with sections
        user_plants_with_sections = (
            db.query(UserPlant)
            .filter(
                UserPlant.user_id == user_id,
                UserPlant.section.isnot(None)
            )
            .all()
        )
        print(f"\n1. User plants with sections: {[{
            'plant_id': up.plant_id,
            'section': up.section
        } for up in user_plants_with_sections]}")

        if not user_plants_with_sections:
            print("No plants with sections found!")
            return {"pruning_schedule": []}

        # 2. Get pruning data
        plant_ids = [up.plant_id for up in user_plants_with_sections]
        pruning_records = (
            db.query(Pruning)
            .filter(Pruning.plant_id.in_(plant_ids))
            .all()
        )
        print(f"\n2. Pruning records found: {[{
            'plant_id': p.plant_id,
            'months': p.months
        } for p in pruning_records]}")

        # 3. Get plant names
        plants = (
            db.query(Plant)
            .filter(Plant.id.in_(plant_ids))
            .all()
        )
        plant_names = {p.id: p.common_name for p in plants}
        print(f"\n3. Plant names: {plant_names}")

        # 4. Process data by section
        schedule_data = {}
        plant_details = {}

        # Create section mapping
        section_plant_map = {up.section: [] for up in user_plants_with_sections}
        for up in user_plants_with_sections:
            section_plant_map[up.section].append(up.plant_id)
        
        print(f"\n4. Section to plant mapping: {section_plant_map}")

        # Process each section
        for section, plant_list in section_plant_map.items():
            schedule_data[section] = {}
            plant_details[section] = {}
            
            for pruning in pruning_records:
                if pruning.plant_id in plant_list:
                    print(f"\nProcessing plant {pruning.plant_id} in section {section}")
                    print(f"Original months: {pruning.months}")
                    
                    # Convert month names to numbers
                    month_numbers = [month_to_number[month] for month in pruning.months]
                    print(f"Converted to numbers: {month_numbers}")
                    
                    for month_num in month_numbers:
                        if month_num not in schedule_data[section]:
                            schedule_data[section][month_num] = 0
                            plant_details[section][month_num] = []
                        
                        schedule_data[section][month_num] += 1
                        plant_details[section][month_num].append({
                            "id": pruning.plant_id,
                            "name": plant_names.get(pruning.plant_id, "Unknown Plant")
                        })

        # 5. Format final result
        result = []
        for section in section_plant_map.keys():
            if schedule_data[section]:  # Only include sections with pruning data
                section_data = {
                    "section": section,
                    "months": schedule_data[section],
                    "details": plant_details[section]
                }
                result.append(section_data)

        print("\n5. Final result:", result)
        return {"pruning_schedule": result}

    except Exception as e:
        print(f"Error in get_pruning_schedule: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clean-pruning-data")
async def clean_pruning_data(db: Session = Depends(get_db)):
    try:
        print("\n=== Cleaning pruning data ===")
        
        # Get all pruning records
        pruning_records = db.query(Pruning).all()
        
        for record in pruning_records:
            print(f"\nChecking Plant ID: {record.plant_id}")
            print(f"Original months: {record.months}")
            
            # Remove duplicates while preserving order
            unique_months = []
            seen = set()
            for month in record.months:
                if month not in seen:
                    unique_months.append(month)
                    seen.add(month)
            
            if len(unique_months) != len(record.months):
                print(f"Found duplicates. Updating to: {unique_months}")
                record.months = unique_months
                db.add(record)
            else:
                print("No duplicates found")

        db.commit()
        return {"message": "Pruning data cleaned successfully"}
    except Exception as e:
        print(f"Error cleaning pruning data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-data")
async def create_test_pruning_data(db: Session = Depends(get_db)):
    try:
        print("\n=== Creating test pruning data ===")
        
        # Get all plants in user's garden that have sections
        user_plants = db.query(UserPlant).filter(
            UserPlant.user_id == 1,
            UserPlant.section.isnot(None)
        ).all()
        
        print(f"\nFound {len(user_plants)} plants with sections")
        
        created_data = []
        for user_plant in user_plants:
            # Check if pruning data already exists
            existing = db.query(Pruning).filter(Pruning.plant_id == user_plant.plant_id).first()
            
            # Create unique months based on plant ID
            base_months = [
                ['3', '6', '9', '12'],  # Default quarterly
                ['1', '4', '7', '10'],  # Alternate quarterly
                ['2', '5', '8', '11'],  # Another alternate quarterly
            ]
            
            months = base_months[len(created_data) % 3]
            
            if existing:
                print(f"Updating existing pruning data for plant {user_plant.plant_id}")
                existing.months = months
                db.add(existing)
            else:
                print(f"Creating new pruning data for plant {user_plant.plant_id}")
                pruning = Pruning(
                    plant_id=user_plant.plant_id,
                    frequency=2,
                    months=months,
                    interval='Quarterly'
                )
                db.add(pruning)
            
            created_data.append({
                'plant_id': user_plant.plant_id,
                'section': user_plant.section,
                'months': months
            })

        db.commit()
        print("\nCreated/updated pruning data:", created_data)
        return {"message": f"Pruning data updated for plants: {created_data}"}
    except Exception as e:
        print(f"Error creating test data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/setup-garden-pruning")
async def setup_garden_pruning(db: Session = Depends(get_db)):
    try:
        print("\n=== Setting up pruning schedules for garden plants ===")
        
        # Get all plants in user's garden that have sections
        user_plants = (
            db.query(UserPlant, Plant)
            .join(Plant, UserPlant.plant_id == Plant.id)
            .filter(
                UserPlant.user_id == 1,
                UserPlant.section.isnot(None)
            )
            .all()
        )
        
        print(f"\nFound {len(user_plants)} plants with sections")
        
        # Define pruning schedules based on plant type
        pruning_schedules = {
            'tree': ['3', '6', '9'],  # Trees: Spring, Summer, Fall
            'shrub': ['2', '5', '8', '11'],  # Shrubs: Every 3 months
            'flower': ['4', '7', '10'],  # Flowers: Spring, Summer, Fall
            'herb': ['3', '6', '9', '12'],  # Herbs: Quarterly
            'vegetable': ['5', '8'],  # Vegetables: Growing season
            'fruit': ['2', '6', '10'],  # Fruit: Before bloom, after fruit, winter prep
            'default': ['3', '9']  # Default: Spring and Fall
        }

        updated_data = []
        for user_plant, plant in user_plants:
            print(f"\nProcessing plant: {plant.common_name} (Type: {plant.type})")
            print(f"Section: {user_plant.section}")
            
            # Determine pruning schedule based on plant type
            plant_type = plant.type.lower() if plant.type else 'default'
            months = pruning_schedules.get(plant_type, pruning_schedules['default'])
            
            # Check if pruning data already exists
            existing = db.query(Pruning).filter(Pruning.plant_id == plant.id).first()
            
            if existing:
                print(f"Updating existing pruning schedule")
                existing.months = months
                existing.frequency = len(months)
                existing.interval = 'Variable'
                db.add(existing)
            else:
                print(f"Creating new pruning schedule")
                pruning = Pruning(
                    plant_id=plant.id,
                    frequency=len(months),
                    months=months,
                    interval='Variable'
                )
                db.add(pruning)
            
            updated_data.append({
                'plant_id': plant.id,
                'name': plant.common_name,
                'type': plant.type,
                'section': user_plant.section,
                'months': months
            })

        db.commit()
        print("\nUpdated pruning schedules:", updated_data)
        return {
            "message": "Pruning schedules updated for garden plants",
            "updated_plants": updated_data
        }
    except Exception as e:
        print(f"Error setting up pruning schedules: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/standardize-months")
async def standardize_month_formats(db: Session = Depends(get_db)):
    try:
        # Number to month name mapping
        number_to_month = {
            '1': 'January',
            '2': 'February',
            '3': 'March',
            '4': 'April',
            '5': 'May',
            '6': 'June',
            '7': 'July',
            '8': 'August',
            '9': 'September',
            '10': 'October',
            '11': 'November',
            '12': 'December'
        }

        # Get all pruning records
        pruning_records = db.query(Pruning).all()
        
        print("\n=== Standardizing month formats ===")
        updates = []
        
        for record in pruning_records:
            print(f"\nProcessing plant ID: {record.plant_id}")
            print(f"Original months: {record.months}")
            
            # Convert any numeric months to full month names
            new_months = [
                number_to_month.get(month, month) 
                for month in record.months
            ]
            
            if new_months != record.months:
                print(f"Updating to: {new_months}")
                record.months = new_months
                db.add(record)
                updates.append({
                    'plant_id': record.plant_id,
                    'old_months': record.months,
                    'new_months': new_months
                })
            else:
                print("No changes needed")

        db.commit()
        return {
            "message": "Month formats standardized",
            "updates": updates
        }
    except Exception as e:
        print(f"Error standardizing months: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
