# Unreal Engine Python Scripting for Sequencer

This repository contains Python scripts to automate Unreal Engine's Sequencer for video generation. The scripts handle various tasks such as setting up camera locations, backgrounds, audio, and rendering. To ensure proper functionality, developers need to install specific Python packages in Unreal Engine's environment.

## Prerequisites

- Unreal Engine installed (version 5.4.4).
- Access to Unreal Engine's Python environment or ability to create a virtual environment within the Unreal Engine directory.

## Setup Instructions

### 1. Plugins to Enable in unreal engine
1. Go to `Edit > Plugins`.
2. Search and Enable `Python Editor Script Plugin`.
3. Search and Enable `USD Importer`.
4. Restart the editor.

### 2. Install Required Python Packages

To run the Python scripts, you must install necessary Python packages inside Unreal Engine's environment. Follow the steps below:

Install Packages Directly in Unreal Engine

1. Navigate to Unreal Engine's Python environment directory:
   ```bash
   cd /path/to/UnrealEngine/Engine/Binaries/ThirdParty/Python/YOUR_PYTHON_VERSION
   
2. Install required packages using pip:
  ```bash
  ./python.exe -m pip install -r /path/to/your/repo/requirements.txt
```

## Start Rendering
### 1. Navigate to AutoStart folder in unreal repo:
  ```bash
  cd /path/to/Repo/Content/PythonScripting/autostart/`
  ```

### 2. Execute python script for Unreal Enigne Rendering
  ```bash
  /path/to/UnrealEngine/Engine/Binaries/ThirdParty/Python/YOUR_PYTHON_VERSION/python.exe pythonTVRender.py --projectPath {path-to-repo/.uporject} --shotId {shot-guid} --renderQuality {quality} --production false`
  ```
  ```bash
  Arguments:
  --shotId (string): Defines the shot ID to process.
  --renderQuality (string): Specifies the render quality (e.g. "fast", "720p", "1080p", "2160p").
  --isprod (bool): Boolean value to determine whether the environment is production or testing.
```

## LFS config to AWS
1. Stack Name : `VisualTv-Lfs`
2. API Gateway : `VisualTv-Lfs`
3. Bucket :  `visualtv-lfs-storagebucket-xuwgehfk9ffj`
4. Lambda function : `VisualTv-Lfs`
