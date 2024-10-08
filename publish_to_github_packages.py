import os
import subprocess
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define NuGet API key and package information
nuget_api_key = os.getenv('NUGET_API_KEY')
owner = os.getenv('GITHUB_OWNER')
package_path = 'package'

# Check if the NuGet API key and GitHub owner are provided
if not nuget_api_key:
    raise ValueError("The NUGET_API_KEY environment variable is not set. Please set it in the .env file.")
if not owner:
    raise ValueError("The GITHUB_OWNER environment variable is not set. Please set it in the .env file.")

# Construct the source URL for GitHub Packages
source_url = f"https://nuget.pkg.github.com/{owner}/index.json"

# Publish package to GitHub Packages
try:
    # Find all .nupkg files in the package directory
    for file in os.listdir(package_path):
        if file.endswith(".nupkg"):
            full_path = os.path.join(package_path, file)
            # Use dotnet nuget push to publish the package
            subprocess.run([
                "dotnet", "nuget", "push", full_path,
                "--source", source_url,
                "--api-key", nuget_api_key
            ], check=True)
    print("Package published to GitHub Packages successfully.")
except subprocess.CalledProcessError as e:
    print(f"Failed to publish package to GitHub Packages. Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
