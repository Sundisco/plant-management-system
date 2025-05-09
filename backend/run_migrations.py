from app.database.migrations.add_wind_speed import upgrade as add_wind_speed_column
from app.database.migrations.add_default_user import add_default_user
from app.database.migrations.ensure_schema import ensure_schema
from app.database.migrations.prepare_data import prepare_data

def run_migrations():
    print("Running migrations...")
    ensure_schema()
    add_wind_speed_column()
    prepare_data()
    add_default_user()
    print("Migrations completed successfully!")

if __name__ == "__main__":
    run_migrations() 