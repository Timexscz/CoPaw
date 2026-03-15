"""Category management API routes."""

from typing import List
from fastapi import APIRouter, HTTPException, Query, Body

from ...db.repositories import CategoryRepository, SkillCategoryMapRepository
from ...services.category_service import CategoryService
from ...db.repositories.category_repo import CategoryModel

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/skills", response_model=List[CategoryModel])
async def get_skill_categories(
    enabled_only: bool = Query(True, description="Whether to return only enabled categories")
):
    """Get list of skill categories."""
    return await CategoryService.get_skill_categories(enabled_only)


@router.get("/mcp", response_model=List[CategoryModel])
async def get_mcp_categories(
    enabled_only: bool = Query(True, description="Whether to return only enabled categories")
):
    """Get list of MCP categories."""
    return await CategoryService.get_mcp_categories(enabled_only)


@router.post("/skills", response_model=CategoryModel)
async def create_skill_category(category: CategoryModel = Body(...)):
    """Create a new skill category."""
    category.is_custom = True
    category.category_type = 'skill'
    return await CategoryRepository.create_category(category)


@router.post("/mcp", response_model=CategoryModel)
async def create_mcp_category(category: CategoryModel = Body(...)):
    """Create a new MCP category."""
    category.is_custom = True
    category.category_type = 'mcp'
    return await CategoryRepository.create_category(category)


@router.put("/skills/reorder")
async def reorder_skill_categories(category_ids: List[str] = Body(..., description="Category IDs in new order")):
    """Reorder skill categories by updating priorities."""
    await CategoryRepository.update_category_priority(category_ids, 'skill')
    return {"success": True}


@router.put("/mcp/reorder")
async def reorder_mcp_categories(category_ids: List[str] = Body(..., description="Category IDs in new order")):
    """Reorder MCP categories by updating priorities."""
    await CategoryRepository.update_category_priority(category_ids, 'mcp')
    return {"success": True}


@router.delete("/skills/{category_id}")
async def delete_skill_category(category_id: str):
    """Delete a skill category (only custom categories)."""
    success = await CategoryRepository.delete_category(category_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot delete built-in category")
    return {"success": True}


@router.delete("/mcp/{category_id}")
async def delete_mcp_category(category_id: str):
    """Delete an MCP category (only custom categories)."""
    success = await CategoryRepository.delete_category(category_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot delete built-in category")
    return {"success": True}


@router.patch("/skills/{category_id}/toggle")
async def toggle_skill_category(category_id: str):
    """Toggle skill category enabled status."""
    new_status = await CategoryRepository.toggle_category(category_id)
    if new_status is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"success": True, "is_enabled": new_status}


@router.patch("/mcp/{category_id}/toggle")
async def toggle_mcp_category(category_id: str):
    """Toggle MCP category enabled status."""
    new_status = await CategoryRepository.toggle_category(category_id)
    if new_status is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"success": True, "is_enabled": new_status}


@router.post("/skills/{skill_name}/category")
async def set_skill_category(
    skill_name: str,
    category_id: str = Body(..., embed=True, description="Category ID to assign")
):
    """Set category for a skill (manual assignment)."""
    await CategoryService.set_manual_category(skill_name, category_id)
    return {"success": True}


@router.get("/skills/{skill_name}/category")
async def get_skill_category(skill_name: str):
    """Get category for a skill."""
    category_id = await SkillCategoryMapRepository.get_category(skill_name)
    if not category_id:
        # Auto-categorize
        category_id, _, _ = await CategoryService.categorize_skill(skill_name)
    return {"category_id": category_id}


@router.post("/skills/batch/categorize")
async def batch_categorize_skills(
    skill_names: List[str] = Body(..., description="List of skill names to categorize")
):
    """Get categories for multiple skills."""
    return await SkillCategoryMapRepository.batch_get_categories(skill_names)
