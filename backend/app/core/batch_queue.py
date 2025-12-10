"""
Batch job queue system for async task processing.

MVP implementation using asyncio for simplicity.
Can be migrated to Redis + Celery/ARQ for production scaling.
"""
import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum


class JobStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class JobResult:
    """Result of a single job item."""
    item_id: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class BatchJob:
    """Represents a batch processing job."""
    id: str
    job_type: str
    status: JobStatus
    total_items: int
    completed_items: int = 0
    failed_items: int = 0
    results: List[JobResult] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def progress(self) -> float:
        """Progress percentage (0-100)."""
        if self.total_items == 0:
            return 100.0
        return (self.completed_items + self.failed_items) / self.total_items * 100

    @property
    def is_done(self) -> bool:
        """Check if job is finished (completed or failed)."""
        return self.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "id": self.id,
            "job_type": self.job_type,
            "status": self.status.value,
            "total_items": self.total_items,
            "completed_items": self.completed_items,
            "failed_items": self.failed_items,
            "progress": self.progress,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
            "results": [
                {
                    "item_id": r.item_id,
                    "success": r.success,
                    "result": r.result,
                    "error": r.error,
                }
                for r in self.results
            ],
        }


class BatchQueue:
    """
    In-memory batch job queue with async processing.

    Features:
    - Concurrent task execution
    - Progress tracking
    - Graceful error handling
    - Job cancellation support
    """

    def __init__(self, max_concurrent: int = 3):
        self.jobs: Dict[str, BatchJob] = {}
        self.max_concurrent = max_concurrent
        self._tasks: Dict[str, asyncio.Task] = {}

    def create_job(
        self,
        job_type: str,
        total_items: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> BatchJob:
        """Create a new batch job."""
        job = BatchJob(
            id=str(uuid.uuid4()),
            job_type=job_type,
            status=JobStatus.PENDING,
            total_items=total_items,
            metadata=metadata or {},
        )
        self.jobs[job.id] = job
        return job

    def get_job(self, job_id: str) -> Optional[BatchJob]:
        """Get job by ID."""
        return self.jobs.get(job_id)

    def list_jobs(
        self,
        job_type: Optional[str] = None,
        status: Optional[JobStatus] = None,
        limit: int = 20,
    ) -> List[BatchJob]:
        """List jobs with optional filtering."""
        jobs = list(self.jobs.values())

        if job_type:
            jobs = [j for j in jobs if j.job_type == job_type]
        if status:
            jobs = [j for j in jobs if j.status == status]

        # Sort by created_at descending
        jobs.sort(key=lambda j: j.created_at, reverse=True)
        return jobs[:limit]

    async def run_job(
        self,
        job_id: str,
        items: List[Any],
        processor: Callable[[Any], Awaitable[Any]],
    ) -> BatchJob:
        """
        Run a batch job with the given processor function.

        Args:
            job_id: The job ID to run
            items: List of items to process
            processor: Async function to process each item

        Returns:
            Updated BatchJob with results
        """
        job = self.jobs.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        job.status = JobStatus.IN_PROGRESS
        job.started_at = datetime.utcnow()

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def process_with_semaphore(item: Any, index: int) -> JobResult:
            async with semaphore:
                item_id = str(index)
                try:
                    result = await processor(item)
                    job.completed_items += 1
                    return JobResult(
                        item_id=item_id,
                        success=True,
                        result=result,
                    )
                except Exception as e:
                    job.failed_items += 1
                    return JobResult(
                        item_id=item_id,
                        success=False,
                        error=str(e),
                    )

        # Process all items concurrently (with semaphore limiting)
        try:
            tasks = [
                process_with_semaphore(item, i)
                for i, item in enumerate(items)
            ]
            job.results = await asyncio.gather(*tasks)

            # Determine final status
            if job.failed_items == job.total_items:
                job.status = JobStatus.FAILED
                job.error = "All items failed to process"
            elif job.failed_items > 0:
                job.status = JobStatus.COMPLETED  # Partial success
            else:
                job.status = JobStatus.COMPLETED

        except asyncio.CancelledError:
            job.status = JobStatus.CANCELLED
            job.error = "Job was cancelled"
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)

        job.completed_at = datetime.utcnow()
        return job

    def start_job_async(
        self,
        job_id: str,
        items: List[Any],
        processor: Callable[[Any], Awaitable[Any]],
    ) -> None:
        """Start a job in the background without waiting."""
        task = asyncio.create_task(self.run_job(job_id, items, processor))
        self._tasks[job_id] = task

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job."""
        if job_id in self._tasks:
            task = self._tasks[job_id]
            if not task.done():
                task.cancel()
                return True

        job = self.jobs.get(job_id)
        if job and not job.is_done:
            job.status = JobStatus.CANCELLED
            job.completed_at = datetime.utcnow()
            return True

        return False

    def cleanup_old_jobs(self, max_age_hours: int = 24) -> int:
        """Remove jobs older than max_age_hours. Returns count removed."""
        cutoff = datetime.utcnow()
        removed = 0

        for job_id in list(self.jobs.keys()):
            job = self.jobs[job_id]
            age_hours = (cutoff - job.created_at).total_seconds() / 3600
            if age_hours > max_age_hours and job.is_done:
                del self.jobs[job_id]
                if job_id in self._tasks:
                    del self._tasks[job_id]
                removed += 1

        return removed


# Singleton instance
batch_queue = BatchQueue(max_concurrent=3)
