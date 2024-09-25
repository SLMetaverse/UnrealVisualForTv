import unreal
import argparse
import glob
import time

def splitVal(p):
	return p.split("\\")

def convertVal(n, path):
	l = splitVal(path)[n:]
	f, _ = l[-1].split(".")
	t = "/".join(l[:-1]) + "/"
	return "/Game/" + t + f+"."+f

parser = argparse.ArgumentParser()

parser.add_argument("-p", "--projectFile", required=True)
parser.add_argument("-l", "--levelFile", required=True)
parser.add_argument("-c", "--configFile", required=True)

parser.add_argument("-v", "--videoSeq", nargs="+", required=True)

args = parser.parse_args()

print("\nProject file: ", args.projectFile)
print("Level file  : ", args.levelFile)
print("Config file : ", args.configFile)
print("Sequence dir: ", args.videoSeq)

s = splitVal(args.projectFile)

print("\nProject     : ", '\\'.join(s[:-1]))
print("Level path  : ", convertVal(len(s), args.levelFile))
print("Config path : ", convertVal(len(s), args.configFile))
print("Sequences    : ")

jobs = []
# for vs in glob.glob(args.param3 + '/LS_*'):
for vs in args.videoSeq:
	print(" ", convertVal(len(s), vs))
	jobs.append(convertVal(len(s), vs))

jobLength = len(jobs)

def render_finished(params):
	global jobLength
	unreal.log("=====================Render End===================================")
	# unreal.log(f"====================={params}===================================")
	# unreal.SystemLibrary.execute_console_command(None, "QUIT_EDITOR")
	jobLength -= 1
	if(jobLength == 0):
		time.sleep(15)
		unreal.SystemLibrary.execute_console_command(None, "QUIT_EDITOR")



subsystem = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)

unreal.log("This is log")
unreal.log_warning("This is warning")
unreal.log_error("This is error log")

# # u_level_file = "/Game/Work/L_WaikikiMap.L_WaikikiMap"
# u_level_file = "/Game/Work/L_WaikikiCesium.L_WaikikiCesium"
# u_level_seq_file = "/Game/Work/LevelSeqs/LS_first.LS_first"
# # u_preset_file = "/Game/Work/LevelSeqs/res720p.res720p"
# u_preset_file = "/Game/Work/LevelSeqs/res1080p.res1080p"

u_level_file = convertVal(len(s), args.levelFile)
u_preset_file = convertVal(len(s), args.configFile)

# editor = unreal.LevelEditorSubsystem()
# isLevelLoaded = editor.load_level(u_level_file)

queue = subsystem.get_queue()
executor = unreal.MoviePipelinePIEExecutor()

i = 0
for job_name in jobs:
	u_level_seq_file = job_name
	# config render job with movie pipeline config
	job = queue.allocate_new_job(unreal.MoviePipelineExecutorJob)
	job.job_name = 'job_' + str(i)
	job.map = unreal.SoftObjectPath(u_level_file)
	job.sequence = unreal.SoftObjectPath(u_level_seq_file)
	preset = unreal.EditorAssetLibrary.find_asset_data(u_preset_file).get_asset()
	job.set_configuration(preset)

	i += 1

executor.on_individual_job_work_finished_delegate.add_callable_unique(render_finished)

subsystem.render_queue_with_executor_instance(executor)


