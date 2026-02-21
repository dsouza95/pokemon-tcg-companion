#!/usr/bin/env python3
"""
Create Pub/Sub topic and push subscription.

Project ID is read from settings (core.settings).
Backend URL can be passed as argument or read from settings.

Usage:
    python scripts/create_topic_sub.py \\
        --topic topic \\
        --subscription topic-sub \\
        --push-endpoint http://host.docker.internal:8000/my-endpoint
"""

import argparse

from google.cloud import pubsub_v1

from core.settings import settings


def create_topic_and_subscription(
    topic_name: str,
    subscription_name: str,
    push_endpoint: str,
):
    """
    Create a Pub/Sub topic and push subscription.

    Args:
        topic_name: Name of the topic to create
        subscription_name: Name of the subscription to create
        push_endpoint: Full URL of the webhook endpoint
    """
    project_id = settings.gcp_pubsub_project
    publisher = pubsub_v1.PublisherClient()
    subscriber = pubsub_v1.SubscriberClient()

    topic_path = publisher.topic_path(project_id, topic_name)
    subscription_path = subscriber.subscription_path(project_id, subscription_name)

    publisher.create_topic(request={"name": topic_path})
    push_config = {"push_endpoint": push_endpoint}

    subscriber.create_subscription(
        request={
            "name": subscription_path,
            "topic": topic_path,
            "push_config": push_config,
        }
    )
    print(f"✓ Created topic: {topic_path}")
    print(f"✓ Created push subscription: {subscription_path}")
    print(f"✓ Push endpoint: {push_endpoint}")


def main():
    parser = argparse.ArgumentParser(
        description="Create Pub/Sub topic and push subscription"
    )
    parser.add_argument(
        "--topic",
        required=True,
        help="Topic name (e.g., topic)",
    )
    parser.add_argument(
        "--subscription",
        required=True,
        help="Subscription name (e.g., topic-sub)",
    )
    parser.add_argument(
        "--push-endpoint",
        required=True,
        help="Push endpoint (e.g., http://host.docker.internal:8000/my-endpoint)",
    )

    args = parser.parse_args()

    create_topic_and_subscription(
        topic_name=args.topic,
        subscription_name=args.subscription,
        push_endpoint=args.push_endpoint,
    )


if __name__ == "__main__":
    main()
