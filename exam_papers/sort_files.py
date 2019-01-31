import os
import glob
from shutil import copyfile

YEAR = "2018"

dir_path = os.path.dirname(os.path.realpath(__file__))
all_files = glob.glob(os.path.join(dir_path, YEAR, "*"))
module_names = {
    "EE1": [os.path.basename(x[0]) for x in os.walk(os.path.join(dir_path, "EE1"))],
    "EE2": [os.path.basename(x[0]) for x in os.walk(os.path.join(dir_path, "EE2"))],
    "EE3": [os.path.basename(x[0]) for x in os.walk(os.path.join(dir_path, "EE3"))],
    "EE4": [os.path.basename(x[0]) for x in os.walk(os.path.join(dir_path, "EE4"))],
}
for file_path in all_files:
    file_name = os.path.basename(file_path)
    year = file_name[0:3]
    module_num = file_name[4:7].strip().replace("_", "")
    module_name = None
    for name in module_names[year]:
        if name.startswith(module_num):
            module_name = name
    if not module_name:
        print("Could not find: {}-{}".format(year, module_num))
        continue

    _, extension = os.path.splitext(file_name.lower())

    if "solutions" in file_name.lower():
        target_filename = f"{YEAR}_sols.pdf"
    elif "annotate" in file_name.lower():
        target_filename = f"{YEAR}_ann.pdf"
    else:
        target_filename = f"{YEAR}.pdf"
    target_path = os.path.join(dir_path, year, module_name, target_filename)
    if os.path.isfile(target_path):
        print("Already exists: {}".format(target_path))
    else:
        copyfile(file_path, target_path)
        print("Copied {}".format(module_name))
print("Done!")
