import argparse
import datetime
import logging
import os

from video_streaming.ffprobe import FFProbe

logging.basicConfig(
    filename="probe.log",
    level=logging.NOTSET,
    format="[%(asctime)s] %(levelname)s: %(message)s",
)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i", "--input", required=True, help="Пусть к видео файлу (обязательно)."
    )

    args = parser.parse_args()

    return FFProbe(args.input)


if __name__ == "__main__":
    ffprobe = main()

    current_dir = os.path.dirname(os.path.abspath(__file__))
    ffprobe.save_as_json(os.path.join(current_dir, "probe.json"))

    all_media = ffprobe.all()

    video_format = ffprobe.format()

    streams = ffprobe.streams().all()
    videos = ffprobe.streams().videos()
    audios = ffprobe.streams().audios()

    first_stream = ffprobe.streams().first_stream()
    first_video = ffprobe.streams().video()
    first_audio = ffprobe.streams().audio()

    print("все медиа:")
    print(all_media)

    print("формат:")
    print(video_format)

    print("потоки:")
    print(streams)

    print("видео:")
    for video in videos:
        print(video)

    print("аудио:")
    for audio in audios:
        print(audio)

    print("первый поток:")
    print(first_stream)

    print("первое видео:")
    print(first_video)

    print("первое аудио:")
    print(first_audio)

    print(
        "длительность: {}".format(
            str(datetime.timedelta(seconds=float(video_format.get("duration", 0))))
        )
    )
    # длительность: 00:00:10.496

    print("размер: {}k".format(round(int(video_format.get("size", 0)) / 1024)))
    # размер: 290k

    print(
        "общий битрейт: {}k".format(round(int(video_format.get("bit_rate", 0)) / 1024))
    )
    # битрейт: 221k

    print(
        "разрешение: {}x{}".format(
            first_video.get("width", "Неизвестно"),
            first_video.get("height", "Неизвестно"),
        )
    )
    # разрешение: 480x270

    print(
        "видео битрейт: {}k".format(round(int(first_video.get("bit_rate", 0)) / 1024))
    )
    # видео битрейт: 149k

    print(
        "аудио битрейт: {}k".format(round(int(first_audio.get("bit_rate", 0)) / 1024))
    )
    # аудио битрейт: 64k
