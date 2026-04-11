"""File-based JSONL job queue for batch processing."""

import fcntl
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional


class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    REVIEW_PENDING = "review_pending"


@dataclass
class Job:
    """A single job in the queue."""
    id: str
    input_type: str = ""         # "url", "file", "text"
    input_ref: str = ""          # URL, file path, or text
    status: str = JobStatus.PENDING.value
    config_overrides: dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result_path: Optional[str] = None
    error: Optional[str] = None
    retry_count: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    def to_jsonl(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


class JobQueue:
    """File-based job queue using JSONL."""

    def __init__(self, queue_dir: str):
        self.queue_dir = Path(queue_dir)
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        self.queue_file = self.queue_dir / "queue.jsonl"
        self.lock_file = self.queue_dir / "queue.lock"

    def enqueue(self, job: Job) -> str:
        """Add a job to the queue."""
        with self._lock():
            with open(self.queue_file, "a", encoding="utf-8") as f:
                f.write(job.to_jsonl() + "\n")
        return job.id

    def dequeue(self, limit: int = 10) -> List[Job]:
        """Get pending jobs up to limit."""
        jobs = []
        for job in self._read_all():
            if job.status == JobStatus.PENDING.value:
                jobs.append(job)
                if len(jobs) >= limit:
                    break
        return jobs

    def update(self, job_id: str, status: JobStatus, **kwargs):
        """Update a job's status."""
        with self._lock():
            jobs = self._read_all_raw()
            updated = []
            for line in jobs:
                data = json.loads(line)
                if data["id"] == job_id:
                    data["status"] = status.value
                    if status == JobStatus.RUNNING:
                        data["started_at"] = datetime.now().isoformat()
                    if status in (JobStatus.COMPLETED, JobStatus.FAILED):
                        data["completed_at"] = datetime.now().isoformat()
                    data.update(kwargs)
                updated.append(json.dumps(data, ensure_ascii=False))

            with open(self.queue_file, "w", encoding="utf-8") as f:
                f.write("\n".join(updated) + "\n")

    def list_jobs(self, status: Optional[JobStatus] = None) -> List[Job]:
        """List all jobs, optionally filtered by status."""
        jobs = self._read_all()
        if status:
            jobs = [j for j in jobs if j.status == status.value]
        return jobs

    def clear(self):
        """Clear completed and failed jobs."""
        with self._lock():
            jobs = self._read_all_raw()
            remaining = []
            for line in jobs:
                data = json.loads(line)
                if data["status"] in (JobStatus.PENDING.value, JobStatus.RUNNING.value):
                    remaining.append(line)
            with open(self.queue_file, "w", encoding="utf-8") as f:
                f.write("\n".join(remaining))
                if remaining:
                    f.write("\n")

    def _read_all(self) -> List[Job]:
        """Read all jobs from queue file."""
        if not self.queue_file.exists():
            return []
        jobs = []
        with open(self.queue_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    jobs.append(Job(**data))
        return jobs

    def _read_all_raw(self) -> List[str]:
        """Read raw JSONL lines."""
        if not self.queue_file.exists():
            return []
        with open(self.queue_file, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]

    def _lock(self):
        """File lock context manager."""
        class Lock:
            def __init__(self, lock_path):
                self.lock_path = lock_path
                self.fd = None

            def __enter__(self):
                self.fd = open(self.lock_path, "w")
                fcntl.flock(self.fd, fcntl.LOCK_EX)
                return self

            def __exit__(self, *args):
                if self.fd:
                    fcntl.flock(self.fd, fcntl.LOCK_UN)
                    self.fd.close()

        return Lock(self.lock_file)
