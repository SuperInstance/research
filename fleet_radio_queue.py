#!/usr/bin/env python3
"""Fleet Radio work-queue — inspired by agent-coordinator.

A persistent task queue with topic-based routing and heartbeat monitoring.
Used to coordinate ZAI/DS/Kimi voices across sessions.
"""
import json
import os
import time
from enum import Enum

class Voice(Enum):
    ZAI = "zai"
    DS = "ds"
    KIMI = "kimi"
    CURATED = "curated"

class Status(Enum):
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"

class TaskQueue:
    def __init__(self, path: str = '/workspace/research/fleet_radio_queue.json'):
        self.path = path
        self.tasks = self._load()

    def _load(self):
        if os.path.exists(self.path):
            return json.load(open(self.path))
        return {'tasks': [], 'version': 1}

    def _save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        json.dump(self.tasks, open(self.path, 'w'), indent=2)

    def enqueue(self, topic: str, voice: Voice, prompt: str, priority: float = 0.5):
        task = {
            'id': f'task-{int(time.time()*1000)}',
            'topic': topic,
            'voice': voice.value,
            'prompt': prompt[:200],
            'priority': priority,
            'status': Status.QUEUED.value,
            'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        }
        self.tasks['tasks'].append(task)
        self._save()
        return task

    def heartbeat(self, task_id: str, status: Status, output: str = ''):
        for t in self.tasks['tasks']:
            if t['id'] == task_id:
                t['status'] = status.value
                t['heartbeat_at'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
                if output:
                    t['output_length'] = len(output)
        self._save()

    def pending(self, voice: Voice = None) -> list:
        result = []
        for t in self.tasks['tasks']:
            if t['status'] == Status.QUEUED.value:
                if voice is None or t['voice'] == voice.value:
                    result.append(t)
        return sorted(result, key=lambda t: -t['priority'])

    def stats(self) -> dict:
        statuses = [t['status'] for t in self.tasks['tasks']]
        from collections import Counter
        return {
            'total': len(self.tasks['tasks']),
            'by_status': dict(Counter(statuses)),
            'by_voice': dict(Counter(t['voice'] for t in self.tasks['tasks'])),
        }

def main():
    q = TaskQueue()
    
    # Add some tasks for next rounds
    q.enqueue('witness_dreams', Voice.ZAI, 'Write Fleet Radio piece on REM cycle', priority=0.9)
    q.enqueue('witness_dreams', Voice.DS, 'Cellular biologist angle on REM cycle', priority=0.7)
    q.enqueue('oracle_heard', Voice.KIMI, 'Code-flavored piece on oracle as API', priority=0.6)
    q.enqueue('phoenix_burn', Voice.CURATED, 'Cross-cut all 10 archetypes in one piece', priority=0.5)
    
    print('=== Fleet Radio Work Queue ===\n')
    print('Pending tasks by voice:')
    for voice in [Voice.ZAI, Voice.DS, Voice.KIMI, Voice.CURATED]:
        tasks = q.pending(voice)
        print(f'  {voice.value}: {len(tasks)} pending')
        for t in tasks[:3]:
            print(f'    - {t["topic"]} (priority={t["priority"]})')
    print()
    print('Stats:', q.stats())

if __name__ == '__main__':
    main()
