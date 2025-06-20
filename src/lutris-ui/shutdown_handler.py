from __future__ import annotations
from datetime import datetime
from os import getuid
from subprocess import run

import psutil


class BaseModule:
    __zero_datetime = datetime(2000, 1, 1)

    def __init__(self):
        self.pid: int | None = None
        self.shutdown_sent_time = self.__zero_datetime

    def check_is_running(self) -> bool:
        # Check the launched command is still running
        if self.pid is not None:
            try:
                process = psutil.Process(self.pid)
                if process.status() == "zombie":
                    try:
                        process.wait(timeout=1)
                        return False
                    except psutil.TimeoutExpired:
                        return True
                if process.is_running():
                    return True
            except psutil.NoSuchProcess:
                self.pid = None
                self.shutdown_sent_time = self.__zero_datetime
                return False
        return False

    def shutdown(self, root_pid: int) -> bool:
        return False


class LaunchModule(BaseModule):
    def __init__(self, pid: int):
        super().__init__()
        self.pid = pid
        self.launch_time = datetime.now()

    def check_is_running(self) -> bool:
        is_running = super().check_is_running()
        if is_running is True:
            return True

        if (
            datetime.now() - self.launch_time
        ).total_seconds() < 5:  # Wait at least 5 seconds before giving up
            return True
        return False


class LutrisModule(BaseModule):
    def check_is_running(self) -> bool:
        if self.pid is None:
            # Search for pid in running processes
            for process in psutil.process_iter():
                try:
                    if process.uids().real != getuid():
                        continue
                except psutil.ZombieProcess:
                    continue
                except psutil.NoSuchProcess:
                    continue

                if process.name().startswith("lutris-wrapper"):
                    self.pid = process.pid
        return super().check_is_running()


class AnyModule(BaseModule):
    def shutdown(self, root_pid: int) -> bool:
        if root_pid is None:
            return False
        try:
            root_process = psutil.Process(root_pid)
            if root_process.is_running():
                if (datetime.now() - self.shutdown_sent_time).total_seconds() < 10:
                    return True  # Wait at least 2 Seconds for app shutdown
                done = False
                for child in root_process.children():
                    print(f"Game shutdown ANY: send kill to {child.pid}")
                    child.kill()
                    self.shutdown_sent_time = datetime.now()
                    done = True
                return done

        except psutil.NoSuchProcess:
            return True
        return False


class SteamModule(BaseModule):
    def shutdown(self, root_pid: int) -> bool:
        if root_pid is None:
            return False
        try:
            root_process = psutil.Process(root_pid)
            if root_process.is_running():
                for child in root_process.children():
                    try:
                        # Assumption: Command line is 'bash', '*/steam.sh', 'steam://rungameid/*'
                        if child.cmdline()[2].startswith("steam://rungameid"):
                            if (
                                datetime.now() - self.shutdown_sent_time
                            ).total_seconds() < 10:
                                return True  # Wait at least 10 Seconds for Steam client shutdown
                            print(f"Game shutdown Steam: call steam -shutdown")
                            run(["steam", "-shutdown"])
                            self.shutdown_sent_time = datetime.now()
                            return True
                    except IndexError:
                        pass

        except psutil.NoSuchProcess:
            return True
        return False


class ShutdownManager:
    def __init__(self, pid: int):
        self.shutdown_modules = []
        self.lutris_module = LutrisModule()  # Lutris process is the root process
        self.shutdown_modules.append(LaunchModule(pid))
        self.shutdown_modules.append(self.lutris_module)
        self.shutdown_modules.append(AnyModule())
        self.shutdown_modules.append(SteamModule())

    def check_is_running(self, check_all: bool = False) -> bool:
        is_running_all = False
        for module in self.shutdown_modules:
            is_running = module.check_is_running()
            if is_running is True:
                if check_all is False:
                    return is_running
                is_running_all = True
        return is_running_all

    def shutdown_game(self) -> None:
        for module in reversed(self.shutdown_modules):
            done = module.shutdown(self.lutris_module.pid)
            if done is True:
                return
