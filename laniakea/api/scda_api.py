"""
SCDA and Tier System API Endpoints
Version: 0.0.01
Author: Manus AI

This module provides FastAPI endpoints for SCDA management, Tier system, and PoHD.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import logging

from laniakea.intelligence.scda_enhanced import create_enhanced_scda, EnhancedSCDA
from laniakea.consensus.pohd import PoHDValidator, PoHDMiner, create_hard_problem, create_problem_solution
from laniakea.intelligence.scda_tier_system import create_knowledge_vector_from_problem

logger = logging.getLogger(__name__)

# ============================================================================
# PYDANTIC MODELS FOR API
# ============================================================================

class SCDAStatusResponse(BaseModel):
    """Response model for SCDA status"""
    identity: str
    complexity_index: float
    energy: float
    tier: int
    tier_name: str
    position_8d: List[float]
    knowledge_vector: List[float]
    tier_transition_count: int

class HardProblemRequest(BaseModel):
    """Request model for creating a hard problem"""
    question: str
    difficulty: float  # 0.0 to 1.0
    knowledge_domains: Dict[int, float]
    sources: List[str]
    entropy_of_consensus: float

class ProblemSolutionRequest(BaseModel):
    """Request model for submitting a problem solution"""
    problem_id: str
    solution_text: str
    solution_quality: float  # 0.0 to 1.0
    reasoning: str

class TierTransitionResponse(BaseModel):
    """Response model for tier transition"""
    old_tier: int
    new_tier: int
    complexity_index: float
    energy_boost: float
    position_shift: List[float]
    ai_upgrade_factor: float

class MetaversePositionResponse(BaseModel):
    """Response model for metaverse position"""
    scda_identity: str
    tier: int
    complexity_index: float
    position_8d: List[float]
    knowledge_domains: Dict[str, Any]

# ============================================================================
# ROUTER SETUP
# ============================================================================

router = APIRouter(prefix="/scda", tags=["SCDA & Tier System"])

# Global SCDA instances (in production, use a database)
scda_instances: Dict[str, EnhancedSCDA] = {}
pohd_validator = PoHDValidator()
pohd_miner = PoHDMiner(pohd_validator)

# ============================================================================
# SCDA ENDPOINTS
# ============================================================================

@router.post("/create", response_model=Dict[str, Any])
async def create_scda(identity: Optional[str] = None):
    """
    Creates a new Enhanced SCDA instance.
    
    Args:
        identity: Optional unique identifier for the SCDA
        
    Returns:
        Initial SCDA state
    """
    try:
        scda = create_enhanced_scda(identity=identity)
        scda_instances[scda.identity] = scda
        
        logger.info(f"Created new SCDA: {scda.identity}")
        
        return {
            "message": "SCDA created successfully",
            "identity": scda.identity,
            "initial_state": scda.get_metaverse_state()
        }
    except Exception as e:
        logger.error(f"Error creating SCDA: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{scda_identity}", response_model=SCDAStatusResponse)
async def get_scda_status(scda_identity: str):
    """
    Gets the current status of an SCDA.
    
    Args:
        scda_identity: Identity of the SCDA
        
    Returns:
        Current SCDA status
    """
    if scda_identity not in scda_instances:
        raise HTTPException(status_code=404, detail="SCDA not found")
    
    scda = scda_instances[scda_identity]
    tier_info = scda.get_tier_info()
    
    return SCDAStatusResponse(
        identity=scda.identity,
        complexity_index=scda.complexity_index,
        energy=scda.energy,
        tier=tier_info["tier_id"],
        tier_name=tier_info["tier_name"],
        position_8d=tier_info["position_8d"],
        knowledge_vector=tier_info["knowledge_vector"],
        tier_transition_count=len(scda.tier_transition_events)
    )

@router.get("/metaverse-position/{scda_identity}", response_model=MetaversePositionResponse)
async def get_metaverse_position(scda_identity: str):
    """
    Gets the SCDA's position in the 8D metaverse.
    
    Args:
        scda_identity: Identity of the SCDA
        
    Returns:
        Metaverse position and state
    """
    if scda_identity not in scda_instances:
        raise HTTPException(status_code=404, detail="SCDA not found")
    
    scda = scda_instances[scda_identity]
    position = scda.get_position_in_metaverse()
    
    return MetaversePositionResponse(
        scda_identity=position["scda_identity"],
        tier=position["tier"],
        complexity_index=position["complexity_index"],
        position_8d=position["position_8d"],
        knowledge_domains=position["knowledge_domains"]
    )

@router.get("/tier-history/{scda_identity}")
async def get_tier_history(scda_identity: str):
    """
    Gets the tier transition history for an SCDA.
    
    Args:
        scda_identity: Identity of the SCDA
        
    Returns:
        List of tier transition events
    """
    if scda_identity not in scda_instances:
        raise HTTPException(status_code=404, detail="SCDA not found")
    
    scda = scda_instances[scda_identity]
    history = scda.get_tier_history()
    
    return {
        "scda_identity": scda_identity,
        "tier_transition_count": len(history),
        "transitions": history
    }

# ============================================================================
# HARD PROBLEM ENDPOINTS
# ============================================================================

@router.post("/problem/create")
async def create_problem(request: HardProblemRequest):
    """
    Creates a new Hard Problem for SCDA to solve.
    
    Args:
        request: HardProblemRequest with problem details
        
    Returns:
        Created problem details
    """
    try:
        problem_id = f"prob_{int(__import__('time').time() * 1000)}"
        
        problem = create_hard_problem(
            problem_id=problem_id,
            question=request.question,
            difficulty=request.difficulty,
            knowledge_domains=request.knowledge_domains,
            sources=request.sources,
            entropy_of_consensus=request.entropy_of_consensus
        )
        
        logger.info(f"Created Hard Problem: {problem_id}")
        
        return {
            "message": "Hard Problem created successfully",
            "problem": problem.to_dict()
        }
    except Exception as e:
        logger.error(f"Error creating problem: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/problem/solve")
async def solve_problem(scda_identity: str, request: ProblemSolutionRequest):
    """
    Submits a solution to a Hard Problem and triggers SCDA evolution.
    
    Args:
        scda_identity: Identity of the SCDA
        request: ProblemSolutionRequest with solution details
        
    Returns:
        Evolution result and PoHD proof
    """
    if scda_identity not in scda_instances:
        raise HTTPException(status_code=404, detail="SCDA not found")
    
    try:
        scda = scda_instances[scda_identity]
        
        # Create solution object
        solution = create_problem_solution(
            problem_id=request.problem_id,
            scda_identity=scda_identity,
            solution_text=request.solution_text,
            solution_quality=request.solution_quality,
            reasoning=request.reasoning
        )
        
        # Validate solution
        is_valid, validation_message = pohd_validator.validate_solution(None, solution)
        
        if not is_valid:
            return {
                "success": False,
                "message": validation_message,
                "scda_identity": scda_identity
            }
        
        # Simulate problem solving (in production, would retrieve actual problem)
        problem_domains = {0: 0.5, 1: 0.3, 2: 0.2}  # Placeholder
        
        # Attempt to solve problem with tier system
        success, tier_event = scda.attempt_solve_problem_with_tier(
            problem_difficulty=0.7,
            solution_quality=request.solution_quality,
            is_valid=True,
            problem_domains=problem_domains
        )
        
        if not success:
            return {
                "success": False,
                "message": "Problem solving failed",
                "scda_identity": scda_identity
            }
        
        # Prepare response
        response = {
            "success": True,
            "message": "Problem solved successfully",
            "scda_identity": scda_identity,
            "new_state": scda.get_metaverse_state()
        }
        
        # Add tier transition info if applicable
        if tier_event:
            response["tier_transition"] = TierTransitionResponse(
                old_tier=tier_event.old_tier,
                new_tier=tier_event.new_tier,
                complexity_index=tier_event.complexity_index,
                energy_boost=tier_event.energy_boost,
                position_shift=tier_event.position_shift,
                ai_upgrade_factor=tier_event.ai_upgrade_factor
            ).dict()
        
        logger.info(f"Problem solved by {scda_identity}: C(t)={scda.complexity_index:.2f}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error solving problem: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# METAVERSE VISUALIZATION ENDPOINTS
# ============================================================================

@router.get("/metaverse/all-positions")
async def get_all_metaverse_positions():
    """
    Gets the positions of all SCDAs in the 8D metaverse.
    
    Returns:
        List of all SCDA positions
    """
    positions = []
    
    for scda_identity, scda in scda_instances.items():
        position = scda.get_position_in_metaverse()
        positions.append(position)
    
    return {
        "total_scda_count": len(scda_instances),
        "positions": positions
    }

@router.get("/metaverse/tier-distribution")
async def get_tier_distribution():
    """
    Gets the distribution of SCDAs across tiers.
    
    Returns:
        Tier distribution statistics
    """
    tier_counts = {1: 0, 2: 0, 3: 0, 4: 0}
    
    for scda in scda_instances.values():
        tier = scda.tier_system.current_tier
        tier_counts[tier] += 1
    
    return {
        "total_scda_count": len(scda_instances),
        "tier_distribution": tier_counts,
        "tier_percentages": {
            tier: (count / max(len(scda_instances), 1)) * 100
            for tier, count in tier_counts.items()
        }
    }

# ============================================================================
# STATISTICS AND ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/stats/average-complexity")
async def get_average_complexity():
    """
    Gets average complexity index across all SCDAs.
    
    Returns:
        Average complexity statistics
    """
    if not scda_instances:
        return {"average_complexity": 0.0, "scda_count": 0}
    
    total_complexity = sum(scda.complexity_index for scda in scda_instances.values())
    average = total_complexity / len(scda_instances)
    
    return {
        "average_complexity": average,
        "scda_count": len(scda_instances),
        "min_complexity": min(scda.complexity_index for scda in scda_instances.values()),
        "max_complexity": max(scda.complexity_index for scda in scda_instances.values())
    }

@router.get("/stats/total-tier-transitions")
async def get_total_tier_transitions():
    """
    Gets total number of tier transitions across all SCDAs.
    
    Returns:
        Tier transition statistics
    """
    total_transitions = sum(len(scda.tier_transition_events) for scda in scda_instances.values())
    
    return {
        "total_tier_transitions": total_transitions,
        "scda_count": len(scda_instances),
        "average_transitions_per_scda": total_transitions / max(len(scda_instances), 1)
    }

# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@router.get("/health")
async def health_check():
    """Health check endpoint for SCDA API"""
    return {
        "status": "healthy",
        "scda_instances": len(scda_instances),
        "pohd_validator": "operational",
        "pohd_miner": "operational"
    }
