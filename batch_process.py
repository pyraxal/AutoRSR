from tqdm import tqdm
import os
import shutil

def write_output(wavfile, gt):
    #Takes the paths of the wav file and ground truths
    json1 = whispherx.transcribe(wavfile)
    print(json1)
    json2 = align(gt, format(json1))
    ground_truth = open(gt).readlines()
    _, __, score = auto_rsr.batch(ground_truth, json2)
    file = open("/output.txt", "a")
    file.writelines(f"{score}" + "\n")
    file.close()

def move_file(file_path, processed_directory):
    shutil.move(file_path, os.path.join(processed_directory, os.path.basename(file_path)))
    print(f"Moved file: {file_path} to {processed_directory}")

def process_file(file_path, processed_directory, gt):
    print(f"Processing file: {file_path}")
    write_output(file_path, gt)
    move_file(file_path, processed_directory)

def iterate_files(directory, processed_directory, gt):
    files = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    
    if not files:
        print("No files found in the directory.")
        return

    files.sort()
    
    for file in tqdm(files, desc="Processing files", unit="file"):
        process_file(file, processed_directory, gt)


'''
Sample:

directory = "/" #Give directory of the wav files
processed_directory = "/" #Give location to store finished wav files in case of any interruption
gt = "/" #Give location of the ground truth file
iterate_files(directory, processed_directory, gt)
'''
