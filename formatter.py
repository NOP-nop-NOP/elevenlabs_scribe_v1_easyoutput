# -*- coding: utf-8 -*-

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Union


@dataclass
class Segment:
    text: str
    start: float
    end: float
    speaker_id: str
    segment_type: str

    def to_dict(self) -> Dict[str, Union[str, float]]:
        return {
            "text": self.text,
            "start": self.start,
            "end": self.end,
            "speaker_id": self.speaker_id,
            "type": self.segment_type,
        }


Segmenter = Callable[[object], Sequence[Segment]]


class BaseFormatter:
    extension: str = ""

    def write(self, segments: Sequence[Segment], file_path: Union[str, Path]) -> None:
        raise NotImplementedError


FORMATTERS: Dict[str, BaseFormatter] = {}
SEGMENTERS: Dict[str, Segmenter] = {}


def register_formatter(formatter: BaseFormatter) -> None:
    FORMATTERS[formatter.extension] = formatter


def register_segmenter(name: str, segmenter: Segmenter) -> None:
    SEGMENTERS[name] = segmenter


def resolve_segmenter(segmentation: Union[str, Segmenter, None]) -> Segmenter:
    if callable(segmentation):
        return segmentation
    if segmentation is None:
        return SEGMENTERS["default"]
    if segmentation in SEGMENTERS:
        return SEGMENTERS[segmentation]
    raise KeyError(f"Unknown segmentation strategy: {segmentation}")


def formatter(output_path: str, transcription, audio_file: str, *, segmentation: Union[str, Segmenter, None] = None) -> None:
    output_dir = Path(output_path)
    available_extensions = discover_output_extensions(output_dir)
    segmenter = resolve_segmenter(segmentation)
    segments = list(segmenter(transcription))
    base_name = Path(audio_file).stem

    for ext in available_extensions:
        formatter_impl = FORMATTERS.get(ext)
        if not formatter_impl:
            continue
        target_path = output_dir / f"{base_name}{ext}"
        formatter_impl.write(segments, target_path)


def discover_output_extensions(output_dir: Path) -> List[str]:
    return sorted({path.suffix for path in output_dir.iterdir() if path.is_file() and path.suffix})


def default_segmenter(transcription) -> List[Segment]:
    words = getattr(transcription, "words", [])
    segments: List[Segment] = []
    text_buffer: List[str] = []
    start_buffer: Optional[float] = None
    end_buffer: Optional[float] = None
    speaker_buffer: Optional[str] = None

    def flush_buffer() -> None:
        nonlocal text_buffer, start_buffer, end_buffer, speaker_buffer
        if not text_buffer:
            return
        segments.append(
            Segment(
                text="".join(text_buffer),
                start=start_buffer if start_buffer is not None else 0.0,
                end=end_buffer if end_buffer is not None else start_buffer or 0.0,
                speaker_id=speaker_buffer or "speaker_0",
                segment_type="word",
            )
        )
        text_buffer = []
        start_buffer = None
        end_buffer = None
        speaker_buffer = None

    for token in words:
        token_type = getattr(token, "type", "word")
        token_text = getattr(token, "text", "")
        token_start = getattr(token, "start", 0.0)
        token_end = getattr(token, "end", token_start)
        token_speaker = getattr(token, "speaker_id", "speaker_0")

        if token_type != "word":
            flush_buffer()
            segments.append(
                Segment(
                    text=token_text,
                    start=token_start,
                    end=token_end,
                    speaker_id=token_speaker,
                    segment_type=token_type,
                )
            )
            continue

        if speaker_buffer is not None and token_speaker != speaker_buffer:
            flush_buffer()

        if not text_buffer:
            start_buffer = token_start
            speaker_buffer = token_speaker

        text_buffer.append(token_text)
        end_buffer = token_end

    flush_buffer()
    return segments


class JsonFormatter(BaseFormatter):
    extension = ".json"

    def write(self, segments: Sequence[Segment], file_path: Union[str, Path]) -> None:
        data = [segment.to_dict() for segment in segments]
        write_json(file_path, data)
        print(f"json saved to {file_path}")


class TxtFormatter(BaseFormatter):
    extension = ".txt"

    def write(self, segments: Sequence[Segment], file_path: Union[str, Path]) -> None:
        lines: List[str] = []
        for segment in segments:
            if segment.segment_type == "audio_event":
                lines.append(segment.text)
            else:
                lines.append(f"({segment.speaker_id}){segment.text}")
        write_text(file_path, "\n".join(lines))
        print(f"txt saved to {file_path}")


class SrtFormatter(BaseFormatter):
    extension = ".srt"

    def write(self, segments: Sequence[Segment], file_path: Union[str, Path]) -> None:
        index = 1
        lines: List[str] = []
        for segment in segments:
            start_time = format_srt_time(segment.start)
            end_time = format_srt_time(segment.end)
            if segment.segment_type == "audio_event":
                content = segment.text
            else:
                content = f"{segment.speaker_id}: {segment.text}"
            lines.extend((
                str(index),
                f"{start_time} --> {end_time}",
                content,
                "",
            ))
            index += 1
        write_text(file_path, "\n".join(lines))
        print(f"srt saved to {file_path}")


def format_srt_time(seconds: float) -> str:
    frac, whole = math.modf(seconds)
    ms = int(round(frac * 1000))
    m, s = divmod(int(whole), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_json(file_path: Union[str, Path], data: Iterable) -> None:
    path = Path(file_path)
    with path.open("w", encoding="utf-8-sig") as handle:
        json.dump(list(data), handle, indent=4, ensure_ascii=False)


def write_text(file_path: Union[str, Path], content: str) -> None:
    path = Path(file_path)
    path.write_text(content, encoding="utf-8-sig")


register_segmenter("default", default_segmenter)
register_formatter(JsonFormatter())
register_formatter(TxtFormatter())
register_formatter(SrtFormatter())


if __name__ == "__main__":
    pass


