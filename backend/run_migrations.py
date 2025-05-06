from app.database.migrations.add_wind_speed import upgrade

if __name__ == "__main__":
    print("Running database migrations...")
    upgrade()
    print("Migrations completed successfully!") 