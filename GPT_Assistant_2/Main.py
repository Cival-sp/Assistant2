import sys
import json
import base64
import time
import subprocess
from flask import Flask, jsonify, request, g
from GPT_Assistant_2.Assistant_core import SessionManager, AssistantLogic
from GPT_Assistant_2.Command_processor import CommandProcessor
from GPT_Assistant_2.Database_module import FileDatabase
from GPT_Assistant_2.User_module import UserManager, User, Permission
from STT_module import OpenAiStt
from TTS_module import OpenAiTTS
from Requester import RequestFormatter
from Logger import Logger


@Logger.log_call
def load_server_cfg(filepath="config.json"):
    try:
        with open(filepath, 'r') as config_file:
            config = json.load(config_file)
        return config
    except Exception as e:
        print(f"Ошибка загрузки конфигурации: {e}")
        return {}


@Logger.log_call
def environment_init(config):
    global AiServer, database, session_manager, command_processor, stt_service, tts_service, assistant_core

    AiServer = Flask(__name__)

    database = FileDatabase(config.get("database_path"))
    session_manager = SessionManager(config.get("session_timeout", 180),
                                     config.get("max_sessions", 5), database)
    command_processor = CommandProcessor()
    stt_service = OpenAiStt()
    tts_service = OpenAiTTS()
    assistant_core = AssistantLogic(command_processor, session_manager, stt_service, tts_service, database)


@Logger.log_call
def verify_password(username, password) -> bool:
    try:
        user = UserManager.find_user(user_login=username)
        if user is None:
            return False
        if username == user.authorization_data["login"] and password == user.authorization_data["password"]:
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False


@Logger.log_call
def auth_check(req) -> User | None:
    auth_header = req.headers.get('Authorization')
    if not auth_header:
        return None
    # Формат заголовка: "Basic <base64_encoded_credentials>"
    try:
        auth_type, encoded_credentials = auth_header.split(' ')
    except ValueError:
        return None
    if auth_type.lower() != 'basic':
        return None
    try:
        decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
        username, password = decoded_credentials.split(':')

        user = UserManager.find_user(user_login=username)
        if not verify_password(username, password):
            return None
        return user
    except Exception as e:
        return None


@Logger.log_call
def identify_user(Flask_request):
    client_ip = Flask_request.remote_addr
    client_user_agent = Flask_request.user_agent.string


@Logger.log_call
def main():
    config = load_server_cfg("../Conf/server_config.json")
    environment_init(config)

    @AiServer.before_request
    def request_pre_handler():
        user = auth_check(request)
        if user:
            g.user = user
            telegram_id = request.headers.get('tg_id')
            g.start_time = time.time()
            if telegram_id:
                g.tg_id = telegram_id

    @AiServer.route('/say', methods=['POST'])
    @Logger.log_call
    def say():
        try:
            if g.user is None:
                return jsonify({'error': 'Authorization failed'}), 401
            if Permission.check(g.user, User.Group.BANNED) or Permission.check(g.user, User.Group.GUEST):
                return jsonify({'error': "User,don't have a permission"}), 403
            assistant_req = RequestFormatter.to_assistant_request(request, g)
            assistant_output = assistant_core.process_session(assistant_req)
            return RequestFormatter.make_flask_response(assistant_output)
        except Exception as e:
            print(e)
            return jsonify({'error': str(e)}), 500

    @AiServer.after_request
    def after_request(response):
        pass

    @AiServer.route('/shutdown', methods=['POST'])
    def shutdown():
        if Permission.check(g.user, User.Group.ADMIN) or Permission.check(g.user, User.Group.OWNER):
            print("Остановка сервера")
            sys.exit(0)
        else:
            return jsonify({'error': 'Authorization failed'}), 401

    @AiServer.route('/restart', methods=['POST'])
    def restart():
        if Permission.check(g.user, User.Group.ADMIN) or Permission.check(g.user, User.Group.OWNER):
            print("Перезапуск сервера")
            subprocess.Popen([sys.executable] + sys.argv)
            sys.exit(0)
        else:
            return jsonify({'error': 'Authorization failed'}), 401

    AiServer.run(host=config.get("host", "127.0.0.1"), port=config.get("port", 5000))


if __name__ == '__main__':
    main()
