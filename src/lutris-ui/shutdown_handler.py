from __future__ import annotations

from datetime import datetime
from os import X_OK, access, getuid, path
from subprocess import run

import psutil


class BaseModule:
    _zero_datetime: datetime = datetime(2000, 1, 1)

    @staticmethod
    def get_env(pid: int):
        try:
            with open(f"/proc/{pid}/environ", "rb") as f:
                env_data = f.read()
                env_vars = dict(
                    var.decode().split("=", 1)
                    for var in env_data.split(b"\0")
                    if b"=" in var
                )
        except Exception as e:
            return {}
        return env_vars

    def __init__(self):
        self.pid: int | None = None
        self.shutdown_sent_time: datetime = self._zero_datetime

    def check_is_running(self) -> bool:
        # Check the launched command is still running
        if self.pid:
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
                self.shutdown_sent_time = self._zero_datetime
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
                    return True  # Wait at least 10 Seconds for app shutdown
                done = False
                for child in root_process.children():
                    print(f"Any shutdown: send kill to {child.pid}")
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
            env_vars = self.get_env(root_pid)
            if env_vars.get("STORE") == "steam":
                if (datetime.now() - self.shutdown_sent_time).total_seconds() < 10:
                    return True  # Wait at least 10 Seconds for Steam client shutdown
                print(f"Steam shutdown: call steam -shutdown")
                run(["steam", "-shutdown"])
                self.shutdown_sent_time = datetime.now()
                return True

        except psutil.NoSuchProcess:
            return True
        return False


class WineModule(BaseModule):
    def __init__(self):
        super().__init__()
        self.wine_shutdown_time: datetime = self._zero_datetime
        self.wineprefix: str | None = None
        self.wineboot: str | None = None
        self.env_vars: dict | None = None
        self.tried = False

    def get_wineboot(self, pid: int) -> None:
        self.env_vars = self.get_env(pid)

        self.wineprefix = self.env_vars.get("WINEPREFIX")
        wine = self.env_vars.get("WINE")
        if self.wineprefix is None or wine is None:
            return

        if wine.endswith("wine"):
            wineboot = f"{wine}boot"
            if path.isfile(wineboot) and access(wineboot, X_OK):
                self.wineboot = wineboot

        if self.wineboot is None:
            r_wine = path.realpath(wine)
            if wine != r_wine:
                wine = r_wine
                if wine.endswith("wine"):
                    wineboot = f"{wine}boot"
                    if path.isfile(wineboot) and access(wineboot, X_OK):
                        self.wineboot = wineboot

    def shutdown(self, root_pid: int) -> bool:
        if root_pid is None:
            return False
        if self.wineboot is None:
            self.get_wineboot(root_pid)
        if self.wineboot is None:
            try:
                root_process = psutil.Process(root_pid)
                for child in root_process.children():
                    self.get_wineboot(child.pid)
                    if self.wineboot:
                        break
            except psutil.NoSuchProcess:
                pass

        if self.wineboot is None:
            return False

        if self.tried:
            if (datetime.now() - self.wine_shutdown_time).total_seconds() > 15:
                return False  # Give up after 10 seconds
        else:
            print(f"Wine shutdown: call {self.wineboot} for {self.wineprefix}")
            run(
                [self.wineboot, "--end-session", "--shutdown", "--force", "--kill"],
                env=self.env_vars,
            )

        if self.tried is False:
            self.tried = True
            self.wine_shutdown_time = datetime.now()
        return True


class ShutdownManager:
    def __init__(self, pid: int):
        self.shutdown_modules = []
        self.lutris_module = LutrisModule()  # Lutris process is the root process
        self.shutdown_modules.append(LaunchModule(pid))
        self.shutdown_modules.append(self.lutris_module)
        self.shutdown_modules.append(AnyModule())
        self.shutdown_modules.append(SteamModule())
        self.shutdown_modules.append(WineModule())

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
