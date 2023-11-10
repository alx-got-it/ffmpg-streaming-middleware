import shlex
import subprocess
import threading
import logging
import time

from .hls import HLSKeyInfoFile
from .utiles import get_time, time_left


def _p_open(commands, **options):
    logging.info("ffmpeg выполняет команду: {}".format(commands))
    return subprocess.Popen(shlex.split(commands), **options)


class Process(object):
    out = None
    err = None

    def __init__(self, media, commands: str, monitor: callable = None, **options):
        self.is_monitor = False
        self.input = options.pop("input", None)
        self.timeout = options.pop("timeout", None)
        default_proc_opts = {
            "stdin": None,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.STDOUT,
            "universal_newlines": False,
        }
        default_proc_opts.update(options)
        options.update(default_proc_opts)
        if callable(monitor) or isinstance(
            getattr(media, "key_rotation"), HLSKeyInfoFile
        ):
            self.is_monitor = True
            options.update({"stdin": subprocess.PIPE, "universal_newlines": True})

        self.process = _p_open(commands, **options)
        self.media = media
        self.monitor = monitor

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.process.kill()

    def _monitor(self):
        duration = 1
        _time = 0
        log = []
        start_time = time.time()

        while True:
            line = self.process.stdout.readline().strip()
            if line == "" and self.process.poll() is not None:
                break

            if line != "":
                log += [line]

            if isinstance(getattr(self.media, "key_rotation"), HLSKeyInfoFile):
                getattr(self.media, "key_rotation").rotate_key(line)

            if callable(self.monitor):
                duration = get_time("Длительность: ", line, duration)
                _time = get_time("время=", line, _time)
                self.monitor(
                    self,
                    line,
                    duration,
                    _time,
                    time_left(start_time, _time, duration),
                    self.process,
                )

        Process.out = log

    def _thread_mon(self):
        thread = threading.Thread(target=self._monitor)
        thread.start()

        thread.join(self.timeout)
        if thread.is_alive():
            self.process.terminate()
            thread.join()
            error = "Превышен таймаут {} секунд.".format(str(self.timeout))
            logging.error(error)
            raise RuntimeError(error)

    def run(self):
        if self.is_monitor:
            self._thread_mon()
        else:
            Process.out, Process.err = self.process.communicate(
                self.input, self.timeout
            )

        if self.process.poll():
            error = str(Process.err) if Process.err else str(Process.out)
            logging.error("ffmpeg не смог выполнить команду: {}".format(error))
            raise RuntimeError("ffmpeg не смог выполнить команду: ", error)

        logging.info("ffmpeg выполнил команду!")

        return Process.out, Process.err
