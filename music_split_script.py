import csv
import ffmpeg
import os

def time_to_seconds(time_str):
    parts = list(map(int, time_str.split(':')))
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return hours * 3600 + minutes * 60 + seconds
    elif len(parts) == 2:
        minutes, seconds = parts
        return minutes * 60 + seconds
    return None

def split_audio(input_file, csv_file, cache_dir, output_dir):
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        rows = list(reader)
    
    if not rows:
        print("No split points found in CSV.")
        return
    
    os.makedirs(cache_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    metadata_input_files = []

    for i in range(len(rows)):
        name, split_time = rows[i]
        start_time = time_to_seconds(split_time)
        
        if i < len(rows) - 1:
            end_time = time_to_seconds(rows[i + 1][1])  # Next start time as current end time
        else:
            end_time = None  # Last segment goes till the end of the audio
        
        cache_file = os.path.join(cache_dir, f"{name}.flac")

        metadata_output_file = os.path.join(output_dir, f"{name}.flac")
        metadata_input_files.append((cache_file, metadata_output_file, i + 1, name))  # Store file info for later metadata assignment

        ffmpeg_cmd = ffmpeg.input(input_file, ss=start_time, to=end_time) if end_time else ffmpeg.input(input_file, ss=start_time)
        
        ffmpeg_cmd = ffmpeg_cmd.output(cache_file, metadata = f'title={name}')
        ffmpeg_cmd.run(overwrite_output=True)
    
    # Assign metadata after splitting
    for input_file, output_file, track_number, name in metadata_input_files:
        ffmpeg_cmd = ffmpeg.input(input_file)
        ffmpeg_cmd = ffmpeg_cmd.output(output_file, metadata = f"track={track_number}")
        ffmpeg_cmd.run(overwrite_output=True)
    
    print("Audio splitting and metadata assignment completed.")

if __name__ == "__main__":
    input_audio = r"directory of your input audio"  # Change to your actual input file
    csv_file = r"directory of your input csv"  # the first row of the table should be "name,split_time"
    cache_directory = r"where would you like to put cache in."  #  it is needed to be deleted manually
    output_directory = r"out put folder" # where to output

    split_audio(input_audio, csv_file, cache_directory, output_directory)
