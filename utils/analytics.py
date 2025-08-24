import time
import json
from datetime import datetime

class Analytics:
    def __init__(self):
        self.research_sessions = []
    
    def start_session(self, query: str):
        session = {
            'id': f"session_{int(time.time())}",
            'query': query,
            'start_time': datetime.now().isoformat(),
            'status': 'running',
            'steps_completed': []
        }
        self.research_sessions.append(session)
        return session['id']
    
    def log_step(self, session_id: str, step_name: str, status: str = 'completed'):
        for session in self.research_sessions:
            if session['id'] == session_id:
                session['steps_completed'].append({
                    'step': step_name,
                    'status': status,
                    'timestamp': datetime.now().isoformat()
                })
                break
    
    def complete_session(self, session_id: str, status: str = 'completed'):
        for session in self.research_sessions:
            if session['id'] == session_id:
                session['end_time'] = datetime.now().isoformat()
                session['status'] = status
                break
    
    def get_stats(self):
        completed = sum(1 for s in self.research_sessions if s['status'] == 'completed')
        failed = sum(1 for s in self.research_sessions if s['status'] == 'failed')
        return {
            'total_sessions': len(self.research_sessions),
            'completed': completed,
            'failed': failed,
            'success_rate': completed / len(self.research_sessions) * 100 if self.research_sessions else 0
        }