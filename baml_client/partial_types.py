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
from typing import Dict, Generic, List, Optional, TypeVar, Union, Literal

from . import types
from .types import Checked, Check

###############################################################################
#
#  These types are used for streaming, for when an instance of a type
#  is still being built up and any of its fields is not yet fully available.
#
###############################################################################

T = TypeVar('T')
class StreamState(BaseModel, Generic[T]):
    value: T
    state: Literal["Pending", "Incomplete", "Complete"]


class CompositionPlan(BaseModel):
    plan_title: Optional[str] = None
    style: Optional[str] = None
    sections: List["SectionPlan"]

class CompositionPlanWithMetadata(BaseModel):
    plan: Optional["CompositionPlan"] = None
    metadata: Optional["SongMetadata"] = None

class Instrumentation(BaseModel):
    bass: Optional[int] = None
    tenor: Optional[int] = None
    alto: Optional[int] = None
    soprano: Optional[int] = None

class Measure(BaseModel):
    phrase_measure_number: Optional[int] = None
    bass: List["NoteDuration"]
    tenor: List["NoteDuration"]
    alto: List["NoteDuration"]
    soprano: List["NoteDuration"]
    piano: List["NoteDuration"]
    percussion: Optional[List["NoteDuration"]] = None

class ModularPhrase(BaseModel):
    phrase_label: Optional[str] = None
    phrase_description: Optional[str] = None
    lyrics: Optional[str] = None
    measures: List["Measure"]

class ModularPiece(BaseModel):
    metadata: Optional["SongMetadata"] = None
    sections: List["ModularSection"]

class ModularSection(BaseModel):
    section_label: Optional[str] = None
    section_description: Optional[str] = None
    harmonic_direction: Optional[str] = None
    rhythmic_direction: Optional[str] = None
    melodic_direction: Optional[str] = None
    phrases: List["ModularPhrase"]

class NoteDuration(BaseModel):
    note: Optional[int] = None
    duration: Optional[str] = None

class SectionPlan(BaseModel):
    label: Optional[str] = None
    description: Optional[str] = None
    number_of_phrases: Optional[int] = None
    measures_per_phrase: Optional[int] = None
    harmonic_direction: Optional[str] = None
    rhythmic_direction: Optional[str] = None
    melodic_direction: Optional[str] = None

class SongMetadata(BaseModel):
    title: Optional[str] = None
    tempo: Optional[int] = None
    key_signature: Optional[str] = None
    time_signature: Optional[str] = None
    instruments: Optional["Instrumentation"] = None
