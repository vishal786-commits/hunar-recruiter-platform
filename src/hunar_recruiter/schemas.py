from typing import Optional

from pydantic import BaseModel, Field


class Location(BaseModel):
    city: Optional[str] = Field(
        default=None,
        description="City where the role is based."
    )
    country: Optional[str] = Field(
        default=None,
        description="Country where the role is based."
    )
    remote: bool = Field(
        default=False,
        description="Whether the role explicitly allows remote work."
    )


class Experience(BaseModel):
    min_years: Optional[float] = Field(
        default=None,
        description="Minimum years of relevant professional experience."
    )
    max_years: Optional[float] = Field(
        default=None,
        description="Maximum years of relevant professional experience, if specified."
    )


class Skills(BaseModel):
    required: list[str] = Field(
        default_factory=list,
        description="Skills explicitly required for the role."
    )
    preferred: list[str] = Field(
        default_factory=list,
        description="Skills described as preferred, nice-to-have, or bonus."
    )


class ScreeningRequirements(BaseModel):
    technical_skills: list[str] = Field(
        default_factory=list,
        description="Technical skills that should be evaluated during candidate screening."
    )
    availability: bool = Field(
        default=True,
        description="Whether candidate availability should be collected."
    )
    notice_period: bool = Field(
        default=True,
        description="Whether candidate notice period should be collected."
    )
    compensation_expectation: bool = Field(
        default=True,
        description="Whether candidate compensation expectations should be collected."
    )
    interest: bool = Field(
        default=True,
        description="Whether candidate interest in the role should be assessed."
    )
    location_flexibility: bool = Field(
        default=False,
        description="Whether relocation or remote/location flexibility should be assessed."
    )


class JobDescription(BaseModel):
    title: Optional[str] = Field(
        default=None,
        description="The job title or role being hired for."
    )

    company: Optional[str] = Field(
        default=None,
        description="Company hiring for the position."
    )

    location: Location = Field(
        default_factory=Location,
        description="Location requirements for the position."
    )

    experience: Experience = Field(
        default_factory=Experience,
        description="Required professional experience."
    )

    employment_type: Optional[str] = Field(
        default=None,
        description="Employment type such as full-time, part-time, contract, or internship."
    )

    skills: Skills = Field(
        default_factory=Skills,
        description="Required and preferred technical/professional skills."
    )

    responsibilities: list[str] = Field(
        default_factory=list,
        description="Key responsibilities of the role."
    )

    requirements: list[str] = Field(
        default_factory=list,
        description="Explicit qualifications and requirements from the JD."
    )

    screening_requirements: ScreeningRequirements = Field(
        default_factory=ScreeningRequirements,
        description="Information that should be collected during candidate screening."
    )