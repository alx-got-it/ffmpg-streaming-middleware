import abc


MULTIPLY_BY_ONE = 1
MULTIPLY_BY_TWO = 2
MULTIPLY_BY_FOUR = 4
MULTIPLY_BY_Eight = 8
MULTIPLY_BY_SIXTEEN = 16
MULTIPLY_BY_THIRTY_TWO = 32


def _verify_codecs(codec, codecs):
    if codec is None:
        return
    elif codec not in codecs:
        ValueError("Кодек недоступен!")
    else:
        return str(codec)


class Format(abc.ABC):
    def __init__(self, video: str, audio: str, **codec_options):
        self.video = video
        self.audio = audio
        self.codec_options = codec_options

    @property
    def all(self) -> dict:
        args = {
            "c:v": self.video,
            "c:a": self.audio,
        }
        args.update(self.get_codec_options())
        return args

    @abc.abstractmethod
    def multiply(self) -> int:
        pass

    @abc.abstractmethod
    def get_codec_options(self) -> dict:
        pass


class H264(Format):
    def __init__(self, video: str = "libx264", audio: str = "aac", **codec_options):
        videos = ["libx264", "h264", "h264_amf", "h264_nvenc"]
        audios = ["copy", "aac", "libvo_aacenc", "libfaac", "libmp3lame", "libfdk_aac"]

        super(H264, self).__init__(
            _verify_codecs(video, videos),
            _verify_codecs(audio, audios),
            **codec_options
        )

    def multiply(self) -> int:
        return MULTIPLY_BY_TWO

    def get_codec_options(self) -> dict:
        h264_codec_options = {"bf": 1, "keyint_min": 25, "g": 250, "sc_threshold": 40}
        h264_codec_options.update(self.codec_options)
        return h264_codec_options


class HEVC(Format):
    def __init__(self, video: str = "libx265", audio: str = "aac", **codec_options):
        videos = ["libx265", "h265"]
        audios = ["copy", "aac", "libvo_aacenc", "libfaac", "libmp3lame", "libfdk_aac"]

        super(HEVC, self).__init__(
            _verify_codecs(video, videos),
            _verify_codecs(audio, audios),
            **codec_options
        )

    def multiply(self) -> int:
        return MULTIPLY_BY_TWO

    def get_codec_options(self) -> dict:
        h265_codec_options = {"keyint_min": 25, "g": 250, "sc_threshold": 40}
        h265_codec_options.update(self.codec_options)
        return h265_codec_options


class VP9(Format):
    def __init__(self, video: str = "libvpx-vp9", audio: str = "aac", **codec_options):
        videos = ["libvpx", "libvpx-vp9"]
        audios = ["copy", "aac", "libvo_aacenc", "libfaac", "libmp3lame", "libfdk_aac"]

        super(VP9, self).__init__(
            _verify_codecs(video, videos),
            _verify_codecs(audio, audios),
            **codec_options
        )

    def multiply(self) -> int:
        return MULTIPLY_BY_TWO

    def get_codec_options(self) -> dict:
        vp9_codec_options = {}
        vp9_codec_options.update(self.codec_options)
        return vp9_codec_options


class Formats:
    @staticmethod
    def h264(video: str = "libx264", audio: str = "aac", **codec_options) -> Format:
        return H264(video, audio, **codec_options)

    @staticmethod
    def hevc(video: str = "libx265", audio: str = "aac", **codec_options) -> Format:
        return HEVC(video, audio, **codec_options)

    @staticmethod
    def vp9(video: str = "libvpx-vp9", audio: str = "aac", **codec_options) -> Format:
        return VP9(video, audio, **codec_options)
