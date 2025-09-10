# -*- coding: utf-8 -*-

import os, math, json
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
	
SrtExportOptions = {
	"format": "srt", # format
	"max_characters_per_line": 100, # max_characters_per_line
	"include_speakers": True, # include_speakers
	"include_timestamps": True, # include_timestamps
	"segment_on_silence_longer_than_s": 5, # segment_on_silence_longer_than_s
	"max_segment_duration_s": 100, # max_segment_duration_s
	"max_segment_chars": 1000, # max_segment_chars
}
SegmentedJsonExportOptions = {
	"format": "segmented_json", # format
	"include_speakers": True, # include_speakers
	"include_timestamps": True, # include_timestamps
	"segment_on_silence_longer_than_s": 5, # segment_on_silence_longer_than_s
	"max_segment_duration_s": 100, # max_segment_duration_s
	"max_segment_chars": 1000, # max_segment_chars
}

def api_key_and_audio_input(api_key_path, audio_input_path):
	with open(api_key_path, "r", encoding="utf-8") as f:
		api_key_from_file = f.read().strip()
	with open(audio_input_path, "r", encoding="utf-8") as f:
		audio_input = f.read().strip()
		# audio_input = ''
	return api_key_from_file,audio_input

def local_file_input(audio_url):
	if audio_url:
		return audio_url
	audio_file = None
		# Find the first .wav, .mp3, or .aac file in the current directory
	for ext in ['.wav', '.mp3', '.aac']:
		files = sorted([f for f in os.listdir('.') if f.lower().endswith(ext)])
		if files:
			audio_file = files[0]
			with open(audio_file, 'rb') as f:
				return f.read()
	else:
		raise FileNotFoundError("No .wav, .mp3, or .aac file found in the current directory.")

def get_transcription(api_key_path, audio_input_path):
	load_dotenv()
	audio_url = audio_input(audio_input_path)
	elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"),)
	# print(audio_url,api_key_from_file)
	audio_input = local_file_input(audio_url)
	transcription = elevenlabs.speech_to_text.convert(
		# https://elevenlabs.io/docs/api-reference/speech-to-text/convert
		model_id="scribe_v1", # Model to use, for now only "scribe_v1" is supported
		# file=audio_input, # or cloud_storage_url
		cloud_storage_url=audio_input,
		language_code="jpn", # Language of the audio file. If set to None, the model will detect the language automatically.
		tag_audio_events=True, # Tag audio events like laughter, applause, etc.
		# num_speakers=32,
		timestamps_granularity="word",
		diarize=True, # Whether to annotate who is speaking
		diarization_threshold=0.1, # A low value means there will be a higher chance of one speaker being diarized as two different speakers but also a lower chance of two different speakers being diarized as one speaker (more total speakers predicted).
		additional_formats=[SegmentedJsonExportOptions],
		# use_multi_channel=True,
	)
	return transcription

def saveload_transcription(transcription, file_name):
	import pickle
	if transcription:	
		with open(file_name, 'wb') as f:
				pickle.dump(transcription, f)
	else:
		with open(file_name, 'rb') as f:
			transcription = pickle.load(f)
	return transcription
	
def format_srt_time(seconds: float) -> str:
	frac, whole = math.modf(seconds)
	ms = int(frac * 1000)
	m, s = divmod(int(whole), 60)
	h, m = divmod(m, 60)
	return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def save_json(json_data,file_name):
	with open(file_name, 'a+', encoding='utf-8-sig') as f:
		json.dump(json_data, f, indent=4, ensure_ascii=False)

def word_to_json(transcription,file_name):
	json_data = []
	text_0=''
	start_0=0
	for word in transcription.words:
		if start_0==0:
			start_0 = word.start
		text = word.text
		type = word.type
		if type == 'spacing' or type == 'audio_event':
			if type == 'spacing' and text_0 == '':
				continue
			json_data.append({
				"text": text if text_0 == '' else text_0,
				"start": word.start if type == "audio_event" else start_0,
				"end": word.end if type == "audio_event" else word.start,
				"speaker_id": word.speaker_id,
				"type": "audio_event" if type == "audio_event" else "word"
			})
			text_0 = ''
			start_0 = 0
		else:
			text_0 += text
	
	json_data.append({
		"text": text_0,
		"start": start_0,
		"end": word.start,
		"speaker_id": word.speaker_id,
		"type": word.type
	})
	save_json(json_data,file_name)

def transcription_results_to_segmented_json(transcription, file_name):
	json_data = json.loads(transcription.additional_formats[0].content)
	# json_str = json.dumps(json_data, ensure_ascii=False, indent=4)
	# print(json_str)
	save_json(json_data, file_name)

if __name__ == "__main__":
	transcription = ''
	main()
	audio_input_path = os.path.join('input', 'audio_input.txt')
	transcription = get_transcription(api_key_path, audio_input_path)
	output_path = os.path.join('output', 'transcription_results_misumi')
	transcription = saveload_transcription(transcription, f"{output_path}.pkl")

	word_to_json(transcription,f'{output_path}.json')
	# transcription_results_to_segmented_json(transcription, f"transcription_results_{file_name}_segmented.json")

	# print(transcription)
	# print(transcription.additional_formats[0].content)
	# for word in transcription.words:
	# 	print(word)



