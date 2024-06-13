from imgui_bundle import ImVec4, ImVec2, ImColor
from typing_extensions import Annotated
from pydantic_core import core_schema
from pydantic import (
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
)
from pydantic.json_schema import JsonSchemaValue
from typing import Any



class _ImVec4PydanticAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
            cls,
            _source_type: Any,
            _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        def validate_from_tuple(value: tuple[float, float, float, float]) -> ImVec4:
            result = ImVec4()
            result.x = value[0]
            result.y = value[1]
            result.z = value[2]
            result.w = value[3]
            return result

        from_tuple_schema = core_schema.chain_schema(
            [
                core_schema.tuple_schema([core_schema.float_schema(), core_schema.float_schema(), core_schema.float_schema(), core_schema.float_schema()]),
                core_schema.no_info_plain_validator_function(validate_from_tuple),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_tuple_schema,
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(ImVec4),
                    from_tuple_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: [instance.x, instance.y, instance.z, instance.w]
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
            cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return handler(core_schema.tuple_schema())

# ImVec4_Pydantic is a synonym for ImVec4, which is compatible with Pydantic
ImVec4_Pydantic = Annotated[
    ImVec4, _ImVec4PydanticAnnotation
]


class _ImVec2PydanticAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
            cls,
            _source_type: Any,
            _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        def validate_from_tuple(value: tuple[float, float]) -> ImVec2:
            result = ImVec2()
            result.x = value[0]
            result.y = value[1]
            return result

        from_tuple_schema = core_schema.chain_schema(
            [
                core_schema.tuple_schema([core_schema.float_schema(), core_schema.float_schema()]),
                core_schema.no_info_plain_validator_function(validate_from_tuple),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_tuple_schema,
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(ImVec2),
                    from_tuple_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: [instance.x, instance.y]
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
            cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return handler(core_schema.tuple_schema())


# ImVec2_Pydantic is a synonym for ImVec2, which is compatible with Pydantic
ImVec2_Pydantic = Annotated[
    ImVec2, _ImVec2PydanticAnnotation
]


class _ImColorPydanticAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
            cls,
            _source_type: Any,
            _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        def validate_from_tuple(value: tuple[float, float, float, float]) -> ImVec4:
            result = ImColor()
            result.value.x = value[0]
            result.value.y = value[1]
            result.value.z = value[2]
            result.value.w = value[3]
            return result

        from_tuple_schema = core_schema.chain_schema(
            [
                core_schema.tuple_schema([core_schema.float_schema(), core_schema.float_schema(), core_schema.float_schema(), core_schema.float_schema()]),
                core_schema.no_info_plain_validator_function(validate_from_tuple),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_tuple_schema,
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(ImVec4),
                    from_tuple_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: [instance.value.x, instance.value.y, instance.value.z, instance.value.w]
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
            cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return handler(core_schema.tuple_schema())

# ImColor_Pydantic is a synonym for ImColor, which is compatible with Pydantic
ImColor_Pydantic = Annotated[
    ImColor, _ImColorPydanticAnnotation
]
