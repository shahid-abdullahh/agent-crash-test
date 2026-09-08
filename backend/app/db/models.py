from sqlalchemy import Column, String, Integer, Float, Boolean, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone

Base = declarative_base()


class SQLTask(Base):
    __tablename__ = "tasks"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    constraints = Column(JSON, nullable=False)
    expected_outcome_description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class SQLRun(Base):
    __tablename__ = "runs"

    id = Column(String(64), primary_key=True, index=True)
    task_id = Column(String(64), ForeignKey("tasks.id"), index=True, nullable=False)
    scenario_mode = Column(String(64), nullable=False)
    agent_type = Column(String(64), nullable=False)
    agent_retry_policy = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False)
    created_at = Column(String(64), nullable=False)
    completed_at = Column(String(64), nullable=True)
    final_output = Column(JSON, nullable=True)

    trace_events = relationship("SQLTraceEvent", back_populates="run", cascade="all, delete-orphan", order_by="SQLTraceEvent.sequence_number")
    evaluation = relationship("SQLEvaluation", back_populates="run", uselist=False, cascade="all, delete-orphan")
    diagnosis = relationship("SQLDiagnosis", back_populates="run", uselist=False, cascade="all, delete-orphan")


class SQLTraceEvent(Base):
    __tablename__ = "trace_events"

    event_id = Column(String(64), primary_key=True, index=True)
    run_id = Column(String(64), ForeignKey("runs.id"), index=True, nullable=False)
    sequence_number = Column(Integer, nullable=False)
    timestamp = Column(String(64), nullable=False)
    event_type = Column(String(64), nullable=False)
    tool_name = Column(String(128), nullable=True)
    tool_arguments = Column(JSON, nullable=True)
    http_payload = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    metadata_payload = Column(JSON, nullable=True)

    run = relationship("SQLRun", back_populates="trace_events")


class SQLEvaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(64), ForeignKey("runs.id"), unique=True, index=True, nullable=False)
    task_id = Column(String(64), nullable=False)
    success = Column(Boolean, nullable=False)
    criteria = Column(JSON, nullable=False)
    side_effects = Column(JSON, nullable=False)
    reasons = Column(JSON, nullable=False)
    evaluated_at = Column(String(64), nullable=False)

    run = relationship("SQLRun", back_populates="evaluation")


class SQLDiagnosis(Base):
    __tablename__ = "diagnoses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(64), ForeignKey("runs.id"), unique=True, index=True, nullable=False)
    failure_category = Column(String(255), nullable=False)
    observed_behavior = Column(Text, nullable=False)
    agent_behavior = Column(Text, nullable=False)
    impact = Column(Text, nullable=False)
    likely_responsibility = Column(String(255), nullable=False)
    recommended_remediation = Column(Text, nullable=False)
    evidence_events = Column(JSON, nullable=False)

    run = relationship("SQLRun", back_populates="diagnosis")
