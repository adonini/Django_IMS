import uuid
from django.utils.deprecation import MiddlewareMixin
from django.db import connection

class SetCurrentUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            username = request.user.username
        else:
            username = 'anonymous'

        session_id = str(uuid.uuid4())  # Generates an unique session ID

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO user_context (session_id, current_user_name)
                VALUES (%s, %s)
                ON CONFLICT (session_id)
                DO UPDATE SET current_user_name = EXCLUDED.current_user_name;
            """, [session_id, username])

            # Saves session_id in the session variables on postgre
            cursor.execute("SET session myapp.session_id = %s;", [session_id])

        # Saves the session ID in the request
        request.session_id = session_id

    def process_response(self, request, response):
        if hasattr(request, 'session_id'):
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM user_context WHERE session_id = %s;", [request.session_id])
        return response
