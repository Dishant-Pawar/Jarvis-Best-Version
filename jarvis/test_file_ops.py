import sys
sys.path.insert(0, 'd:/lasttry')
import warnings
warnings.filterwarnings('ignore')

from jarvis.services.gemini_service import GeminiService
from jarvis.automation.file_manager import FileManager
import os

g = GeminiService()

print('=== Testing commands that failed in logs ===')
for cmd in [
    'open report.pdf',
    'open folders document',
    'create file notes.txt',
    'create folder projects',
    'delete file temp.txt',
    'search files for budget',
    'list desktop',
    'move notes.txt to desktop',
    'rename notes.txt to backup.txt',
    'organize downloads',
    'show recent files',
    'weather in pune',
    'news',
]:
    result = g.parse_intent(cmd)
    intent = result.get('intent', '?')
    action = result.get('action', '?')
    params = result.get('params', {})
    status = 'OK' if intent != 'chat' else 'CHAT'
    print(f'  [{status}] {action} | {params}')
    print(f'         <- "{cmd}"')

print()
print('All done - no crashes = no more text_l errors')
