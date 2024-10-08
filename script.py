import os
import subprocess
import time
import zipfile
import requests
from pymongo import MongoClient

# Function to check if MongoDB is running
def is_mongodb_running():
    print("Checking if MongoDB is running...")
    try:
        client = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=5000)
        client.server_info()  # Attempt to connect to MongoDB
        print("MongoDB is already running.")
        return True
    except Exception as e:
        print(f"MongoDB is not running. Reason: {e}")
        return False

# Function to download MongoDB if not available
def download_mongodb():
    print("Downloading MongoDB...")
    url = "https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-6.0.0.zip"
    output_path = "mongodb.zip"
    
    # Download MongoDB
    response = requests.get(url, stream=True)
    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    
    # Extract MongoDB
    with zipfile.ZipFile(output_path, 'r') as zip_ref:
        zip_ref.extractall("C:\\MongoDB")
    
    # Create data directory
    os.makedirs("C:\\data\\db", exist_ok=True)
    print("MongoDB downloaded and extracted successfully.")

# Function to start MongoDB if not running
def start_mongodb():
    print("Starting MongoDB...")
    try:
        # Check if MongoDB is already running
        result = subprocess.run(["tasklist"], capture_output=True, text=True)
        if "mongod.exe" not in result.stdout:
            subprocess.Popen(
                ["C:\\MongoDB\\mongodb-windows-x86_64-6.0.0\\bin\\mongod.exe", "--dbpath", "C:\\data\\db"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("Waiting for MongoDB to start...")
            for i in range(10):
                time.sleep(3)
                if is_mongodb_running():
                    print("MongoDB started successfully.")
                    return
            raise Exception("MongoDB did not start in time.")
        else:
            print("MongoDB is already running.")
    except Exception as e:
        print(f"Failed to start MongoDB: {e}")

# Initialize MongoDB if not exists
def initialize_mongodb():
    print("Initializing MongoDB...")
    try:
        client = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=5000)
        client.server_info()  # Trigger exception if MongoDB is not available
        db = client['TestDb']
        if 'TestModels' not in db.list_collection_names():
            db.create_collection('TestModels')
            print("Initialized MongoDB and created 'TestModels' collection.")
        else:
            print("'TestModels' collection already exists.")
    except Exception as e:
        print(f"MongoDB initialization failed: {e}")

# Main script flow

print("Starting main script...")

# Step 1: Check if MongoDB is running, if not, download and start MongoDB
if not is_mongodb_running():
    if not os.path.exists("C:\\MongoDB\\mongodb-windows-x86_64-6.0.0\\bin\\mongod.exe"):
        download_mongodb()
    start_mongodb()

# Step 2: Initialize MongoDB
initialize_mongodb()

# Step 3: Restore dependencies
print("Restoring .NET dependencies...")
subprocess.run(["dotnet", "restore"], check=True)

# Step 4: Build solution
print("Building solution...")
subprocess.run(["dotnet", "build", "--configuration", "Release", "--no-restore"], check=True)

try:
    swagger_url = "http://localhost:5000/swagger/v1/swagger.json"
    response = requests.get(swagger_url)
    if response.status_code == 200:
        with open("swagger.json", "w") as f:
            f.write(response.text)
        print("Swagger documentation downloaded successfully.")
    else:
        print(f"Failed to download Swagger documentation. Status code: {response.status_code}")
except Exception as e:
    print(f"Error while downloading Swagger documentation: {e}")

# Step 9: Package Application
print("Packaging application...")
subprocess.run(["dotnet", "publish", "-c", "Release", "-o", "package"], check=True)

# Step 10: Publish Application to GitHub Packages
print("Publishing package to GitHub Packages...")
subprocess.run(["python", "publish_to_github_packages.py"], check=True)
