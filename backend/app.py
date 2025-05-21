from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@app.get("/api/plants/{plant_id}/attracts")
async def get_plant_attracts(plant_id: int):
    try:
        with SessionLocal() as session:
            result = session.execute(
                text("""
                    SELECT birds, butterflies, bees, hummingbirds, other_animals
                    FROM attracts
                    WHERE plant_id = :plant_id
                """),
                {"plant_id": plant_id}
            )
            attracts_data = result.fetchone()
            
            if attracts_data:
                data = dict(attracts_data._mapping)
                # Convert other_animals from string to list if it's stored as comma-separated values
                if data['other_animals']:
                    data['other_animals'] = [animal.strip() for animal in data['other_animals'].split(',')]
                else:
                    data['other_animals'] = []
                return data
            raise HTTPException(status_code=404, detail="No attracts data found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/plants/{plant_id}/sunlight")
async def get_plant_sunlight(plant_id: int):
    try:
        with SessionLocal() as session:
            result = session.execute(
                text("""
                    SELECT full_sun, partial_shade, full_shade, notes
                    FROM sunlight
                    WHERE plant_id = :plant_id
                """),
                {"plant_id": plant_id}
            )
            sunlight_data = result.fetchone()
            
            if sunlight_data:
                return dict(sunlight_data._mapping)
            raise HTTPException(status_code=404, detail="No sunlight data found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    port = int(os.getenv('PORT', 5000))
    uvicorn.run(app, host='0.0.0.0', port=port) 