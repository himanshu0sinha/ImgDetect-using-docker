import telebot
from loguru import logger
import os
import requests
from collections import Counter

YOLO_URL = 'http://localhost:8081'


class Bot:

    def __init__(self, token):
        self.bot = telebot.TeleBot(token, threaded=False)
        self.bot.set_update_listener(self._bot_internal_handler)

        self.current_msg = None

    def _bot_internal_handler(self, messages):
        """Bot internal messages handler"""
        for message in messages:
            self.current_msg = message
            self.handle_message(message)

    def start(self):
        """Start polling msgs from users, this function never returns"""
        logger.info(f'{self.__class__.__name__} is up and listening to new messages....')
        logger.info(f'Telegram Bot information\n\n{self.bot.get_me()}')

        self.bot.infinity_polling()

    def send_text(self, text):
        self.bot.send_message(self.current_msg.chat.id, text)

    def send_text_with_quote(self, text, message_id):
        self.bot.send_message(self.current_msg.chat.id, text, reply_to_message_id=message_id)

    def is_current_msg_photo(self):
        return self.current_msg.content_type == 'photo'

    def download_user_photo(self, quality=2):
        """
        Downloads the photos that sent to the Bot to `photos` directory (should be existed)
        :param quality: integer representing the file quality. Allowed values are [0, 1, 2]
        :return:
        """
        if not self.is_current_msg_photo():
            raise RuntimeError(
                f'Message content of type \'photo\' expected, but got {self.current_msg.content_type}')

        file_info = self.bot.get_file(self.current_msg.photo[quality].file_id)
        data = self.bot.download_file(file_info.file_path)
        folder_name = file_info.file_path.split('/')[0]

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        with open(file_info.file_path, 'wb') as photo:
            photo.write(data)

        return file_info.file_path

    def handle_message(self, message):
        """Bot Main message handler"""
        logger.info(f'Incoming message: {message}')
        self.send_text(f'Your original message: {message.text}')


class QuoteBot(Bot):
    def handle_message(self, message):
        logger.info(f'Incoming message: {message}')

        if message.text != 'Please don\'t quote me':
            self.send_text_with_quote(message.text, message_id=message.message_id)


class ObjectDetectionBot(Bot):
    def handle_message(self, message):
        logger.info(f'Incoming message: {message}')

        if self.is_current_msg_photo():
            photo_path = self.download_user_photo()
            logger.info(f'Photo downloaded: {photo_path}')

            # Send the photo to the YOLO5 service for object detection
            try:
                with open(photo_path, 'rb') as photo_file:
                    files = {'file': photo_file}
                    response = requests.post(f'{YOLO_URL}/predict', files=files)

                    if response.status_code == 200:
                        # Process the response from the YOLO5 service and send the detected objects to the user
                        objects = response.json()
                        if objects:
                            self.send_text('Detected objects:')
                            object_counts = Counter(objects)
                            for obj, count in object_counts.items():
                                self.send_text(f'{obj}: {count} instances')
                        else:
                            self.send_text('No objects detected.')
                    else:
                        self.send_text('Failed to perform object detection.')
            except Exception as e:
                logger.error(f'Error during object detection: {e}')
                self.send_text('Error occurred during object detection.')
        else:
            self.send_text('Please send a photo for object detection.')


if __name__ == '__main__':
    # TODO - in the 'polyBot' dir, create a file called .telegramToken and store your bot token there.
    #  ADD THE .telegramToken FILE TO .gitignore, NEVER COMMIT IT!!!
    with open('.telegramToken') as f:
        _token = f.read()

    my_bot = Bot(_token)
    my_bot.start()
