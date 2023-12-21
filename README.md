# Object Detection Docker Project

## Services
- yolov5 - object detection AI model
- polybot - The Telegram app is a flask-based service that responsible for providing a chat-based interface for users to interact with your image object detection functionality. It utilizes the Telegram Bot API to receive user images and respond with detected objects.

## Usage
When a user sends a message to the bot, telegram servers forward the message to the Python app. The Python app processes the message, executes the desired logic, and may send a response back to Telegram servers, which then delivers the response to the user.
To start the application run the "runDockerCompose.sh" script which will do docker-compose up, initiate the replica set and run Ngrok.

## Example
![image](https://github.com/ShirinLabay/projectDocker/assets/62480878/63ca5491-24a1-4f3f-a0cd-4b4aea125142)



