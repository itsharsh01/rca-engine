import time
import datetime
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, List
from core.database import get_database
from onboarding.connection_tester import test_platform_connection

router = APIRouter(prefix="/projects", tags=["projects"])

class CreateProjectRequest(BaseModel):
    project_name: str

class AddObservabilityRequest(BaseModel):
    platform_name: str
    credentials: Dict[str, Any]

@router.get("")
async def get_projects():
    try:
        db = get_database()
        cursor = db.projects.find({}, {"_id": 0})
        projects = await cursor.to_list(length=100)
        
        # If no projects exist, seed initial default projects
        if not projects:
            now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
            default_projects = [
                {
                    "project_id": "proj_customer_support",
                    "project_name": "Customer Support Bot",
                    "created_at": now_iso,
                    "observabilities": [
                        {
                            "platform_name": "langsmith",
                            "credentials": {"endpoint": "https://api.smith.langchain.com"},
                            "connected": True,
                            "added_at": now_iso
                        }
                    ]
                },
                {
                    "project_id": "proj_internal_doc",
                    "project_name": "Internal Doc Search RAG",
                    "created_at": now_iso,
                    "observabilities": [
                        {
                            "platform_name": "phoenix",
                            "credentials": {"endpoint": "http://localhost:6006"},
                            "connected": True,
                            "added_at": now_iso
                        }
                    ]
                }
            ]
            await db.projects.insert_many(default_projects)
            projects = await db.projects.find({}, {"_id": 0}).to_list(length=100)
            
        return {
            "status": "success",
            "count": len(projects),
            "projects": projects
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch projects: {str(e)}"
        )

@router.post("")
async def create_project(body: CreateProjectRequest):
    try:
        if not body.project_name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project name cannot be empty"
            )
            
        db = get_database()
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        proj_id = f"proj_{int(time.time())}"
        
        new_project = {
            "project_id": proj_id,
            "project_name": body.project_name.strip(),
            "created_at": now_iso,
            "observabilities": []
        }
        
        await db.projects.insert_one(new_project)
        # Exclude _id before returning
        new_project.pop("_id", None)
        
        return {
            "status": "success",
            "message": f"Project '{body.project_name}' created successfully",
            "project": new_project
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )

@router.post("/{project_id}/observability")
async def add_observability_to_project(project_id: str, body: AddObservabilityRequest):
    try:
        # 1. Test platform credentials first
        try:
            await test_platform_connection(body.platform_name, body.credentials)
        except Exception as ce:
            print(f"Connection warning for {body.platform_name}: {ce}")

        db = get_database()
        project = await db.projects.find_one({"project_id": project_id})
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID '{project_id}' not found"
            )
            
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        obs_entry = {
            "platform_name": body.platform_name.lower(),
            "credentials": body.credentials,
            "connected": True,
            "added_at": now_iso
        }
        
        # Remove existing config for same platform if present, then push new one
        await db.projects.update_one(
            {"project_id": project_id},
            {"$pull": {"observabilities": {"platform_name": body.platform_name.lower()}}}
        )
        
        await db.projects.update_one(
            {"project_id": project_id},
            {"$push": {"observabilities": obs_entry}}
        )

        # Also sync to global configuration collection for default fallback
        await db.configurations.update_one(
            {"platform_name": body.platform_name.lower()},
            {"$set": {"credentials": body.credentials, "connected": True}},
            upsert=True
        )
        
        updated = await db.projects.find_one({"project_id": project_id}, {"_id": 0})
        
        return {
            "status": "success",
            "message": f"Observability '{body.platform_name}' added to project '{project.get('project_name')}'",
            "project": updated
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to attach observability to project: {str(e)}"
        )
