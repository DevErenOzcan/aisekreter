from channels.generic.websocket import AsyncWebsocketConsumer
import json

class AudioStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'audio_room'
        await self.accept()

    async def disconnect(self, close_code):
        pass  # You can handle cleanup here

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            # Handle text messages (if needed)
            data = json.loads(text_data)
            await self.send(text_data=json.dumps({
                'message': 'Text data received'
            }))

        if bytes_data:
            # Handle binary (audio) data
            print("Received binary audio data:", len(bytes_data), "bytes")

            # Process or save the received audio data (optional)
            # Example: Save to a file
            # with open("received_audio.raw", "ab") as f:
            #     f.write(bytes_data)

            await self.send(text_data=json.dumps({
                'message': 'Binary audio data received'
            }))
