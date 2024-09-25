import subprocess
import glob
import argparse
import os

def getFileFromCollection(rootPath, filter, fileIdentifier):
    for i in glob.glob(rootPath + filter, recursive=True):
      if(fileIdentifier in i):
        print(f"FileID: '{fileIdentifier}' found as {i}")
        return i
    print(f"Failed to find '{fileIdentifier}' inside {rootPath}.")
    return None

def execute_command(cmd, cwd = None):
    """
    Executes a command in a subprocess and captures its output.

    Args:
      cmd (str): The command to be executed.
      cwd (str, optional): The current working directory for the subprocess. Defaults to None.

    Returns:
      str: The captured output of the command.

    Raises:
      subprocess.CalledProcessError: If the command returns a non-zero exit code.

    Example:
      >>> execute_command("ls -l")
      total 4
      -rw-r--r--  1 user  staff  0 Jan  1 00:00 file.txt
    """
    try:
      result = subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=cwd,
        check=True,  # Raise subprocess.CalledProcessError for non-zero return codes
      )
      print(result.stdout)
    except subprocess.CalledProcessError as e:
      print(f"Error executing command: {cmd}\n{e.stderr}")
      return e.stderr
    

def startUnreal(U_PROJECT, py_file, shotGUID, renderQuality, isProdution, verbose = False):
    try:
      UNREAL_EXE = getFileFromCollection("C:\\Program Files\\Epic Games\\UE_5.4\\Engine\\Binaries\\Win64", "/**/*Editor-Cmd.exe", "UnrealEditor-Cmd")
      # py_file = getFileFromCollection("./", "/**/**/py*.py", "Render")
      py_cmd = py_file + " -i " + shotGUID + " -r " + renderQuality + " -p " + str(isProdution)
      
      print("Unreal Editor started!!")
      print(70*"*")

      cmd = f'"{UNREAL_EXE}" "{U_PROJECT}" -ExecCmds="py {py_cmd}"'
      if(verbose):
         cmd += " -stdout "
      print(cmd)
      execute_command(cmd)
      print(f"shotId: {shotGUID}, Rendering complete!")
    except Exception as e:
      print(f"Failed to start Unreal Engine through python subprocess: {str(e)}")
      raise e


parser = argparse.ArgumentParser()
parser.add_argument("-p", "--projectPath", required=True)
parser.add_argument("-i", "--shotId", required=True)
parser.add_argument("-r", "--renderQuality", help='fast, 720p, 1080p, 2160p', required=True) # "fast", "720p", "1080p", "2160p"
parser.add_argument("-d", "--production", required=True, default=False, type=lambda x: (str(x).lower() == 'true'))
parser.add_argument("-v", "--verbose", action='count', default=0)

args = parser.parse_args()
projectDir = args.projectPath
shotID = args.shotId
renderQuality = args.renderQuality
isProd = args.production

startUnreal(
   getFileFromCollection(projectDir, "/**/*.uproject", "UnrealVisualTv"),
   getFileFromCollection(projectDir, "/**/**/*.py", "Initialize"),
   shotID,
   renderQuality,
   isProd,
   0 < args.verbose
)

# cmd: "C:\Program Files\Epic Games\UE_5.4\Engine\Binaries\ThirdParty\Python3\Win64\python.exe" pythonTVRender.py --projectPath "F:\Repos\VisualForTV" --shotId "53faa6c4-ca63-4dfa-a523-a6d3066d3bdc" --renderQuality "fast" --production True