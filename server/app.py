from flask import Flask, request, send_file, jsonify, after_this_request
from werkzeug.utils import secure_filename
from flask_cors import CORS
from scipy.io import wavfile
from scipy.fft import fft, fftfreq
from scipy.signal import find_peaks
from midiutil import MIDIFile
import numpy as np
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(app.instance_path, 'files')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

midiTable = {
    8.18: 0,
    8.66: 1,
    9.18: 2,
    9.72: 3,
    10.3: 4,
    10.91: 5,
    11.56: 6,
    12.25: 7,
    12.98: 8,
    13.75: 9,
    14.57: 10,
    15.43: 11,
    16.35: 12,
    17.32: 13,
    18.35: 14,
    19.45: 15,
    20.6: 16,
    21.83: 17,
    23.12: 18,
    24.5: 19,
    25.96: 20,
    27.5: 21,
    29.14: 22,
    30.87: 23,
    32.7: 24,
    34.65: 25,
    36.71: 26,
    38.89: 27,
    41.2: 28,
    43.65: 29,
    46.25: 30,
    49.0: 31,
    51.91: 32,
    55.0: 33,
    58.27: 34,
    61.74: 35,
    65.41: 36,
    69.3: 37,
    73.42: 38,
    77.78: 39,
    82.41: 40,
    87.31: 41,
    92.5: 42,
    98.0: 43,
    103.83: 44,
    110.0: 45,
    116.54: 46,
    123.47: 47,
    130.81: 48,
    138.59: 49,
    146.83: 50,
    155.56: 51,
    164.81: 52,
    174.61: 53,
    185.0: 54,
    196.0: 55,
    207.65: 56,
    220.0: 57,
    233.08: 58,
    246.94: 59,
    261.63: 60,
    277.18: 61,
    293.66: 62,
    311.13: 63,
    329.63: 64,
    349.23: 65,
    369.99: 66,
    392.0: 67,
    415.3: 68,
    440.0: 69,
    466.16: 70,
    493.88: 71,
    523.25: 72,
    554.37: 73,
    587.33: 74,
    622.25: 75,
    659.26: 76,
    698.46: 77,
    739.99: 78,
    783.99: 79,
    830.61: 80,
    880.0: 81,
    932.33: 82,
    987.77: 83,
    1046.5: 84,
    1108.73: 85,
    1174.66: 86,
    1244.51: 87,
    1318.51: 88,
    1396.91: 89,
    1479.98: 90,
    1567.98: 91,
    1661.22: 92,
    1760.0: 93,
    1864.66: 94,
    1975.53: 95,
    2093.0: 96,
    2217.46: 97,
    2349.32: 98,
    2489.02: 99,
    2637.02: 100,
    2793.83: 101,
    2959.96: 102,
    3135.96: 103,
    3322.44: 104,
    3520.0: 105,
    3729.31: 106,
    3951.07: 107,
    4186.01: 108,
    4434.92: 109,
    4698.64: 110,
    4978.03: 111,
    5274.04: 112,
    5587.65: 113,
    5919.91: 114,
    6271.93: 115,
    6644.88: 116,
    7040.0: 117,
    7458.62: 118,
    7902.13: 119,
    8372.02: 120,
    8869.84: 121,
    9397.27: 122,
    9956.06: 123,
    10548.08: 124,
    11175.3: 125,
    11839.82: 126,
    12543.85: 127
}

midiFreqs = list(midiTable.keys())

# Credit: https://stackoverflow.com/questions/2566412/find-nearest-value-in-numpy-array
def findNearestMidiPitch(freq):

    # Search frequency placement within fixed Midi freequencies
    idx = np.searchsorted(midiFreqs, freq, side="left")

    # Return pitch of closest Midi frequency
    if idx > 0 and (idx == len(midiFreqs) or np.abs(freq - midiFreqs[idx-1]) < np.abs(freq - midiFreqs[idx])):
        return midiTable[midiFreqs[idx-1]]
    else:
        return midiTable[midiFreqs[idx]]

def getFrameNotes(audio, samplerate, interval):

    # Init some variables to describe data 
    duration = len(audio)/samplerate
    frames = int(duration / interval) + 1
    frameLength = int(samplerate * interval)
    frameNotes = []

    # Go through each sample within a frame
    for i in range(0, frames):

        # Retrieve sample
        start = i * frameLength
        end = (i + 1) * frameLength
        frameData = audio[start:end]

        # Apply FFT
        yf = fft(frameData)
        xf = fftfreq(len(frameData), 1 / samplerate)

        # Get peak frequencies within FFT
        indices, properties = find_peaks(yf, threshold=200000, distance=5)

        # Approximate Midi pitch of each peak frequency
        peakFreqs = set()
        for j in indices:
            peakFreqs.add(findNearestMidiPitch(np.abs(xf[j])))
        frameNotes.append(peakFreqs)
    return frameNotes

def getNotes(frameNotes):
    notes = []
    allNotes = []
    playingNotes = {}
    for i in range(0, len(frameNotes)):
        currNotes = frameNotes[i]
        if i is 0:
            for note in currNotes:
                playingNotes[note] = 0
        else:
            # Find which notes stopped playing
            playingNotesCopy = playingNotes.copy()
            for note in playingNotes:
                startTime = playingNotes[note]
                if note not in currNotes:
                    allNotes.append({
                        "pitch": note,
                        "start": startTime,
                        "duration": i - startTime
                    })
                    del playingNotesCopy[note]
            
            # Find which notes started playing
            for note in currNotes:
                if note not in playingNotes:
                    playingNotesCopy[note] = i
            playingNotes = playingNotesCopy               
    return allNotes

def createMidiFile(allNotes, interval, filepath):

    # Midi Config
    track    = 0
    channel  = 0
    time     = 0
    tempo    = 60 / interval
    volume   = 100 
    MyMIDI = MIDIFile(1) 
    MyMIDI.addTempo(track, time, tempo)

    # Add all notes to Midi
    for note in allNotes:
        MyMIDI.addNote(track, channel, note["pitch"], note["start"], note["duration"], volume)
    
    # Create Midi FIle
    with open(filepath, "wb") as output_file:
        MyMIDI.writeFile(output_file)

@app.route('/', methods=['POST'])
def home():

    # Save uploaded file
    f = request.files["audio"]
    filename = secure_filename(f.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    f.save(filepath)

    # Process audio file
    samplerate, data = wavfile.read(filepath)
    audio = data.mean(axis=1)
    interval = .1
    frameNotes = getFrameNotes(audio, samplerate, interval)
    allNotes = getNotes(frameNotes)
    midiFilePath = filepath + ".mid"
    createMidiFile(allNotes, interval, midiFilePath)

    # Send and delete temp files
    @after_this_request
    def deleteFiles(response):
        os.remove(midiFilePath)
        os.remove(filepath)
        return response
    return send_file(midiFilePath)
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)


