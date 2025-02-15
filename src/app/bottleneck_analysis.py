from src.app import dfg


def show(full_log, filtered_log):
    full_log = full_log.copy()

    dfg.show(full_log, filtered_log)
