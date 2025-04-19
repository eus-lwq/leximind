from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
import time
from vllm import LLM, SamplingParams

app = FastAPI(title="vLLM Inference API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model instance
llm = None

class GenerationRequest(BaseModel):
    prompt: str
    max_tokens: int = Field(default=128, gt=0, le=4096)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    top_k: int = Field(default=-1)
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    stop: Optional[List[str]] = None
    stream: bool = Field(default=False)

class TokenResponse(BaseModel):
    text: str
    index: int
    
class GenerationResponse(BaseModel):
    id: str
    text: str
    tokens: List[TokenResponse]
    finish_reason: str
    usage: Dict[str, int]

@app.on_event("startup")
async def startup_event():
    global llm
    # Load model on startup - replace with your model path
    model_path = "meta-llama/Llama-2-7b-chat-hf"
    print(f"Loading model {model_path}...")
    llm = LLM(model=model_path)
    print("Model loaded successfully!")

@app.get("/")
async def root():
    return {"message": "vLLM Inference API is running"}

@app.get("/health")
async def health_check():
    if llm is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "healthy", "model_loaded": True}

@app.post("/generate", response_model=GenerationResponse)
async def generate(request: GenerationRequest):
    if llm is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # Configure sampling parameters
    sampling_params = SamplingParams(
        temperature=request.temperature,
        top_p=request.top_p,
        top_k=request.top_k,
        max_tokens=request.max_tokens,
        presence_penalty=request.presence_penalty,
        frequency_penalty=request.frequency_penalty,
        stop=request.stop
    )
    
    start_time = time.time()
    
    # Generate response
    outputs = llm.generate([request.prompt], sampling_params)
    generated_text = outputs[0].outputs[0].text
    
    # Count tokens (approximate)
    prompt_tokens = len(request.prompt.split())
    completion_tokens = len(generated_text.split())
    
    # Create response
    response = GenerationResponse(
        id=f"gen-{int(time.time())}",
        text=generated_text,
        tokens=[TokenResponse(text=token, index=i) for i, token in enumerate(generated_text.split())],
        finish_reason="stop",
        usage={
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "time_seconds": time.time() - start_time
        }
    )
    
    return response

@app.post("/models")
async def list_models():
    """List available models (in this case just the loaded model)"""
    if llm is None:
        return {"models": []}
    
    return {
        "models": [{
            "id": llm.llm_engine.model_config.model,
            "object": "model",
            "created": int(time.time()),
            "owned_by": "vllm"
        }]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)