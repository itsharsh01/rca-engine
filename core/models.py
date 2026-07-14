from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from core.database import Base

class Org(Base):
    __tablename__ = "orgs"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    projects = relationship("Project", back_populates="org")

class Project(Base):
    __tablename__ = "projects"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    org_id = Column(String, ForeignKey("orgs.id"))
    org = relationship("Org", back_populates="projects")
    apps = relationship("App", back_populates="project")

class App(Base):
    __tablename__ = "apps"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    project_id = Column(String, ForeignKey("projects.id"))
    project = relationship("Project", back_populates="apps")
    traces = relationship("Trace", back_populates="app")

class Trace(Base):
    __tablename__ = "traces"
    id = Column(String, primary_key=True)
    app_id = Column(String, ForeignKey("apps.id"))
    app = relationship("App", back_populates="traces")
    spans = relationship("Span", back_populates="trace")

class Span(Base):
    __tablename__ = "spans"
    id = Column(String, primary_key=True)
    trace_id = Column(String, ForeignKey("traces.id"))
    parent_span_id = Column(String, nullable=True)
    name = Column(String, nullable=False)
    start_time = Column(String, nullable=False)
    end_time = Column(String, nullable=False)
    attributes = Column(Text, nullable=True)
    trace = relationship("Trace", back_populates="spans")
