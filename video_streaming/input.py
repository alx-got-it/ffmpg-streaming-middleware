from .media import Media
from .utiles import get_os, cnv_options_to_args


class Capture(object):
    def __init__(self, video, options):
        self.options = options
        self.video = video

    def _linux(self):
        cap = "x11grab" if (is_screen := self.options.pop("screen", False)) else "v4l2"
        return {"f": cap, "i": self.video}

    def _windows(self):
        self.video = f"video={str(self.video)}"
        windows_audio = self.options.pop("windows_audio", None)
        if windows_audio is not None:
            self.video = f"{self.video}:audio={str(windows_audio)}"

        return {"f": "dshow", "i": self.video}

    def _os_x(self):
        return {"f": "avfoundation", "i": self.video}

    @staticmethod
    def _unknown():
        raise OSError("Неподдерживаемая ОС!")

    def __iter__(self):
        yield from getattr(self, f"_{get_os()}")().items()


class InputOption(object):
    def __init__(self, _input, **options):
        self.input_ = _input
        self.options = options

    def __str__(self):
        return " ".join(cnv_options_to_args(self._create()))

    def __iter__(self):
        yield from self._create().items()

    def _create(self):
        options = self.options.pop("pre_opts", {"y": None})
        is_cap = self.options.pop("capture", False)

        if is_cap:
            options.update(Capture(self.input_, self.options))
        elif isinstance(self.input_, (str, int)):
            i_options = {"i": str(self.input_)}
            i_options.update(self.options)
            options.update(i_options)
        else:
            raise ValueError("Поток не определён!")

        return options


class Input:
    def __init__(self, _input: InputOption):
        self.inputs = [_input]

    def input(self, _input, **options):
        self.inputs.append(InputOption(_input, **options))

    def __getattr__(self, name):
        def method(*args, **kwargs):
            media = Media(self)
            if hasattr(media, name):
                return getattr(media, name)(*args, **kwargs)
            else:
                raise AttributeError("Объект не имеет атрибута {}".format(name))

        return method


def input(_input, **options) -> Input:
    return Input(InputOption(_input, **options))
