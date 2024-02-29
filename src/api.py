from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List


class SectionChild(BaseModel):
    title: str


class Section(BaseModel):
    title: str
    children: List[SectionChild]


class TopicRequest(BaseModel):
    topic: str
    sections: List[Section]


app = FastAPI()


@app.post("/generate")
async def generate(request_data: TopicRequest):
    try:
        return {"OK"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
