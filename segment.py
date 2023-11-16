from pydub import AudioSegment
from pydub.silence import split_on_silence
import matplotlib.pyplot as plt
import numpy as np
# Import Flask and create an app instance
from flask import Flask, request, jsonify, render_template
app = Flask(__name__)

# Define a route for the root URL and a function to render the index.html template
@app.route('/')
def home():
    return render_template('index.html')

# Define a route for the API endpoint and a function to handle requests
@app.route('/split-audio', methods=['POST'])
def split_audio():
    # Get the file from the form data
    file = request.form['audio']
    # Save the file to a temporary location
    file.save('temp.wav')
    # Load the audio file
    audio = AudioSegment.from_wav('temp.wav')
    # Initialize the top energy db value to 31 dBFS
    top_db = 31
    # Split the audio on silence with minimum length of 1 second and top energy db of 27 dBFS
    chunks = split_on_silence(audio, min_silence_len=1000, silence_thresh=-top_db)
    # Create a list to store the chunk names and URLs
    result = []
    # Loop through the chunks
    for i, chunk in enumerate(chunks):
        # If the chunk is longer than 30 seconds, split it into smaller chunks of 30 seconds each
        if len(chunk) > 30000:
            # Initialize the min silence value to 1000 ms
            min_silence_len = 1000
            # Initialize a flag to indicate if the chunk is fully split
            fully_split = False
            # Loop until the chunk is fully split or the min silence value reaches zero
            while not fully_split and min_silence_len > 0:
                # Split the chunk on silence with the current min silence value and top energy db value
                subchunks = split_on_silence(chunk, min_silence_len=min_silence_len, silence_thresh=-top_db)
                # Check if any subchunk is longer than 30 seconds
                too_long = any(len(subchunk) > 30000 for subchunk in subchunks)
                # If yes, decrease the min silence value by 0.1 seconds and repeat the loop
                if too_long:
                    min_silence_len -= 50
                    # Decrease the top energy db value by 1 dBFS and repeat the loop 
                    top_db -= 1
                # If no, set the flag to True and exit the loop
                else:
                    fully_split = True
            
            # Loop through the final subchunks
            for j, subchunk in enumerate(subchunks):
                # Export the subchunk as a wav file
                subchunk.export(f"output/chunk{i}_{j}.wav", format="wav")
                # Append the chunk name and URL to the result list
                result.append({
                    "name": f"chunk{i}_{j}.wav",
                    "url": f"http://localhost:5000/output/chunk{i}_{j}.wav"
                })
        else:
            # Export the chunk as a wav file 
            chunk.export(f"output/chunk{i}.wav", format="wav")
            # Append the chunk name and URL to the result list 
            result.append({
                "name": f"chunk{i}.wav",
                "url": f"http://localhost:5000/output/chunk{i}.wav"
            })
    
    # Return a JSON response with the chunk names and URLs 
    return jsonify(result)

# Run the app 
if __name__ == '__main__':
    app.run(debug=True)
