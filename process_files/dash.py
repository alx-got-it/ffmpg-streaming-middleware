import argparse
import datetime
import sys
import logging

import video_streaming
from video_streaming.format import Formats

logging.basicConfig(
    filename="streaming.log",
    level=logging.NOTSET,
    format="[%(asctime)s] %(levelname)s: %(message)s",
)


def monitor(ffmpeg, duration, time_, time_left, process):
    per = round(time_ / duration * 100)
    sys.stdout.write(
        "\rПерекодирую...(%s%%) %s осталось [%s%s]"
        % (
            per,
            datetime.timedelta(seconds=int(time_left)),
            "#" * per,
            "-" * (100 - per),
        )
    )
    sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i", "--input", required=True, help="Пусть к видео файлу (обязательно)."
    )
    parser.add_argument("-o", "--output", default=None, help="Путь для записи файлов.")

    parser.add_argument(
        "-hls", "--hls_output", default=False, help="разместить HLS плейлисты."
    )

    args = parser.parse_args()

    video = video_streaming.input(args.input)

    dash = video.dash(Formats.h264())
    dash.auto_generate_representations()

    if args.hls_output:
        dash.generate_hls_playlist()

    dash.output(args.output, monitor=monitor)


if __name__ == "__main__":
    sys.exit(main())
