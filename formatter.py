# -*- coding: utf-8 -*-

import os, math, json

def formatter(output_path, transcription, audio_file):
	extensions = set()
	for f in os.listdir(output_path):
		name, ext = os.path.splitext(f)
		if ext:
			extensions.add(ext)
	file_name_without_path = os.path.basename(audio_file)
	file_name = os.path.splitext(file_name_without_path)[0]
	if '.json' in extensions:
		word_to_json(transcription, os.path.join(output_path, f"{file_name}.json"))
	if '.txt' in extensions:
		word_to_txt(transcription, os.path.join(output_path, f"{file_name}.txt"))
	if '.srt' in extensions:
		word_to_srt(transcription, os.path.join(output_path, f"{file_name}.srt"))
	
def format_srt_time(seconds: float) -> str:
	frac, whole = math.modf(seconds)
	ms = int(frac * 1000)
	m, s = divmod(int(whole), 60)
	h, m = divmod(m, 60)
	return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def word_to_json(transcription, file_path):
	json_data = []
	text_0=''
	start_0=0
	speaker_0='speaker_0'
	word_end=0
	for word in transcription.words:
		if start_0==0:
			start_0 = word.start
		word_text = word.text
		word_type = word.type
		word_speaker = word.speaker_id
		word_end = word.end
		if word_type != 'word':
			if text_0:
				json_data.append({
					"text": text_0,
					"start": start_0,
					"end": word.start,
					"speaker_id": speaker_0,
					"type": "word"
			})
			if word_type == 'audio_event':
				json_data.append({
					"text": word_text,
					"start": word.start,
					"end": word_end,
					"speaker_id": word_speaker,
					"type": "audio_event"
				})
			text_0 = ''
			start_0 = 0
		else:
			if word_speaker != speaker_0:
				if text_0:
					json_data.append({
						"text": text_0,
						"start": start_0,
						"end": word.start,
						"speaker_id": speaker_0,
						"type": "word"
					})
				text_0 = ''
				start_0 = word.start
				speaker_0 = word_speaker
			text_0 += word_text
	
	if text_0:
		json_data.append({
			"text": text_0,
			"start": start_0,
			"end": word_end,
			"speaker_id": speaker_0,
			"type": "word"
		})
	save_json(json_data, file_path)

def save_json(json_data, file_name):
	with open(file_name, 'a+', encoding='utf-8-sig') as f:
		json.dump(json_data, f, indent=4, ensure_ascii=False)
	print(f"json saved to {file_name}")

def word_to_txt(transcription, file_path):
	txt_data = []
	text_buffer = ''
	speaker_buffer = ''
	for word in transcription.words:
		if word.type != 'word':
			if text_buffer:
				txt_data.append(f"({speaker_buffer}){text_buffer}")
			if word.type == 'audio_event':
				txt_data.append(f"{word.text}")
			text_buffer = ''
		else:
			if word.speaker_id != speaker_buffer:
				if text_buffer:
					txt_data.append(f"({speaker_buffer}){text_buffer}")
					text_buffer = ''
				speaker_buffer = word.speaker_id
			text_buffer += word.text
	if text_buffer:
		txt_data.append(f"({speaker_buffer}){text_buffer}")
	save_txt(txt_data, file_path)

def save_txt(txt_data, file_name):
	with open(file_name, 'a+', encoding='utf-8-sig') as f:
		f.write('\n'.join(txt_data))
	print(f"txt saved to {file_name}")

def word_to_srt(transcription, file_path):
	srt_data = []
	srt_index = 1
	text_buffer = ''
	speaker_buffer = ''
	start_time = 0
	end_time = 0
	for word in transcription.words:
		end_time = word.end
		if start_time == 0:
			start_time = word.start
			speaker_buffer = word.speaker_id
		if word.type != 'word':
			if text_buffer:
				srt_data.append(f"{srt_index}\n{format_srt_time(start_time)} --> {format_srt_time(end_time)}\n<{speaker_buffer}>{text_buffer}\n")
				srt_index += 1
			if word.type == 'audio_event':
				srt_data.append(f"{srt_index}\n{format_srt_time(word.start)} --> {format_srt_time(end_time)}\n{word.text}\n")
				srt_index += 1
			text_buffer = ''
			start_time == 0
		else:
			if word.speaker_id != speaker_buffer:
				if text_buffer:
					srt_data.append(f"{srt_index}\n{format_srt_time(start_time)} --> {format_srt_time(end_time)}\n<{speaker_buffer}>{text_buffer}\n")
					srt_index += 1
				text_buffer = ''
				start_time = word.start
				speaker_buffer = word.speaker_id
			text_buffer += word.text		
	if text_buffer:
		srt_data.append(f"{srt_index}\n{format_srt_time(start_time)} --> {format_srt_time(end_time)}\n<{speaker_buffer}>{text_buffer}\n")
	save_srt(srt_data, file_path)
	
def save_srt(srt_data, file_name):
	with open(file_name, 'a+', encoding='utf-8-sig') as f:
		f.write('\n'.join(srt_data))
	print(f"srt saved to {file_name}")

if __name__ == "__main__":
	from main import saveload_transcription
	transcription = ''
	transcription = saveload_transcription(transcription, audio_file)
	print(transcription.additional_formats[0].content)
	formatter('output', transcription, audio_file)

	# transcription_results_to_segmented_json(transcription, f"transcription_results_{file_name}_segmented.json")

	# print(transcription)
	# print(transcription.additional_formats[0].content)
	# for word in transcription.words:
	# 	print(word)



