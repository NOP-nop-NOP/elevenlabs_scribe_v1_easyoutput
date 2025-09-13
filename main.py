# -*- coding: utf-8 -*-

import os, json, re
from scribe_v1 import api_service
from formatter import formatter

def audio_input(audio_input_path):
	input_type = 0
	pkl_files = []
	for f in os.listdir(audio_input_path):
		if f.lower().endswith('.pkl'):
			pkl_files.append(os.path.join(audio_input_path, f))
	
	if pkl_files:
		input_type = 2
		return input_type, pkl_files

	audio_input_file = os.path.join(audio_input_path, 'audio_input.txt')
	if os.path.exists(audio_input_file):
		input_type = 1
		with open(audio_input_file, "r", encoding="utf-8") as f:
			audio_input = f.read().strip().split('\n')
	else:
		audio_input = []
		for ext in ['.wav', '.mp3', '.aac', '.m4a', '.flac', '.ogg']:
			files = [f for f in os.listdir(audio_input_path) if f.lower().endswith(ext)]
			audio_input.extend([os.path.join(audio_input_path, f) for f in files])
	
	return input_type, audio_input

def saveload_transcription(transcription, file_name):
	import pickle
	if transcription:
		file_name_without_path = os.path.basename(file_name)
		file_name_without_ext = os.path.splitext(file_name_without_path)[0]
		file_name = os.path.join('output', f"{file_name_without_ext}.pkl")
		with open(file_name, 'wb') as f:
				pickle.dump(transcription, f)
	else:
		with open(file_name, 'rb') as f:
			transcription = pickle.load(f)
	return transcription

if __name__ == "__main__":
	input_type, audio_input = audio_input('input')
	
	for audio_file in audio_input:
		print(f"{audio_file}\n")
		transcription = ''
		if input_type < 2:
			print(f"{audio_file} : {input_type}\n")
			transcription = api_service(input_type, audio_file)
		transcription = saveload_transcription(transcription, audio_file)
		print(f"{audio_file} : {transcription.text}\n")
		for word in transcription.words:
			print(word)
		# print(transcription.additional_formats[0].content)
		formatter('output', transcription, audio_file)

