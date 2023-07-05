import telebot
from loguru import logger
import os
import requests

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

    def send_text(self, chat_id, text):
        self.bot.send_message(chat_id, text)

    def send_text_with_quote(self, chat_id, text, message_id):
        self.bot.send_message(chat_id, text, reply_to_message_id=message_id)

    def is_current_msg_photo(self):
        return self.current_msg.content_type == 'photo'

    def download_user_photo(self, quality=2):
        """
        Downloads the photos that sent to the Bot to `photos` directory (should be existed)
        :param quality: integer representing the file quality. Allowed values are [0, 1, 2]
        :return:
        """
        if not self.is_current_msg_photo():
            raise RuntimeError(f'Message content of type \'photo\' expected, but got {self.current_msg.content_type}')

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
        self.send_text(message.chat.id, f'Your original message: {message.text}')


class QuoteBot(Bot):
    def handle_message(self, message):
        logger.info(f'Incoming message: {message}')
        if message.text != 'Please don\'t quote me':
            self.send_text_with_quote(message.chat.id, message.text, message_id=message.message_id)


class ObjectDetectionBot(Bot):
    def handle_message(self, message):
        logger.info(f'Incoming message: {message}')

        if message.content_type == 'photo':
            file_path = self.download_user_photo()
            detected_objects = self.detect_objects(file_path)

            if detected_objects:
                object_names = ", ".join(detected_objects)
                response_text = f"Detected objects: {object_names}"
                self.send_text_with_quote(message.chat.id, response_text, message_id=message.message_id)
            else:
                self.send_text_with_quote(message.chat.id, "No objects detected in the image.", message_id=message.message_id)
        else:
            self.send_text_with_quote(message.chat.id, message.text, message_id=message.message_id)

    def detect_objects(self, image_file_path):
        # Implement the logic to send the image to the yolo5 service and get the detected objects
        # Use the requests library to communicate with the yolo5 service
        # Parse the response and extract the detected objects

        # For example:
        yolo5_url = f"{YOLO_URL}/detect"
        files = {"image": open(image_file_path, "rb")}
        response = requests.post(yolo5_url, files=files)

        if response.status_code == 200:
            detected_objects = response.json()
            return detected_objects
        else:
            # Handle error cases if necessary
            return []


if __name__ == '__main__':
    # TODO - in the 'polyBot' dir, create a file called .telegramToken and store your bot token there.
    #  ADD THE .telegramToken FILE TO .gitignore, NEVER COMMIT IT!!!
    with open('.telegramToken') as f:
        _token = f.read()

    my_bot = ObjectDetectionBot(_token)
    my_bot.start()
