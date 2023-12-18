import glob
import os
import shutil

result_path = "../results-archive"
data_path = "../data"

for pc_name in os.listdir(result_path):
    path = f"{result_path}/{pc_name}"

    for name in os.listdir(path):
        path1 = f"{path}/{name}"

        for nr in os.listdir(path1):
            path2 = f"{path1}/{nr}/criterion"

            for rust_kind in os.listdir(path2):
                path3 = f"{path2}/{rust_kind}"

                if rust_kind == "report":
                    print(path3)
                    shutil.rmtree(path3)
                    continue

                for part in os.listdir(path3):
                    path4 = f"{path3}/{part}"

                    if part == "new":
                        for file in os.listdir(path4):
                            path5 = f"{path4}/{file}"

                            if file == "estimates.json":
                                print(f"Keep: {path5}")
                            else:
                                print(path5)
                                os.remove(path5)
                    else:
                        print(path4)
                        shutil.rmtree(path4)
