from tools.email_tool import mock_send_email
from tools.time_tool import current_time
from tools.weather_tool import fetch_weather


user_functions = {fetch_weather, current_time, mock_send_email}
