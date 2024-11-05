from flask import Flask, jsonify, request, g
import base64
from GPT_Assistant_2.Assistant_core import SessionManager, AssistantLogic
from GPT_Assistant_2.Command_processor import CommandProcessor
from GPT_Assistant_2.Database_module import Database, FileDatabase
from GPT_Assistant_2.User_module import UserManager, User, Permission
from STT_module import SttInterface, OpenAiStt
from TTS_module import TtsInterface, OpenAiTTS
from Requester import RequestFormatter

AiServer = Flask(__name__)

database = FileDatabase()
session_manager = SessionManager(60 * 3, 5, database)
command_processor = CommandProcessor()
stt_service = OpenAiStt()
tts_service = OpenAiTTS()
assistant_core = AssistantLogic(command_processor, session_manager, stt_service, tts_service, database)


@AiServer.before_request
def request_pre_handler():
    user = auth_check(request)
    if user:
        g.user = user
        telegram_id = request.headers.get('tg_id')
        if telegram_id:
            g.tg_id = telegram_id


@AiServer.route('/say', methods=['POST'])
def say():
    if g.user is None:
        return jsonify({'error': 'Authorization failed'}), 401
    if Permission.check(g.user, User.Group.BANNED) or Permission.check(g.user, User.Group.GUEST):
        return jsonify({'error': "User,don't have a permission"}), 403
    assistant_req = RequestFormatter.to_assistant_request(request, g)
    assistant_output = assistant_core.process_session(g.user, assistant_req)



@AiServer.route('/chat', methods=['POST'])
def chat():
    pass


@AiServer.after_request
def after_request(response):
    pass


def load_server_cfg(Filepath=None):
    pass


def environment_init():
    pass


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


def auth_check(req) -> User | None:
    auth_header = req.headers.get('Authorization')
    if not auth_header:
        return None
    # Разделяем заголовок, чтобы выделить тип авторизации и закодированные данные
    # Формат заголовка: "Basic <base64_encoded_credentials>"
    try:
        auth_type, encoded_credentials = auth_header.split(' ')
    except ValueError:
        return None
    if auth_type.lower() != 'basic':
        return None
    # Декодируем base64 в формат "username:password"
    try:
        decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
        username, password = decoded_credentials.split(':')

        user = UserManager.find_user(user_login=username)
        if not verify_password(username, password):
            return None
        return user
    except Exception as e:
        return None


def identify_user(Flask_request):
    client_ip = Flask_request.remote_addr
    client_user_agent = Flask_request.user_agent.string


def main():
    pass
