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
        "-fmp4", "--fragmented", default=False, help="Путь для фрагментов MP4."
    )

    parser.add_argument(
        "-k",
        "--key",
        default=None,
        help="Полный путь к файлу, где будет создан случайный "
        "ключ (обязательно). Внимание: Путь до ключа "
        "должен быть доступен с веб-сайта(например: "
        '"/var/www/public_html/keys/enc.key")',
    )
    parser.add_argument(
        "-u",
        "--url",
        default=None,
        help="URL (или путь) для доступа к ключу на сайте (" "обязательно)",
    )
    parser.add_argument(
        "-krp",
        "--key_rotation_period",
        default=0,
        help="Используйте разные ключи для каждого набора"
        "сегментов, обновляя ключ после заданного количества"
        "сегментов.",
    )

    args = parser.parse_args()

    video = video_streaming.input(args.input)

    hls = video.hls(Formats.h264())
    hls.auto_generate_representations()

    if args.fragmented:
        hls.fragmented_mp4()

    if args.key is not None and args.url is not None:
        hls.encryption(args.key, args.url, args.key_rotation_period)

    hls.output(args.output, monitor=monitor)


if __name__ == "__main__":
    sys.exit(main())
