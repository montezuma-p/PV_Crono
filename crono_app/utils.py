# -*- coding: utf-8 -*-
# utils.py


from datetime import timedelta

def formatar_timedelta(td: timedelta | None) -> str:
    """Formata um objeto timedelta para a string HH:MM:SS.ms com precisão."""
    if td is None:
        return ""

    total_seconds = td.total_seconds()
    sign = "" if total_seconds >= 0 else "-"
    total_seconds = abs(total_seconds)

    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds_total = divmod(remainder, 60)
    seconds = int(seconds_total)
    milliseconds = int((seconds_total - seconds) * 1000)

    return f"{sign}{int(hours):02d}:{int(minutes):02d}:{seconds:02d}.{milliseconds:03d}"