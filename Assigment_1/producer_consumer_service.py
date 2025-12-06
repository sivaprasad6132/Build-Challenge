"""
Implements a classic Producer–Consumer workflow using threads and a
custom bounded blocking queue.
"""

import threading
import logging
from typing import Iterable, List, Any

from synchronized_queue import BoundedBlockingQueue

# Sentinel (poison pill) object used to signal the consumer to stop.
# We use a unique object() instance instead of a regular value like None
# to avoid accidentally colliding with real data items.
SENTINEL = object()

# --------------------------------------------------------------------
# Logging Configuration
# --------------------------------------------------------------------
# Configure root logging for this module:
# - INFO level provides good visibility into producer/consumer behavior
# - Format includes timestamp, thread name, and log level
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)s] %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


class Producer(threading.Thread):
    """
    Producer thread implementation.

    Responsibilities:
    - Iterate over a source container (any iterable)
    - Put each item into the shared BoundedBlockingQueue
    - Send a sentinel when all items have been produced to signal completion

    The queue's put() method is blocking, so if the queue is full,
    the producer thread will wait until the consumer removes items.
    """

    def __init__(self, source: Iterable[Any], queue: BoundedBlockingQueue) -> None:
        """
        :param source: Iterable containing items to be produced.
        :param queue: Shared BoundedBlockingQueue instance used for handoff.
        """
        super().__init__(name="ProducerThread")
        self._source = source
        self._queue = queue

    def run(self) -> None:
        """Entry point for the producer thread."""
        logger.info("Producer started")

        # Produce each item from the source and put it into the queue.
        for item in self._source:
            logger.info("Producing item: %s", item)

            # This call may block if the queue is currently full.
            self._queue.put(item)
            logger.info("Item %s added to queue", item)

        # After producing all items, send a sentinel to notify the consumer(s)
        # that no more data will be produced.
        logger.info("Producer sending SENTINEL and shutting down")
        self._queue.put(SENTINEL)


class Consumer(threading.Thread):
    """
    Consumer thread implementation.

    Responsibilities:
    - Continuously read items from the shared BoundedBlockingQueue
    - Append each non-sentinel item to the destination list
    - Stop cleanly when the sentinel is received

    The queue's get() method is blocking, so if the queue is empty,
    the consumer thread will wait until the producer adds items.
    """

    def __init__(self, queue: BoundedBlockingQueue, destination: List[Any]) -> None:
        """
        :param queue: Shared BoundedBlockingQueue instance to consume from.
        :param destination: List used as the destination container where
                            consumed items are stored.
        """
        super().__init__(name="ConsumerThread")
        self._queue = queue
        self._destination = destination

    def run(self) -> None:
        """Entry point for the consumer thread."""
        logger.info("Consumer started")

        while True:
            # This call may block if the queue is currently empty.
            item = self._queue.get()

            # Check for sentinel indicating that production is finished.
            if item is SENTINEL:
                logger.info("Consumer received SENTINEL, exiting")

                # Put the sentinel back for any additional consumers that may
                # also be listening on the same queue (supports scalability).
                self._queue.put(SENTINEL)
                break

            # Normal item: process (here we simply append to the destination).
            logger.info("Consuming item: %s", item)
            self._destination.append(item)

        logger.info("Consumer stopped cleanly")


def run_pipeline(source_container: Iterable[Any], max_queue_size: int = 3) -> list:
    """
    Helper function that wires together the Producer and Consumer and
    runs the producer–consumer pipeline end-to-end.

    :param source_container: Iterable representing the source data container.
    :param max_queue_size: Maximum capacity of the bounded blocking queue.
                           A smaller capacity increases contention and
                           more clearly exercises blocking behavior.
    :return: The destination list containing all consumed items.
    """
    logger.info("Initializing Producer-Consumer pipeline")

    # Shared bounded blocking queue used for thread-safe handoff.
    queue = BoundedBlockingQueue(max_queue_size)

    # Destination container where the consumer will store processed items.
    destination_container: list = []

    # Instantiate the producer and consumer threads.
    producer = Producer(source_container, queue)
    consumer = Consumer(queue, destination_container)

    # Start both threads.
    producer.start()
    consumer.start()

    # Wait for both threads to finish.
    producer.join()
    consumer.join()

    logger.info("Pipeline execution completed")
    logger.info("Final destination container: %s", destination_container)

    return destination_container


if __name__ == "__main__":
    sample_source = [1, 2, 3, 4, 5]
    run_pipeline(sample_source)
