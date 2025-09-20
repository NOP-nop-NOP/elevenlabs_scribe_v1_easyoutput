# -*- coding: utf-8 -*-

import os, json, re, time
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

def saveload_transcription(transcription, file_name, model_id):
	import pickle
	if transcription:
		file_name_without_path = os.path.basename(file_name)
		file_name_without_ext = os.path.splitext(file_name_without_path)[0]
		file_name = os.path.join('output', f"{file_name_without_ext}_{model_id}.pkl")
		with open(file_name, 'wb') as f:
				pickle.dump(transcription, f)
		print(f"the transcription of {file_name} is saved\n")
	else:
		with open(file_name, 'rb') as f:
			transcription = pickle.load(f)
		print(f"the transcription of {file_name} is loaded\n")
	return transcription

if __name__ == "__main__":
	input_type, audio_input = audio_input('input')
	
	for audio_file in audio_input:
		print(f"{audio_file} is being processed\n")
		transcription = ''
		model_id = ''
		if input_type < 2:
			print(f"the input type is : {input_type}\n")
			# 断线重连 (Reconnect on failure)
			max_retries = 10
			retry_count = 0
			while retry_count < max_retries:
				try:
					transcription, model_id = api_service(input_type, audio_file)
					break
				except Exception as e:
					retry_count += 1
					print(f"Error occurred: {e}. Retrying {retry_count}/{max_retries}...")
					transcription = ''
					model_id = ''
					time.sleep(1)
					if retry_count == max_retries:
						print("Max retries reached. Skipping this file.")
						break
			if transcription == '':
				continue
		# 检查audio_file是否是URL Encoding
		import urllib.parse
		decoded_audio_file = urllib.parse.unquote(audio_file)
		if decoded_audio_file != audio_file:
			audio_file = decoded_audio_file
		transcription = saveload_transcription(transcription, audio_file, model_id)
		print(f"the text of {audio_file} is : {transcription.text}\n")
		# for word in transcription.words:
		# 	print(word)
		# print(transcription.additional_formats[0].content)
		formatter('output', transcription, audio_file)

