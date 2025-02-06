from src.app import bpmn, petri_net


def show(filtered_log):
    petri_net.show(filtered_log)
    bpmn.show(filtered_log)
