"""Redis conversation handler for pub/sub messaging."""
import redis


class Conversation:
    def __init__(self, host="localhost", port=6379, channel="canal1"):
        self.messages = []
        self.host = host
        self.port = port
        self.redis_client = redis.StrictRedis(host=host, port=port, db=0)
        self.channel = channel
        self.subscriber = None
        self.should_stop = False

    def clear(self):
        self.messages = []

    async def send(self, message, username="User"):
        formatted_message = f"{username}: {message}"
        self.redis_client.publish(self.channel, formatted_message)
        return formatted_message

    def get_subscriber(self):
        if self.subscriber is None:
            self.subscriber = self.redis_client.pubsub()
            self.subscriber.subscribe(self.channel)
        return self.subscriber

    def change_channel(self, new_channel):
        self.should_stop = True
        if self.subscriber:
            try:
                self.subscriber.unsubscribe(self.channel)
                self.subscriber.close()
            except:
                pass
            self.subscriber = None
        self.channel = new_channel
        self.should_stop = False

    def change_server(self, new_host, new_port=6379):
        self.should_stop = True
        if self.subscriber:
            try:
                self.subscriber.unsubscribe(self.channel)
                self.subscriber.close()
            except:
                pass
            self.subscriber = None
        self.host = new_host
        self.port = new_port
        self.redis_client = redis.StrictRedis(host=new_host, port=new_port, db=0)
        self.should_stop = False
