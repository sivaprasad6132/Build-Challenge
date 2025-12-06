# test_producer_consumer.py
import time
import unittest
import threading

from blocking_queue import BoundedBlockingQueue
from producer_consumer import run_pipeline, SENTINEL


class TestBoundedBlockingQueue(unittest.TestCase):

    def test_put_and_get_basic(self):
        queue = BoundedBlockingQueue(maxsize=2)
        queue.put(10)
        queue.put(20)
        self.assertEqual(queue.qsize(), 2)
        self.assertTrue(queue.full())

        self.assertEqual(queue.get(), 10)
        self.assertEqual(queue.get(), 20)
        self.assertTrue(queue.empty())

    def test_block_when_full(self):
        """
        Verify that put() blocks when queue is full and resumes
        after a consumer takes an item.
        """
        queue = BoundedBlockingQueue(maxsize=1)
        queue.put("first")  # queue is now full

        unblocked = threading.Event()

        def producer():
            # This should block until consumer takes "first"
            queue.put("second")
            unblocked.set()

        t = threading.Thread(target=producer)
        t.start()

        # Give some time for producer to hit the blocking point
        time.sleep(0.1)
        self.assertFalse(unblocked.is_set(), "Producer should still be blocked")

        # Now consumer removes an item, unblocking the producer
        self.assertEqual(queue.get(), "first")

        # Wait a bit for producer to finish put("second")
        t.join(timeout=1)
        self.assertTrue(unblocked.is_set(), "Producer should have unblocked")
        self.assertEqual(queue.get(), "second")

    def test_block_when_empty(self):
        """
        Verify that get() blocks when queue is empty and resumes
        after a producer puts an item.
        """
        queue = BoundedBlockingQueue(maxsize=1)
        value_holder = {"value": None}

        def consumer():
            value_holder["value"] = queue.get()

        t = threading.Thread(target=consumer)
        t.start()

        # Give some time for consumer to hit the blocking point
        time.sleep(0.1)
        self.assertIsNone(value_holder["value"], "Consumer should be blocked")

        # Now producer puts an item, unblocking the consumer
        queue.put(42)
        t.join(timeout=1)
        self.assertEqual(value_holder["value"], 42)


class TestProducerConsumerPipeline(unittest.TestCase):

    def test_pipeline_moves_all_items_in_order(self):
        source = list(range(10))
        destination = run_pipeline(source, max_queue_size=3)
        self.assertEqual(source, destination)
        self.assertEqual(len(source), len(destination))

    def test_pipeline_handles_empty_source(self):
        source = []
        destination = run_pipeline(source, max_queue_size=2)
        self.assertEqual(destination, [])

    def test_sentinel_stops_consumer(self):
        """
        Directly test sentinel behavior with a consumer.
        """
        queue = BoundedBlockingQueue(maxsize=2)
        destination = []

        from producer_consumer import Consumer

        consumer = Consumer(queue=queue, destination=destination)
        consumer.start()

        # Immediately send sentinel
        queue.put(SENTINEL)
        consumer.join(timeout=1)

        # No items should be consumed; consumer should exit cleanly
        self.assertEqual(destination, [])


if __name__ == "__main__":
    unittest.main()
