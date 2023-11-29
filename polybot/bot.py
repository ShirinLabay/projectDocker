import boto3
import requests
import telebot
from loguru import logger
import os
import time
from telebot.types import InputFile


class Bot:

    def __init__(self, token, telegram_chat_url):
        # create a new instance of the TeleBot class.
        # all communication with Telegram servers are done using self.telegram_bot_client
        self.telegram_bot_client = telebot.TeleBot(token)

        # remove any existing webhooks configured in Telegram servers
        self.telegram_bot_client.remove_webhook()
        time.sleep(0.5)

        # set the webhook URL
        self.telegram_bot_client.set_webhook(url=f'{telegram_chat_url}/{token}/', timeout=60)

        logger.info(f'Telegram Bot information\n\n{self.telegram_bot_client.get_me()}')

    def send_text(self, chat_id, text):
        self.telegram_bot_client.send_message(chat_id, text)

    def send_text_with_quote(self, chat_id, text, quoted_msg_id):
        self.telegram_bot_client.send_message(chat_id, text, reply_to_message_id=quoted_msg_id)

    def is_current_msg_photo(self, msg):
        return 'photo' in msg

    def download_user_photo(self, msg):
        """
        Downloads the photos that sent to the Bot to `photos` directory (should be existed)
        :return:
        """
        if not self.is_current_msg_photo(msg):
            raise RuntimeError(f'Message content of type \'photo\' expected')

        file_info = self.telegram_bot_client.get_file(msg['photo'][-1]['file_id'])
        data = self.telegram_bot_client.download_file(file_info.file_path)
        folder_name = file_info.file_path.split('/')[0]

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        with open(file_info.file_path, 'wb') as photo:
            photo.write(data)

        return file_info.file_path

    def send_photo(self, chat_id, img_path):
        if not os.path.exists(img_path):
            raise RuntimeError("Image path doesn't exist")

        self.telegram_bot_client.send_photo(
            chat_id,
            InputFile(img_path)
        )

    def handle_message(self, msg):
        """Bot Main message handler"""
        logger.info(f'Incoming message: {msg}')
        self.send_text(msg['chat']['id'], f'Your original message: {msg["text"]}')


class QuoteBot(Bot):
    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')

        if msg["text"] != 'Please don\'t quote me':
            self.send_text_with_quote(msg['chat']['id'], msg["text"], quoted_msg_id=msg["message_id"])


class ObjectDetectionBot(Bot):

    aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
    aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']

    def handle_message(self, msg):
        bucket_name = os.environ['BUCKET_NAME']
        logger.info(f'Incoming message: {msg}')

        try:
            if self.is_current_msg_photo(msg):
                s3=boto3.client('s3')
                logger.info(f'photo')
                # TODO download the user photo (utilize download_user_photo)
                img_path = self.download_user_photo(msg)
                obj_name = img_path.split('/')[1]
                # TODO upload the photo to S3
                s3.upload_file(img_path,bucket_name,obj_name)
                logger.info(f'successfully uploaded to s3')
                # TODO send a request to the `yolo5` service for prediction
                response = requests.post(f"http://docker-p:8081/predict?imgName={obj_name}")
                predictions = response.json()['labels']
                detected_objects = {}
                for predict in predictions:
                    object_name = predict['class']
                    if object_name in detected_objects:
                        detected_objects[object_name] += 1
                    else:
                        detected_objects[object_name] = 1
                text = 'Detected objects:\n' + '\n'.join(f'{key}: {value}' for key, value in detected_objects.items())
                self.send_text(msg['chat']['id'], {text})

            elif "text" in msg:
                self.send_text(msg['chat']['id'], f'your message: {msg["text"]}')

            else:
                self.send_text(msg['chat']['id'])
        except Exception as e:
            logger.error(f'Error processing message: {e}')
            error_message = "An error occurred while processing your request. Please try again later."
            self.send_text(msg['chat']['id'], error_message)

