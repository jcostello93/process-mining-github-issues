import json
import os
import time
import argparse
from datetime import datetime
from src.data_pipeline.s3 import fetch_file, upload_file
from pm4py.objects.log.obj import EventLog, Trace, Event
import pm4py

S3_BUCKET = os.environ.get("S3_BUCKET")


def parse_timestamp(timestamp_str):
    try:
        # Convert "Z" to "+00:00" for ISO 8601 compatibility
        if timestamp_str.endswith("Z"):
            timestamp_str = timestamp_str.replace("Z", "+00:00")
        return datetime.fromisoformat(timestamp_str)
    except ValueError as e:
        print(f"Invalid timestamp: {timestamp_str}. Error: {e}")
        return None


def create_xes_log(issues, timelines):
    """
    Create an XES log from issues and timelines using PM4Py.
    :param issues: List of issues.
    :param timelines: Dictionary of issue timelines.
    :return: PM4Py EventLog object.
    """
    log = EventLog()

    # Add global attributes for trace and event
    log.properties = {"concept:name": "name"}

    # Process each issue into a trace
    for issue in issues:
        trace = Trace()
        trace.attributes["concept:name"] = f"Issue {issue['number']}"
        trace.attributes["reactions"] = issue["reactions"]["total_count"]

        # Add creation event
        creation_event = Event()
        creation_event["concept:name"] = "created"
        creation_event["time:timestamp"] = parse_timestamp(issue["created_at"])
        creation_event["org:resource"] = f"User {issue['user']['id']}"
        trace.append(creation_event)

        # Process timeline events
        if str(issue["number"]) in timelines:
            for timeline_event in timelines[str(issue["number"])]:
                event = Event()
                event_name = timeline_event["event"]
                event["time:timestamp"] = parse_timestamp(timeline_event["created_at"])
                event["org:resource"] = (
                    f"User {timeline_event['actor']['id']}"
                    if timeline_event.get("actor")
                    else "Ghost"
                )

                author_map = {
                    "COLLABORATOR": "collaborator",
                    "CONTRIBUTOR": "contributor",
                    "FIRST_TIMER": "first_timer",
                    "FIRST_TIME_CONTRIBUTOR": "first_time_contributor",
                    "MANNEQUIN": "mannequin",
                    "MEMBER": "member",
                    "NONE": "community",
                    "OWNER": "owner",
                }

                if event_name == "labeled":
                    trace.attributes["Label"] = timeline_event["label"]["name"]
                    event["concept:name"] = event_name
                elif event_name == "closed":
                    if timeline_event.get("state_reason"):
                        event["concept:name"] = timeline_event.get("state_reason")
                    elif issue.get("state_reason"):
                        event["concept:name"] = issue.get("state_reason")
                    else:
                        # If there's no state_reason, the issue was reopened
                        event["concept:name"] = "temporarily_closed"
                else:
                    event["concept:name"] = event_name
                    if event.get("author_association"):
                        event["author_association"] = author_map[
                            event["author_association"]
                        ]

                trace.append(event)

        # Append the trace to the log
        sorted_trace = pm4py.objects.log.util.sorting.sort_timestamp_trace(trace)
        log.append(sorted_trace)

    print("XES log creation complete.")
    return log


def main(owner, repo, should_publish):
    """Main function to create and optionally publish the XES log."""
    bucket_name = S3_BUCKET
    issues_file = f"{owner}_{repo}_issues.json"
    timelines_file = f"{owner}_{repo}_timelines.json"

    print("Retrieving issues")
    issues = fetch_file(issues_file, bucket_name, issues_file)
    with open(issues_file, "r", encoding="utf-8") as file:
        issues = json.load(file)
    if issues is None:
        raise ValueError(
            f"Failed to retrieve issues from {issues_file} in bucket {bucket_name}"
        )

    print("Retrieving timelines")
    timelines = fetch_file(timelines_file, bucket_name, issues_file)
    with open(timelines_file, "r", encoding="utf-8") as file:
        timelines = json.load(file)
    if timelines is None:
        raise ValueError(
            f"Failed to retrieve timelines from {timelines_file} in bucket {bucket_name}"
        )

    # Create and save XES log
    start_time = time.time()
    log = create_xes_log(issues, timelines)
    output_file = f"{owner}_{repo}_event_log.xes"
    pm4py.write_xes(log, output_file)
    print(
        f"XES log saved to {output_file}. Time taken: {time.time() - start_time:.2f} seconds."
    )

    # Publish to S3 if requested
    if should_publish:
        print("Uploading XES log to S3...")
        upload_file(output_file, bucket_name, output_file)
        print("XES log successfully uploaded.")
    else:
        print("Publish flag not set. Skipping upload.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Land raw data in S3")
    parser.add_argument("--owner", required=True, help="Owner of the repository")
    parser.add_argument("--repo", required=True, help="Repository name")
    parser.add_argument("--publish", action="store_true", help="Publish the data")
    args = parser.parse_args()
    owner, repo, should_publish = args.owner, args.repo, args.publish

    main(owner, repo, should_publish)
