import click
from confluent_kafka import Consumer, KafkaException, Producer


@click.group()
def cli():
    pass


@cli.command()
@click.option('--message', required=True, help="Message to send")
@click.option('--topic', required=True, help="Kafka topic")
@click.option('--kafka', required=True, help="Kafka bootstrap server (e.g., localhost:9092)")
def produce(message, topic, kafka):
    producer = Producer({'bootstrap.servers': kafka})
    try:
        producer.produce(topic, message)
        producer.flush()
        click.echo(f"Message '{message}' sent to topic '{topic}'")
    except Exception as e:
        click.echo(f"Failed to produce message: {e}")


@cli.command()
@click.option('--topic', required=True, help="Kafka topic")
@click.option('--kafka', required=True, help="Kafka bootstrap server (e.g., localhost:9092)")
def consume(topic, kafka):
    consumer = Consumer({
        'bootstrap.servers': kafka,
        'group.id': 'python-cli-group',
        'auto.offset.reset': 'earliest'
    })
    consumer.subscribe([topic])
    try:
        click.echo(f"Subscribed to topic '{topic}'. Listening for messages...")
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaException._PARTITION_EOF:
                    continue
                else:
                    click.echo(f"Error: {msg.error()}")
                    break
            click.echo(f"Received message: {msg.value().decode('utf-8')}")
    except KeyboardInterrupt:
        click.echo("Exiting consumer...")
    finally:
        consumer.close()


if __name__ == "__main__":
    cli()
