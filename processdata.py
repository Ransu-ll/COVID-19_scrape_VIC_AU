import scrapedata as scr


def analysis_total(file: str, column: scr.ColNames):
    raw = scr.take_info(file, column)
    total = 0
    for val in raw.values():
        total += val
    return total
