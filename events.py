
import queue
import threading

# Local message queue
event_queue = queue.Queue()


def process_events():
    while True:
        event = event_queue.get()

        try:
            handle_donation_event(event)
        finally:
            event_queue.task_done()


def handle_donation_event(event):
    print(
        f"[EVENT PROCESSED] New donation: "
        f"{event['title']} (ID: {event['donation_id']})"
    )


def start_event_worker():
    worker = threading.Thread(
        target=process_events,
        daemon=True
    )
    worker.start()


def publish_donation_event(donation_id, title):
    event = {
        "donation_id": donation_id,
        "title": title
    }

    event_queue.put(event)
    print(f"[EVENT PUBLISHED] {event}")
