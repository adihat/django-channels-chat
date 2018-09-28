from channels.layers import get_channel_layer
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe
from asgiref.sync import async_to_sync

from chat.helpers import convert_datetime_to_different_timezone, UTC_TIMEZONE, INDIAN_TIMEZONE, get_str_from_datetime, \
    DATE_TIME_FORMAT
from mysite.settings import MONGO_CLIENT


def index(request):
    return render(request, 'chat/index.html', {})


def room(request, room_name):
    print('inside room view ======>', room_name)
    username = request.session.get('username') or ''
    if not username:
        return HttpResponseRedirect('/login/')
    filters = {'chat_room': room_name, 'deleted': {'$ne': True}}
    sort_fields = [('timestamp', -1)]
    previous_messages = []
    for chat in MONGO_CLIENT['chat_message']['account_1'].find(filters).sort(sort_fields).limit(20):
        chat['_id'] = str(chat['_id'])
        indian_timestamp = convert_datetime_to_different_timezone(chat['timestamp'], UTC_TIMEZONE, INDIAN_TIMEZONE)
        chat['timestamp'] = get_str_from_datetime(indian_timestamp, DATE_TIME_FORMAT)
        chat['message'] = chat['message']['text']
        previous_messages.append(chat)
    previous_messages = sorted(previous_messages, key=lambda s: s['timestamp'])
    print('previous_messages =======>', previous_messages)
    return render(request, 'chat/chat_ui.html', {
        'room_name': room_name,
        'prev_messages': mark_safe(previous_messages),
        'current_user': request.session['username']
    })


def http_view(request):
    return JsonResponse({'message': 'hello world'})


def login(request):
    return render(request, 'chat/login.html', {})


def logged_in(request):
    post_data = request.POST
    print('post_data =====>', post_data)
    username = post_data['username']
    request.session['username'] = username
    return render(request, 'chat/index.html', {'username': username})


def send_data_from_server(request):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)('server_announcements',
                                            {'type': 'chat.message', 'username': 'server', 'outoffocus': True,
                                             'typing': True, 'timestamp': '10:03 PM', 'online': True,
                                             'message': 'hi from server'})
    return JsonResponse({'success': True})


def alarm(request):
    layer = get_channel_layer()
    async_to_sync(layer.group_send)('events', {
        'type': 'events.alarm',
        'content': 'triggered'
    })
    return HttpResponse('<p>Done</p>')
