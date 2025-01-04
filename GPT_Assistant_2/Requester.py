import json
import time
import mimetypes
from requests_toolbelt import MultipartEncoder
from flask import request, make_response, g
from GPT_Assistant_2.Assistant_core import AssistantRequest, AssistantAnswer
from Utility import File
from Logger import Logger


class RequestFormatter:
    """
    Класс преобразует Запросы flask в запросы AssistantRequest
    """

    @staticmethod
    @Logger.log_call
    def to_assistant_request(flask_request: request, g) -> AssistantRequest:
        try:
            result = AssistantRequest(message=None, user_id=g.user.user_id)
            result.user = g.user
            file = flask_request.files.get('file')
            if file:
                print(f"{result.file}")
                result.file = file
            content_type = flask_request.headers.get('Content-Type')
            print(f"Content_type={content_type}")
            if content_type == "text/plain":
                RequestFormatter.text_handler(flask_request, result)
            elif content_type == "application/json":
                RequestFormatter.json_handler(flask_request, result)
            elif content_type.startswith("multipart/form-data"):
                RequestFormatter.multipart_handler(flask_request, result)
            elif content_type.startswith("audio"):
                RequestFormatter.audio_handler(flask_request, result)
            elif content_type.startswith("image"):
                RequestFormatter.image_handler(flask_request, result)
            elif content_type.startswith("video"):
                RequestFormatter.video_handler(flask_request, result)
            else:
                raise Exception("Unknown content type")
            return result
        except Exception as e:
            print(e)

    @staticmethod
    @Logger.log_call
    def text_handler(flask_request: request, result_lnk: AssistantRequest):
        # result_lnk.message = flask_request.get_data(as_text=True)
        result_lnk.message = flask_request.data.decode('utf-8')
        return result_lnk.message

    @staticmethod
    @Logger.log_call
    def audio_handler(flask_request: request, result_lnk: AssistantRequest):
        if request.files['voice']:
            result_lnk.is_audio_message = True
            result_lnk.voice_data = request.files['voice']
        else:
            pass

    @staticmethod
    @Logger.log_call
    def image_handler(flask_request: request, result_lnk: AssistantRequest):
        pass

    @staticmethod
    @Logger.log_call
    def video_handler(flask_request: request, result_lnk: AssistantRequest):
        pass

    @staticmethod
    @Logger.log_call
    def json_handler(flask_request: request, result_lnk: AssistantRequest):
        result_lnk.file = flask_request.get_json()
        result_lnk.file_type = "json"

    @staticmethod
    @Logger.log_call
    def multipart_handler(flask_request: request, result_lnk: AssistantRequest):
        if 'voice' in request.files:
            result_lnk.is_audio_message = True
            result_lnk.voice_data = RequestFormatter.make_file(request, 'voice')
            return result_lnk


    @staticmethod
    @Logger.log_call
    def make_file(flask_request: request, key='file') -> File:
        if key not in request.files or not request.files[key]:
            raise Exception("No file found")
        file = request.files[key]
        if file.filename == '':
            raise Exception("Filename not found")
        full_filename = file.filename
        filename, file_extension = full_filename.rsplit('.', 1)
        file_body = file.read()
        return File(filename, file_extension, file_body)


    @staticmethod
    @Logger.log_call
    def make_flask_response(assistant_output: AssistantAnswer):
        """
        Метод преобразует AssistantAnswer в flask response.
        :param assistant_output:
        :return: flask response with content type: multipart/form-data including keys: 'json', 'file'(optionally) ,'voice'(optionally)
        """
        multipart_content = None
        try:
            #Json handler -> 'json' key
            json_dict = {
                'text': assistant_output.text,
                'file_type': assistant_output.file_type,
                'processing_time': time.time() - g.start_time,
                'continue_conversation': assistant_output.continue_conversation,
            }
            #Voice handler -> response with form_data Обработчик голосовых сообщений
            if assistant_output.voice_file: #Здесь мы должны оказаться если ответ был озвучен
                multipart_content = MultipartEncoder(
                    fields={
                        'json': ('json', json.dumps(json_dict), 'application/json'),
                        'voice': (
                            assistant_output.voice_file.name  + assistant_output.voice_file.extension, assistant_output.voice_file.body,
                            'audio/' + assistant_output.voice_file.extension)
                    })
            #File handler -> response with form_data  Обработчик файлов
            elif assistant_output.file is not None and assistant_output.file_type != "Voice":
                multipart_content = MultipartEncoder(
                    fields={
                        'json': ('json', json.dumps(json_dict), 'application/json'),
                        'file': (
                            assistant_output.file.name + '.' + assistant_output.file.extension, assistant_output.file.body,
                            mimetypes.guess_type(assistant_output.file.extension)),
                    })
            else:
                multipart_content = MultipartEncoder(
                    fields={
                        'json': ('json', json.dumps(json_dict), 'application/json'),
                    })

        except Exception as e:
            print(f"Во время обработки запроса для user_id= {g.user}, произошла ошибка {e}")
        finally:
            #Проверяем корректность формирования ответа
            if not multipart_content:
                flask_response = make_response("Internal Server Error")
                flask_response.status_code = 500
                return flask_response
            #Если запрос успешно обработан
            else:
                flask_response = make_response(multipart_content.to_string())
                flask_response.content_type = 'multipart/form-data'
                flask_response.status_code = 200
            return flask_response
