"""
LaniakeA Protocol - LLM API Router
Endpoints for LLM generation and validation services.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import json

# Import the AI_API and get_ai_api function
from src.intelligence.ai_api import get_ai_api

router = APIRouter(prefix="/llm", tags=["LLM Services"])

# --- Request/Response Models ---

class LLMGenerateRequest(BaseModel):
    prompt: str = Field(..., description="The user prompt to generate text from.")
    system_prompt: Optional[str] = Field(None, description="System-level instructions for the LLM.")
    model: Optional[str] = Field(None, description="Specific LLM model to use (e.g., gpt-4.1-mini).")
    max_tokens: int = Field(2048, description="Maximum number of tokens to generate.")
    temperature: float = Field(0.7, description="Sampling temperature for generation.")
    # New field for fine-tuning context
    hard_problem_context: Optional[Dict[str, Any]] = Field(None, description="Contextual data for fine-tuning/in-context learning for a 'Hard Problem'.")

class LLMGenerateResponse(BaseModel):
    generated_text: str
    model_used: str
    timestamp: str

class LLMValidateRequest(BaseModel):
    text_to_validate: str = Field(..., description="The text (e.g., a proposed solution) to be validated.")
    validation_criteria: str = Field(..., description="The criteria or problem statement against which the text should be validated.")
    context: Optional[str] = Field(None, description="Additional context for validation.")
    # New field for fine-tuning context
    hard_problem_context: Optional[Dict[str, Any]] = Field(None, description="Contextual data for fine-tuning/in-context learning for a 'Hard Problem'.")

class LLMValidateResponse(BaseModel):
    is_valid: bool
    score: float = Field(..., description="A numerical score (0.0 to 1.0) representing the confidence of validity.")
    reasoning: str = Field(..., description="Detailed reasoning for the validation decision and score.")
    model_used: str
    timestamp: str

# --- Helper for Hard Problem Context (Simulated Fine-Tuning) ---

def apply_hard_problem_context(system_prompt: str, context: Optional[Dict[str, Any]]) -> str:
    """
    Simulates the effect of fine-tuning by injecting context into the system prompt.
    In a real system, this would involve loading a fine-tuned model or a complex RAG system.
    """
    if not context:
        return system_prompt

    context_str = "\n\n--- HARD PROBLEM CONTEXT ---\n"
    if context.get("problem_statement"):
        context_str += f"Problem Statement: {context['problem_statement']}\n"
    if context.get("mathematical_model"):
        context_str += f"Mathematical Model: {context['mathematical_model']}\n"
    if context.get("prior_failed_attempts"):
        context_str += f"Prior Failed Attempts: {context['prior_failed_attempts']}\n"
    if context.get("required_knowledge"):
        context_str += f"Required Knowledge (LKU): {context['required_knowledge']}\n"
    context_str += "---------------------------\n\n"

    return f"{system_prompt}\n{context_str}" if system_prompt else context_str.strip()


# --- Endpoints ---

@router.post("/generate", response_model=LLMGenerateResponse)
async def generate_llm_text(request: LLMGenerateRequest, req: Request):
    """
    Generates text using the LLM, optionally with 'Hard Problem' context.
    """
    ai_api = get_ai_api()
    
    # 1. Apply Hard Problem Context to System Prompt
    final_system_prompt = apply_hard_problem_context(request.system_prompt, request.hard_problem_context)
    
    # 2. Call the asynchronous generation method
    try:
        # The AI_API's async method returns a string (either content or a JSON error string)
        result_str = await ai_api.generate_text_async(
            prompt=request.prompt,
            system_prompt=final_system_prompt,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        # Check if the result is a JSON error string
        if result_str.startswith('{') and '"error"' in result_str:
            error_data = json.loads(result_str)
            raise HTTPException(status_code=500, detail=error_data.get("error", "LLM generation failed"))

        return LLMGenerateResponse(
            generated_text=result_str,
            model_used=request.model if request.model else ai_api.default_model,
            timestamp=ai_api.stats["last_call"] # This is updated inside the generate_text_async call
        )

    except HTTPException:
        raise # Re-raise FastAPI HTTP exceptions
    except Exception as e:
        req.app.state.logger.error(f"Error in /llm/generate: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error during LLM generation: {e}")


@router.post("/validate", response_model=LLMValidateResponse)
async def validate_llm_text(request: LLMValidateRequest, req: Request):
    """
    Validates a proposed solution using the LLM, simulating the Dual Validation mechanism.
    """
    ai_api = get_ai_api()
    
    # 1. Construct the validation prompt
    validation_prompt = (
        f"CRITERIA: {request.validation_criteria}\n\n"
        f"TEXT TO VALIDATE: {request.text_to_validate}\n\n"
        "Analyze the text against the criteria. Provide a JSON object with three keys: "
        "'is_valid' (boolean), 'score' (float between 0.0 and 1.0), and 'reasoning' (string)."
    )
    
    # 2. Apply Hard Problem Context
    validation_system_prompt = "You are an expert scientific validator for the Laniakea Protocol. Your task is to rigorously assess a proposed solution against a set of criteria. You must output a single, valid JSON object."
    final_system_prompt = apply_hard_problem_context(validation_system_prompt, request.hard_problem_context)
    
    # 3. Call the asynchronous generation method
    try:
        # Use a high temperature for creative generation, but a low temperature for validation to ensure deterministic output
        result_str = await ai_api.generate_text_async(
            prompt=validation_prompt,
            system_prompt=final_system_prompt,
            model=request.model,
            max_tokens=1024, # Smaller max_tokens for a focused JSON response
            temperature=0.1
        )
        
        # Check for API error
        if result_str.startswith('{') and '"error"' in result_str:
            error_data = json.loads(result_str)
            raise HTTPException(status_code=500, detail=error_data.get("error", "LLM validation failed"))

        # 4. Parse the JSON response
        try:
            # The LLM might wrap the JSON in markdown, so we try to clean it up
            if result_str.startswith("```json"):
                json_content = result_str.strip().strip("```json").strip("```").strip()
            else:
                json_content = result_str.strip()
                
            validation_result = json.loads(json_content)
            
            # 5. Validate the structure of the response
            if not all(k in validation_result for k in ["is_valid", "score", "reasoning"]):
                raise ValueError("LLM response is missing required keys: is_valid, score, or reasoning.")
            
            if not isinstance(validation_result["is_valid"], bool):
                raise ValueError("LLM response 'is_valid' must be a boolean.")
            
            score = float(validation_result["score"])
            if not (0.0 <= score <= 1.0):
                raise ValueError("LLM response 'score' must be between 0.0 and 1.0.")
            
            return LLMValidateResponse(
                is_valid=validation_result["is_valid"],
                score=score,
                reasoning=validation_result["reasoning"],
                model_used=request.model if request.model else ai_api.default_model,
                timestamp=ai_api.stats["last_call"]
            )
            
        except (json.JSONDecodeError, ValueError) as parse_error:
            req.app.state.logger.error(f"LLM returned invalid JSON or structure: {parse_error}. Raw response: {result_str}")
            raise HTTPException(status_code=500, detail=f"LLM returned an unparseable or invalid response structure. Raw: {result_str[:100]}...")

    except HTTPException:
        raise # Re-raise FastAPI HTTP exceptions
    except Exception as e:
        req.app.state.logger.error(f"Error in /llm/validate: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error during LLM validation: {e}")

# Include the router in the main API file
# (This step will be done in the next action)
