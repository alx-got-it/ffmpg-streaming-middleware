import json
import logging
import subprocess

from .media_property import Size, Bitrate


class Streams:
    def __init__(self, streams):
        self.streams = streams

    def video(self, ignore_error=True):
        return self._get_stream("video", ignore_error)

    def audio(self, ignore_error=True):
        return self._get_stream("audio", ignore_error)

    def first_stream(self):
        return self.streams[0]

    def all(self):
        return self.streams

    def videos(self):
        return self._get_streams("video")

    def audios(self):
        return self._get_streams("audio")

    def _get_stream(self, media, ignore_error):
        media_attr = next(
            (stream for stream in self.streams if stream["codec_type"] == media), None
        )
        if media_attr is None and not ignore_error:
            raise ValueError("Поток {} не найден".format(str(media)))
        return media_attr if media_attr is not None else {}

    def _get_streams(self, media):
        for stream in self.streams:
            if stream["codec_type"] == media:
                yield stream


class FFProbe:
    def __init__(self, filename, cmd="ffprobe"):
        commands = [cmd, "-show_format", "-show_streams", "-of", "json", filename]
        logging.info("ffprobe запускает команду: {}".format(" ".join(commands)))
        process = subprocess.Popen(
            commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        self.out, err = process.communicate()
        if process.returncode != 0:
            logging.error(str(self.out) + str(err))
            raise RuntimeError("ffprobe", self.out, err)
        logging.info("ffprobe выполнил команду!")

    def streams(self):
        return Streams(json.loads(self.out.decode("utf-8"))["streams"])

    def format(self):
        return json.loads(self.out.decode("utf-8"))["format"]

    def all(self):
        return json.loads(self.out.decode("utf-8"))

    def save_as_json(self, path):
        with open(path, "w", encoding="utf-8") as probe:
            probe.write(self.out.decode("utf-8"))

    @property
    def video_size(self) -> Size:
        width = int(self.streams().video().get("width", 0))
        height = int(self.streams().video().get("height", 0))

        if width == 0 or height == 0:
            raise RuntimeError("Не удалось определить размер видео")

        return Size(width, height)

    @property
    def bitrate(self, _type: str = "k") -> Bitrate:
        overall = int(self.format().get("bit_rate", 0))
        video = int(self.streams().video().get("bit_rate", 0))
        audio = int(self.streams().audio().get("bit_rate", 0))

        if overall == 0:
            raise RuntimeError("Не удалось определить битрейт видео")

        return Bitrate(video, audio, overall, type=_type)
