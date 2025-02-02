###############################################################################
#
#  Welcome to Baml! To use this generated code, please run the following:
#
#  $ pip install baml
#
###############################################################################

# This file was generated by BAML: please do not edit it. Instead, edit the
# BAML files and re-generate this code.
#
# ruff: noqa: E501,F401
# flake8: noqa: E501,F401
# pylint: disable=unused-import,line-too-long
# fmt: off
from typing import Any, Dict, List, Optional, TypeVar, Union, TypedDict, Type, Literal, cast
from typing_extensions import NotRequired
import pprint

import baml_py
from pydantic import BaseModel, ValidationError, create_model

from . import partial_types, types
from .types import Checked, Check
from .type_builder import TypeBuilder
from .globals import DO_NOT_USE_DIRECTLY_UNLESS_YOU_KNOW_WHAT_YOURE_DOING_CTX, DO_NOT_USE_DIRECTLY_UNLESS_YOU_KNOW_WHAT_YOURE_DOING_RUNTIME

OutputType = TypeVar('OutputType')

# Define the TypedDict with optional parameters having default values
class BamlCallOptions(TypedDict, total=False):
    tb: NotRequired[TypeBuilder]
    client_registry: NotRequired[baml_py.baml_py.ClientRegistry]

class BamlSyncClient:
    __runtime: baml_py.BamlRuntime
    __ctx_manager: baml_py.BamlCtxManager
    __stream_client: "BamlStreamClient"

    def __init__(self, runtime: baml_py.BamlRuntime, ctx_manager: baml_py.BamlCtxManager):
      self.__runtime = runtime
      self.__ctx_manager = ctx_manager
      self.__stream_client = BamlStreamClient(self.__runtime, self.__ctx_manager)

    @property
    def stream(self):
      return self.__stream_client

    
    def GenerateCompositionPlan(
        self,
        theme: str,
        baml_options: BamlCallOptions = {},
    ) -> types.CompositionPlan:
      __tb__ = baml_options.get("tb", None)
      if __tb__ is not None:
        tb = __tb__._tb # type: ignore (we know how to use this private attribute)
      else:
        tb = None
      __cr__ = baml_options.get("client_registry", None)

      raw = self.__runtime.call_function_sync(
        "GenerateCompositionPlan",
        {
          "theme": theme,
        },
        self.__ctx_manager.get(),
        tb,
        __cr__,
      )
      return cast(types.CompositionPlan, raw.cast_to(types, types, partial_types, False))
    
    def GenerateModularSong(
        self,
        plan: types.CompositionPlan,
        baml_options: BamlCallOptions = {},
    ) -> types.ModularPiece:
      __tb__ = baml_options.get("tb", None)
      if __tb__ is not None:
        tb = __tb__._tb # type: ignore (we know how to use this private attribute)
      else:
        tb = None
      __cr__ = baml_options.get("client_registry", None)

      raw = self.__runtime.call_function_sync(
        "GenerateModularSong",
        {
          "plan": plan,
        },
        self.__ctx_manager.get(),
        tb,
        __cr__,
      )
      return cast(types.ModularPiece, raw.cast_to(types, types, partial_types, False))
    



class BamlStreamClient:
    __runtime: baml_py.BamlRuntime
    __ctx_manager: baml_py.BamlCtxManager

    def __init__(self, runtime: baml_py.BamlRuntime, ctx_manager: baml_py.BamlCtxManager):
      self.__runtime = runtime
      self.__ctx_manager = ctx_manager

    
    def GenerateCompositionPlan(
        self,
        theme: str,
        baml_options: BamlCallOptions = {},
    ) -> baml_py.BamlSyncStream[partial_types.CompositionPlan, types.CompositionPlan]:
      __tb__ = baml_options.get("tb", None)
      if __tb__ is not None:
        tb = __tb__._tb # type: ignore (we know how to use this private attribute)
      else:
        tb = None
      __cr__ = baml_options.get("client_registry", None)

      raw = self.__runtime.stream_function_sync(
        "GenerateCompositionPlan",
        {
          "theme": theme,
        },
        None,
        self.__ctx_manager.get(),
        tb,
        __cr__,
      )

      return baml_py.BamlSyncStream[partial_types.CompositionPlan, types.CompositionPlan](
        raw,
        lambda x: cast(partial_types.CompositionPlan, x.cast_to(types, types, partial_types, True)),
        lambda x: cast(types.CompositionPlan, x.cast_to(types, types, partial_types, False)),
        self.__ctx_manager.get(),
      )
    
    def GenerateModularSong(
        self,
        plan: types.CompositionPlan,
        baml_options: BamlCallOptions = {},
    ) -> baml_py.BamlSyncStream[partial_types.ModularPiece, types.ModularPiece]:
      __tb__ = baml_options.get("tb", None)
      if __tb__ is not None:
        tb = __tb__._tb # type: ignore (we know how to use this private attribute)
      else:
        tb = None
      __cr__ = baml_options.get("client_registry", None)

      raw = self.__runtime.stream_function_sync(
        "GenerateModularSong",
        {
          "plan": plan,
        },
        None,
        self.__ctx_manager.get(),
        tb,
        __cr__,
      )

      return baml_py.BamlSyncStream[partial_types.ModularPiece, types.ModularPiece](
        raw,
        lambda x: cast(partial_types.ModularPiece, x.cast_to(types, types, partial_types, True)),
        lambda x: cast(types.ModularPiece, x.cast_to(types, types, partial_types, False)),
        self.__ctx_manager.get(),
      )
    

b = BamlSyncClient(DO_NOT_USE_DIRECTLY_UNLESS_YOU_KNOW_WHAT_YOURE_DOING_RUNTIME, DO_NOT_USE_DIRECTLY_UNLESS_YOU_KNOW_WHAT_YOURE_DOING_CTX)

__all__ = ["b"]