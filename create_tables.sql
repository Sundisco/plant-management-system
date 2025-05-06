CREATE TABLE public.plants (
    id SERIAL PRIMARY KEY,
    common_name TEXT,
    scientific_name TEXT[],
    other_names TEXT[],
    family TEXT,
    type TEXT,
    description TEXT,
    growth_rate TEXT,
    maintenance TEXT,
    hardiness_zone TEXT,
    image_url TEXT,
    cycle TEXT,
    watering TEXT,
    is_evergreen BOOLEAN DEFAULT FALSE,
    edible_fruit BOOLEAN DEFAULT FALSE
);

CREATE TABLE public.users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE,
    password TEXT
);

CREATE TABLE public.user_plants (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    plant_id INTEGER REFERENCES plants(id) ON DELETE CASCADE,
    section TEXT
);

CREATE TABLE public.attracts (
    id SERIAL PRIMARY KEY,
    plant_id INTEGER REFERENCES plants(id) ON DELETE CASCADE,
    birds BOOLEAN,
    butterflies BOOLEAN,
    bees BOOLEAN,
    hummingbirds BOOLEAN,
    other_animals TEXT
);

CREATE TABLE public.sunlight (
    id SERIAL PRIMARY KEY,
    plant_id INTEGER REFERENCES plants(id) ON DELETE CASCADE,
    full_sun BOOLEAN,
    partial_shade BOOLEAN,
    full_shade BOOLEAN,
    notes TEXT
);

CREATE TABLE public.watering (
    id SERIAL PRIMARY KEY,
    plant_id INTEGER REFERENCES plants(id) ON DELETE CASCADE,
    frequency_days INTEGER,
    depth_mm INTEGER,
    volume_feet FLOAT,
    period TEXT,
    drought_tolerant BOOLEAN DEFAULT FALSE,
    soil TEXT[]
);

CREATE TABLE public.watering_schedule (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    plant_id INTEGER REFERENCES plants(id) ON DELETE CASCADE,
    scheduled_date TIMESTAMP,
    completed BOOLEAN DEFAULT FALSE
);

CREATE TABLE public.weather_forecast (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP,
    location TEXT,
    temperature FLOAT,
    precipitation FLOAT,
    humidity FLOAT
); 