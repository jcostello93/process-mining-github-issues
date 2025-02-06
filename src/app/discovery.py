from src.app import bpmn, petri_net


def show(log, filtered_log):
    petri_net.show(log, filtered_log)
    bpmn.show(filtered_log)
