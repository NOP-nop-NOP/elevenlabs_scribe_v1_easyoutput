# -*- coding: utf-8 -*-

import os, math, json
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

def elevenlabs_api():
	from dotenv import load_dotenv
	load_dotenv()
	elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"),)
	return elevenlabs

def api_service(input_type, audio_file):
	elevenlabs = elevenlabs_api()
	if input_type == 0:
		transcription = get_transcription_file(audio_file, elevenlabs)
	else:
		transcription = get_transcription_url(audio_file, elevenlabs)
	if transcription:
		print(f"Transcription get success")
	return transcription

def get_transcription_file(audio_input_path, elevenlabs):
	with open(audio_input_path, 'rb') as f:
		audio_input = f.read()
	transcription = elevenlabs.speech_to_text.convert(
		model_id="scribe_v1", # Model to use, for now only "scribe_v1" is supported
		file=audio_input, # or cloud_storage_url
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

def get_transcription_url(audio_url, elevenlabs):
	transcription = elevenlabs.speech_to_text.convert(
		model_id="scribe_v1", # Model to use, for now only "scribe_v1" is supported
		cloud_storage_url=audio_url,
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

def transcription_results_to_segmented_json(transcription, file_name):
	json_data = json.loads(transcription.additional_formats[0].content)
	# json_str = json.dumps(json_data, ensure_ascii=False, indent=4)
	# print(json_str)
	with open(file_name, 'a+', encoding='utf-8-sig') as f:
		json.dump(json_data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
	from main import elevenlabs_api
	from main import audio_input
	from main import saveload_transcription
	input_type, audio_input = audio_input('input')
	transcription = ''
	elevenlabs = elevenlabs_api()
	for audio_file in audio_input:
		if input_type < 2:
			transcription = api_service(input_type, audio_file, elevenlabs)
		transcription = saveload_transcription(transcription, audio_file)
		print(transcription)

'''
def get_transcription(audio_input_path):
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
'''