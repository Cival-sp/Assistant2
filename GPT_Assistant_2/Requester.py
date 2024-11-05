import json
import time
import mimetypes
from requests_toolbelt import MultipartEncoder
from flask import request, make_response, g
from GPT_Assistant_2.Assistant_core import AssistantRequest, AssistantAnswer
from Utility import File


class RequestFormatter:

    @staticmethod
    def to_assistant_request(flask_request: request, g) -> AssistantRequest:
        result = AssistantRequest(user_id=g.user.user_id, )
        if g.user:
            result.user_id = g.user.user_id
        if request.files['file']:
            result.file = flask_request.files['file']
        g.start_time = time.time()

        content_type = flask_request.headers.get('Content-Type')
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
            raise Exception("Unknown content type")
        return result

    @staticmethod
    def text_handler(flask_request: request, result_lnk: AssistantRequest):
        result_lnk.message = flask_request.get_data(as_text=True)

    @staticmethod
    def audio_handler(flask_request: request, result_lnk: AssistantRequest):
        if request.files['voice']:
            result_lnk.is_audio_message = True
            result_lnk.voice_data = request.files['voice']
        else:
            pass

    @staticmethod
    def image_handler(flask_request: request, result_lnk: AssistantRequest):
        pass

    @staticmethod
    def video_handler(flask_request: request, result_lnk: AssistantRequest):
        pass

    @staticmethod
    def json_handler(flask_request: request, result_lnk: AssistantRequest):
        result_lnk.file = flask_request.get_json()
        result_lnk.file_type = "json"

    @staticmethod
    def multipart_handler(flask_request: request, result_lnk: AssistantRequest):
        pass

    @staticmethod
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
