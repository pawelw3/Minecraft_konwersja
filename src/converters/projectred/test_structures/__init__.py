"""
ProjectRed Test Structures

Generator i definicje struktur testowych dla konwersji ProjectRed.
"""

from .structure_generator import (
    ProjectRedTestStructureGenerator,
    TestStructure,
    StructureType,
    BlockDefinition,
    MultipartDefinition,
    CommandBlockDef
)

__all__ = [
    'ProjectRedTestStructureGenerator',
    'TestStructure',
    'StructureType',
    'BlockDefinition',
    'MultipartDefinition',
    'CommandBlockDef'
]
