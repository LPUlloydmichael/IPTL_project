import os
from typing import Optional

from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import Response
from pydantic import ConfigDict, BaseModel, Field, EmailStr
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

from bson import ObjectId
import motor.motor_asyncio
from pymongo import ReturnDocument

from pymongo import MongoClient
import urllib.parse

username = urllib.parse.quote_plus('lloydmichaelicay')
password = urllib.parse.quote_plus('lloyd.mongoatlas')
client = motor.motor_asyncio.AsyncIOMotorClient('mongodb+srv://%s:%s@cl-iptl.etlgmnq.mongodb.net/' % (username, password))

app = FastAPI(title="Student Program API",
summary="A sample application showing how to use FastAPI to add a ReST API to a MongoDB collection.",
)

db = client.db_integrativeprogramming
student_collection = db.get_collection("students")

# Represents an ObjectId field in the database.
# It will be represented as a `str` on the model so that it can be serialized to JSON.
PyObjectId = Annotated[str, BeforeValidator(str)]

class StudentModel(BaseModel):
    """
    Container for a single student record.
    """

# The primary key for the StudentModel, stored as a `str` on the instance.
# This will be aliased to `_id` when sent to MongoDB,
# but provided as `id` in the API requests and responses.
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
name: str = Field(...)
email: EmailStr = Field(...)
course: str = Field(...)
gpa: float = Field(..., le=4.0)
model_config = ConfigDict(
populate_by_name=True,
arbitrary_types_allowed=True,
json_schema_extra={
"example": {
"name": "Alexander Hernandez",
"email": "aahernandez@lpu.edu.ph",
"course": "industrial engineering",
"gpa": 3.0,
}
},
)


@app.post(
"/students/",
response_description="Add new student",
response_model=StudentModel,
status_code=status.HTTP_201_CREATED,
response_model_by_alias=False,
)

async def create_student(student: StudentModel = Body(...)):
    """
    Insert a new student record.
    A unique `id` will be created and provided in the response.
    """
    new_student = await student_collection.insert_one(
    student.model_dump(by_alias=True, exclude=["id"])
    )
    created_student = await student_collection.find_one(
    {"_id": new_student.inserted_id}
    )
    return created_student


@app.delete("/students/{id}", response_description="Delete a student")
async def delete_student(id: str):
    """
    Remove a single student record from the database.
    """
    delete_result = await student_collection.delete_one({"_id": ObjectId(id)})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Student {id} not found")

