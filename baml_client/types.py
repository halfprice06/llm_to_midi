###############################################################################
#
#  Welcome to Baml! To use this generated code, please run the following:
#
#  $ pip install baml-py
#
###############################################################################

# This file was generated by BAML: please do not edit it. Instead, edit the
# BAML files and re-generate this code.
#
# ruff: noqa: E501,F401
# flake8: noqa: E501,F401
# pylint: disable=unused-import,line-too-long
# fmt: off
import baml_py
from enum import Enum
from pydantic import BaseModel, ConfigDict
from typing_extensions import TypeAlias
from typing import Dict, Generic, List, Literal, Optional, TypeVar, Union


T = TypeVar('T')
CheckName = TypeVar('CheckName', bound=str)

class Check(BaseModel):
    name: str
    expression: str
    status: str

class Checked(BaseModel, Generic[T,CheckName]):
    value: T
    checks: Dict[CheckName, Check]

def get_checks(checks: Dict[CheckName, Check]) -> List[Check]:
    return list(checks.values())

def all_succeeded(checks: Dict[CheckName, Check]) -> bool:
    return all(check.status == "succeeded" for check in get_checks(checks))



class Beat(BaseModel):
    beat_counter: str
    bass: List["NoteDuration"]
    tenor: List["NoteDuration"]
    alto: List["NoteDuration"]
    soprano: List["NoteDuration"]
    piano: List["NoteDuration"]
    percussion: Optional[List["NoteDuration"]] = None

class CompositionPlan(BaseModel):
    plan_title: str
    style: Optional[str] = None
    sections: List["SectionPlan"]

class CompositionPlanWithMetadata(BaseModel):
    plan: "CompositionPlan"
    metadata: "SongMetadata"

class Instrumentation(BaseModel):
    bass: int
    tenor: int
    alto: int
    soprano: int

class Measure(BaseModel):
    harmony_plan_for_this_measure: str
    phrase_measure_number: int
    beats: List["Beat"]

class ModularPhrase(BaseModel):
    phrase_label: str
    phrase_description: str
    lyrics: Optional[str] = None
    measures: List["Measure"]

class ModularPiece(BaseModel):
    metadata: "SongMetadata"
    sections: List["ModularSection"]

class ModularSection(BaseModel):
    section_label: str
    section_description: str
    harmonic_direction: str
    rhythmic_direction: str
    melodic_direction: str
    phrases: List["ModularPhrase"]

class NoteDuration(BaseModel):
    note: Optional[int] = None
    duration: str

class SectionPlan(BaseModel):
    label: str
    description: Optional[str] = None
    number_of_phrases: int
    measures_per_phrase: int
    harmonic_direction: str
    rhythmic_direction: str
    melodic_direction: str

class SongMetadata(BaseModel):
    title: str
    tempo: int
    key_signature: str
    time_signature: str
    instruments: "Instrumentation"
