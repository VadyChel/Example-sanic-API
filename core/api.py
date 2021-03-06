import uuid
import hashlib
import re
from .database import Database
from sanic import response, Blueprint

bp = Blueprint("api-v2", url_prefix='/api', version="v2")

messages = {
	"error_valid_json": {
		"message": {
			"error": "There is a valid json data"
		}
	},
	"error_no_user": {
		"message": {
			"error": "There is no such user with such an ID"
		}
	},
	"error_valid_password": {
		"message": {
			"error": "There is a valid password"
		}
	},
	"error_mail_already_in_use": {
		"message": {
			"error": "Specified mail already in use"
		}
	},
	"error_valid_email": {
		"message": {
			"error": "There is a valid email"
		}
	},
	"succefly_create_user": {
		"message": {
			'succefly': 'Creating user was succefly'
		}
	},
	"succefly_delete_user": {
		"message": {
			"succefly": "Deleting user was succefly"
		}
	},
	"succefly_edit_user": {
		"message": {
			"succefly": "Editing user was succefly"
		}
	}
}

@bp.listener('before_server_start')
async def setup_db(app, loop):
    await Database().prepare_to_start()

@bp.get('/users')
async def get_users(request):
	data = await Database().get_users()
	return response.json(data)

@bp.get('/users/<id>')
async def get_user(request, id):
	data = await Database().get_user(user_id=id)
	if data == 1:
		return response.json(messages["error_no_user"])
	return response.json(data)

@bp.post('/users')
async def create_user(request):
	fields = ["password", "name", "email"]
	if request.json is not None:
		if sorted(request.json.keys()) == sorted(fields):
			template = re.compile("(^|\s)[-a-z0-9_.]+@([-a-z0-9]+\.)+[a-z]{2,6}(\s|$)")
			if template.match(request.json.get("email")):
				state = await Database().create_user(
					user_id=str(uuid.uuid4()),
					password=request.json.get("password"),
					user_name=request.json.get("name"),
					user_email=request.json.get("email")
				)
				if state == 1:
					return response.json(messages["error_mail_already_in_use"])
				return response.json(messages["succefly_create_user"])
			else:
				return response.json(messages["error_valid_email"])
		else:
			return response.json(messages["error_valid_json"])
	else:
		return response.json(messages["error_valid_json"])

@bp.delete('/users/<id>')
async def delete_user(request, id):
	if request.json is not None:
		if "password" in request.json.keys():
			state = await Database().delete_user(
				user_id=id,
				password=request.json.get("password")
			)
			if state == 1:
				return response.json(messages["error_no_user"])
			elif state == 2:
				return response.json(messages["error_valid_password"])
			return response.json(messages["succefly_delete_user"])
		else:
			return response.json(messages["error_valid_json"])
	else:
		return response.json(messages["error_valid_json"])
			
@bp.patch('/users/<id>')
async def edit_user(request, id):
	if request.json is not None:
		if "password" in request.json.keys():
			if "email" in request.json.keys():
				template = re.compile("(^|\s)[-a-z0-9_.]+@([-a-z0-9]+\.)+[a-z]{2,6}(\s|$)")
				if not template.match(request.json.get("email")):
					return response.json(messages["error_valid_email"])

			state = await Database().edit_user(
				user_id=id,
				params=request.json
			)
			if state == 1:
				return response.json(messages["error_valid_password"])
			elif state == 2:
				return response.json(messages["error_no_user"])
			return response.json(messages["succefly_edit_user"])
		else:
			return response.json(messages["error_valid_json"])
	else:
		return response.json(messages["error_valid_json"])