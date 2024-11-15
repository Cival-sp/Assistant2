import json
import time
import mimetypes
from requests_toolbelt import MultipartEncoder
from flask import request, make_response, g
from GPT_Assistant_2.Assistant_core import AssistantRequest, AssistantAnswer
from Utility import File
from Logger import Logger


class RequestFormatter:

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
            print(f"Попытка поулчения content_type")
            content_type = flask_request.headers.get('Content-Type')
            print(f"Content_type={content_type}")
            if content_type == "text/plain":
                RequestFormatter.text_handler(flask_request, result)
            elif content_type == "application/json":
                RequestFormatter.json_handler(flask_request, result)
            elif content_type == "multipart/form-data":
                RequestFormatter.multipart_handler(flask_request, result)
            elif content_type.startswith("audio"):
                RequestFormatter.audio_handler(flask_request, result)
            elif content_type.startswith("image"):
                RequestFormatter.image_handler(flask_request, result)
            elif content_type.startswith("video"):
                RequestFormatter.video_handler(flask_request, result)
            else:
                print("Unknown content type")
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
        pass

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
        multipart_content = None
        json_dict = {
            'text': assistant_output.text,
            'file_type': assistant_output.file_type,
            'processing_time': time.time() - g.start_time,
        }

        if assistant_output.continue_conversation:
            json_dict['continue_conversation'] = assistant_output.continue_conversation

        if assistant_output.file_type == "voice" and assistant_output.file:
            multipart_content = MultipartEncoder(
                fields={
                    'json': ('json', json.dumps(json_dict), 'application/json'),
                    'voice': (
                        assistant_output.file.name + '.' + assistant_output.file.extension, assistant_output.file.body,
                        'audio/' + assistant_output.file.extension)
                })

        if assistant_output.text and not assistant_output.file_type == 'voice':
            multipart_content = MultipartEncoder(
                fields={
                    'json': ('json', json.dumps(json_dict), 'application/json'),
                    'file': (
                        assistant_output.file.name + '.' + assistant_output.file.extension, assistant_output.file.body,
                        mimetypes.guess_type(assistant_output.file.extension)),
                })
        if multipart_content:
            flask_response = make_response(multipart_content.to_string())
        else:
            flask_response = make_response()
        flask_response.content_type = 'multipart/form-data'
        flask_response.status_code = 200

        return flask_response
