"""Machine profile for measurement records (OS, CPU, cores/threads, RAM, free disk)."""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
from functools import lru_cache
from typing import Any

from .paths import repo_root

_PS_SCRIPT = (
    "$ErrorActionPreference='Stop';"
    "[Console]::OutputEncoding=[System.Text.Encoding]::UTF8;"
    "$c=Get-CimInstance Win32_Processor | Select-Object -First 1 Name,NumberOfCores,NumberOfLogicalProcessors;"
    "$cs=Get-CimInstance Win32_ComputerSystem | Select-Object TotalPhysicalMemory;"
    "$os=Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,BuildNumber;"
    "[pscustomobject]@{cpu=$c.Name;cores=$c.NumberOfCores;threads=$c.NumberOfLogicalProcessors;"
    "ram=$cs.TotalPhysicalMemory;os=$os.Caption;os_version=$os.Version;build=$os.BuildNumber} | ConvertTo-Json -Compress"
)


def _windows_cim() -> dict[str, Any]:
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", _PS_SCRIPT],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=True,
        ).stdout.strip()
        return json.loads(out) if out else {}
    except (OSError, subprocess.SubprocessError, ValueError):
        return {}


def _linux_cpu_model() -> str | None:
    try:
        with open("/proc/cpuinfo", encoding="utf-8") as fh:
            for line in fh:
                if line.lower().startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return None


def _linux_ram_bytes() -> int | None:
    try:
        with open("/proc/meminfo", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("MemTotal:"):
                    return int(line.split()[1]) * 1024
    except (OSError, ValueError):
        pass
    return None


def _gb(n: int | float | None) -> str | None:
    return None if n is None else f"{n / 1024**3:.1f}"


@lru_cache(maxsize=1)
def machine_profile() -> dict[str, Any]:
    """Collect the machine profile once per process. Missing fields are None, never guessed."""
    prof: dict[str, Any] = {
        "os": f"{platform.system()} {platform.release()}",
        "os_version": platform.version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "cpu_model": platform.processor() or None,
        "cpu_cores_physical": None,
        "cpu_threads_logical": os.cpu_count(),
        "ram_total_bytes": None,
        "ram_total_gb": None,
        "disk_free_bytes": None,
        "disk_free_gb": None,
        "disk_total_gb": None,
        "python": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "source": "platform",
    }
    if platform.system() == "Windows":
        cim = _windows_cim()
        if cim:
            prof["source"] = "platform+cim"
            prof["os"] = cim.get("os") or prof["os"]
            prof["os_version"] = f"{cim.get('os_version')} (build {cim.get('build')})"
            prof["cpu_model"] = (cim.get("cpu") or "").strip() or prof["cpu_model"]
            prof["cpu_cores_physical"] = cim.get("cores")
            prof["cpu_threads_logical"] = cim.get("threads") or prof["cpu_threads_logical"]
            prof["ram_total_bytes"] = int(cim["ram"]) if cim.get("ram") else None
    elif platform.system() == "Linux":
        prof["cpu_model"] = _linux_cpu_model() or prof["cpu_model"]
        prof["ram_total_bytes"] = _linux_ram_bytes()
    prof["ram_total_gb"] = _gb(prof["ram_total_bytes"])
    try:
        du = shutil.disk_usage(repo_root())
        prof["disk_free_bytes"] = du.free
        prof["disk_free_gb"] = _gb(du.free)
        prof["disk_total_gb"] = _gb(du.total)
    except OSError:
        pass
    return prof
