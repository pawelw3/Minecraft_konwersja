"""
Testy integracyjne dla Zadania 4 - EP Chunk Parser, Batch Converter, Report Generator

Testy pokrywają:
- EPChunkParser i analizę chunków
- EPBatchConverter z callbackami
- EPReportGenerator
- Pełną integrację end-to-end
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Dodaj src do path
sys.path.insert(0, str(Path(__file__).parents[4]))

from src.converters.enchantingplus import (
    EPChunkParser,
    EPBlockInChunk,
    ChunkAnalysisResult,
    EPBatchConverter,
    BatchConversionStats,
    BatchConversionResult,
    EPReportGenerator,
    convert_world_enchantingplus,
    convert_chunk_enchantingplus,
    generate_conversion_report,
)
from src.converters.enchantingplus.ep_chunk_parser import get_project_root


class TestEPChunkParser:
    """Testy dla EPChunkParser."""
    
    def test_initialization_with_default_path(self):
        """Test inicjalizacji parsera z domyślną ścieżką."""
        parser = EPChunkParser()
        assert parser.world_path.name == 'mapa_1710'
        assert parser.region_path.name == 'region'
    
    def test_initialization_with_custom_path(self):
        """Test inicjalizacji parsera z niestandardową ścieżką."""
        parser = EPChunkParser('/custom/path')
        # Na Windows ścieżka może być zmieniona
        assert 'custom' in str(parser.world_path)
        assert 'path' in str(parser.world_path)
    
    def test_ep_block_in_chunk_creation(self):
        """Test tworzenia EPBlockInChunk."""
        block = EPBlockInChunk(
            x=100, y=64, z=200,
            block_id='EnchantingPlus:enchanting_table',
            block_name='enchanting_table',
            chunk_x=6, chunk_z=12
        )
        
        assert block.absolute_pos == (100, 64, 200)
        assert block.region_pos == (0, 0)  # 6>>5=0, 12>>5=0
        assert block.block_id == 'EnchantingPlus:enchanting_table'
    
    def test_ep_block_in_chunk_to_dict(self):
        """Test eksportu EPBlockInChunk do słownika."""
        block = EPBlockInChunk(
            x=100, y=64, z=200,
            block_id='EnchantingPlus:enchanting_table',
            block_name='enchanting_table',
            chunk_x=6, chunk_z=12,
            tile_entity={'id': 'EnchantingPlus:enchanting_table', 'x': 100}
        )
        
        data = block.to_dict()
        assert data['x'] == 100
        assert data['block_id'] == 'EnchantingPlus:enchanting_table'
        assert data['has_tile_entity'] == True
        assert 'tile_entity_keys' in data
    
    def test_chunk_analysis_result_creation(self):
        """Test tworzenia ChunkAnalysisResult."""
        block = EPBlockInChunk(
            x=100, y=64, z=200,
            block_id='EnchantingPlus:enchanting_table',
            block_name='enchanting_table',
            chunk_x=6, chunk_z=12
        )
        
        result = ChunkAnalysisResult(
            chunk_x=6,
            chunk_z=12,
            ep_blocks=[block],
            total_tile_entities=5
        )
        
        assert result.has_ep_blocks == True
        assert result.to_dict()['ep_blocks_count'] == 1
    
    @patch('src.converters.enchantingplus.ep_chunk_parser.EPChunkParser._get_anvil_parser')
    def test_analyze_chunk_no_ep_blocks(self, mock_get_parser):
        """Test analizy chunka bez bloków EP."""
        # Mock chunk data bez EP TE
        mock_chunk = MagicMock()
        mock_chunk.get_tile_entities.return_value = [
            {'id': 'minecraft:chest', 'x': 100, 'y': 64, 'z': 200},
            {'id': 'minecraft:furnace', 'x': 101, 'y': 64, 'z': 200},
        ]
        
        mock_parser = MagicMock()
        mock_parser.get_chunk.return_value = mock_chunk
        mock_get_parser.return_value = mock_parser
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Utwórz strukturę folderów
            region_dir = Path(tmpdir) / 'region'
            region_dir.mkdir()
            
            # Utwórz mock pliku regionu
            (region_dir / 'r.0.0.mca').touch()
            
            parser = EPChunkParser(tmpdir)
            result = parser.analyze_chunk(0, 0)
            
            assert result.has_ep_blocks == False
            assert result.total_tile_entities == 2
    
    @patch('src.converters.enchantingplus.ep_chunk_parser.EPChunkParser._get_anvil_parser')
    def test_analyze_chunk_with_ep_blocks(self, mock_get_parser):
        """Test analizy chunka z blokami EP."""
        mock_chunk = MagicMock()
        mock_chunk.get_tile_entities.return_value = [
            {'id': 'EnchantingPlus:enchanting_table', 'x': 100, 'y': 64, 'z': 200},
            {'id': 'minecraft:chest', 'x': 101, 'y': 64, 'z': 200},
        ]
        
        mock_parser = MagicMock()
        mock_parser.get_chunk.return_value = mock_chunk
        mock_get_parser.return_value = mock_parser
        
        with tempfile.TemporaryDirectory() as tmpdir:
            region_dir = Path(tmpdir) / 'region'
            region_dir.mkdir()
            (region_dir / 'r.0.0.mca').touch()
            
            parser = EPChunkParser(tmpdir)
            result = parser.analyze_chunk(0, 0)
            
            assert result.has_ep_blocks == True
            assert len(result.ep_blocks) == 1
            assert result.ep_blocks[0].block_id == 'EnchantingPlus:enchanting_table'


class TestEPBatchConverter:
    """Testy dla EPBatchConverter."""
    
    def test_initialization(self):
        """Test inicjalizacji batch convertera."""
        with tempfile.TemporaryDirectory() as tmpdir:
            converter = EPBatchConverter(
                world_path_1710=tmpdir,
                output_path=f"{tmpdir}/output"
            )
            
            assert converter.world_path == Path(tmpdir)
            assert converter.output_path.exists()
    
    def test_progress_callback(self):
        """Test ustawiania callbacku postępu."""
        with tempfile.TemporaryDirectory() as tmpdir:
            converter = EPBatchConverter(tmpdir)
            
            callback = Mock()
            converter.set_progress_callback(callback)
            
            assert converter.progress_callback == callback
            
            # Test wywołania
            converter._report_progress(50, "Test message")
            callback.assert_called_once_with(50, "Test message")
    
    def test_batch_stats_creation(self):
        """Test tworzenia BatchConversionStats."""
        stats = BatchConversionStats()
        
        stats.start()
        assert stats.start_time is not None
        
        stats.add_block('EnchantingPlus:enchanting_table', success=True)
        stats.add_block('EnchantingPlus:advanced_table', success=True)
        stats.add_block('EnchantingPlus:arcane_inscriber', success=True, removed=True)
        
        stats.finish()
        
        assert stats.total_blocks == 3
        assert stats.converted_blocks == 2
        assert stats.removed_blocks == 1
        assert stats.success_rate == 100.0
    
    def test_batch_stats_to_dict(self):
        """Test eksportu statystyk do słownika."""
        stats = BatchConversionStats()
        stats.total_blocks = 10
        stats.converted_blocks = 7
        stats.removed_blocks = 3
        stats.success_rate = 100.0
        stats.duration_seconds = 5.5
        
        data = stats.to_dict()
        
        assert data['total_blocks'] == 10
        assert data['success_rate_percent'] == 100.0
        assert data['duration_seconds'] == 5.5
    
    def test_batch_conversion_result(self):
        """Test tworzenia BatchConversionResult."""
        stats = BatchConversionStats()
        stats.total_blocks = 5
        
        result = BatchConversionResult(
            stats=stats,
            converted_blocks=[],
            output_path="/output/path"
        )
        
        assert result.stats.total_blocks == 5
        assert result.output_path == "/output/path"
    
    @patch('src.converters.enchantingplus.batch_converter.EPChunkParser')
    def test_convert_single_chunk(self, mock_parser_class):
        """Test konwersji pojedynczego chunka."""
        # Mock parser
        mock_block = EPBlockInChunk(
            x=100, y=64, z=200,
            block_id='EnchantingPlus:enchanting_table',
            block_name='enchanting_table',
            chunk_x=6, chunk_z=12,
            tile_entity={'id': 'EnchantingPlus:enchanting_table', 'x': 100}
        )
        
        mock_result = ChunkAnalysisResult(
            chunk_x=6, chunk_z=12,
            ep_blocks=[mock_block],
            total_tile_entities=1
        )
        
        mock_parser = MagicMock()
        mock_parser.analyze_chunk.return_value = mock_result
        mock_parser_class.return_value = mock_parser
        
        with tempfile.TemporaryDirectory() as tmpdir:
            converter = EPBatchConverter(tmpdir)
            results = converter.convert_single_chunk(6, 12)
            
            assert len(results) == 1
            assert results[0].original_id == 'EnchantingPlus:enchanting_table'
            assert results[0].converted.success == True


class TestEPReportGenerator:
    """Testy dla EPReportGenerator."""
    
    def test_initialization(self):
        """Test inicjalizacji generatora."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = EPReportGenerator(f"{tmpdir}/reports")
            assert generator.output_path.exists()
    
    def test_generate_html_report(self):
        """Test generowania raportu HTML."""
        stats = BatchConversionStats()
        stats.total_blocks = 10
        stats.converted_blocks = 7
        stats.removed_blocks = 3
        stats.success_rate = 100.0
        stats.duration_seconds = 5.5
        stats.blocks_by_type = {
            'EnchantingPlus:enchanting_table': 5,
            'EnchantingPlus:advanced_table': 2,
            'EnchantingPlus:arcane_inscriber': 3
        }
        
        result = BatchConversionResult(
            stats=stats,
            converted_blocks=[],
            output_path="/output"
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = EPReportGenerator(f"{tmpdir}/reports")
            path = generator.generate_html_report(result)
            
            assert Path(path).exists()
            content = Path(path).read_text(encoding='utf-8')
            assert 'Enchanting Plus' in content
            assert '100.0%' in content
            assert 'enchanting_table' in content
    
    def test_generate_markdown_report(self):
        """Test generowania raportu Markdown."""
        stats = BatchConversionStats()
        stats.total_blocks = 5
        stats.converted_blocks = 5
        stats.success_rate = 100.0
        
        result = BatchConversionResult(
            stats=stats,
            converted_blocks=[],
            output_path="/output"
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = EPReportGenerator(f"{tmpdir}/reports")
            path = generator.generate_markdown_report(result)
            
            assert Path(path).exists()
            content = Path(path).read_text(encoding='utf-8')
            assert 'Enchanting Plus' in content
            assert '| Całkowita liczba bloków | 5 |' in content
    
    def test_generate_full_report(self):
        """Test generowania wszystkich raportów."""
        stats = BatchConversionStats()
        result = BatchConversionResult(stats=stats, converted_blocks=[])
        
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = EPReportGenerator(f"{tmpdir}/reports")
            reports = generator.generate_full_report(result)
            
            assert 'html' in reports
            assert 'markdown' in reports
            assert Path(reports['html']).exists()
            assert Path(reports['markdown']).exists()


class TestHelperFunctions:
    """Testy funkcji pomocniczych."""
    
    @patch('src.converters.enchantingplus.EPBatchConverter')
    @patch('src.converters.enchantingplus.EPReportGenerator')
    def test_convert_world_enchantingplus(self, mock_generator_class, mock_converter_class):
        """Test funkcji pomocniczej convert_world_enchantingplus."""
        # Mock
        mock_stats = MagicMock()
        mock_stats.to_dict.return_value = {'total_blocks': 10}
        
        mock_result = MagicMock()
        mock_result.stats = mock_stats
        
        mock_converter = MagicMock()
        mock_converter.run_batch_conversion.return_value = mock_result
        mock_converter_class.return_value = mock_converter
        
        mock_generator = MagicMock()
        mock_generator_class.return_value = mock_generator
        
        # Wywołaj
        result = convert_world_enchantingplus(
            'mapa_1710',
            'output/ep',
            progress_callback=Mock(),
            max_regions=5
        )
        
        # Sprawdź
        assert result == {'total_blocks': 10}
        mock_converter.run_batch_conversion.assert_called_once_with(max_regions=5)
    
    @patch('src.converters.enchantingplus.EPBatchConverter')
    def test_convert_chunk_enchantingplus(self, mock_converter_class):
        """Test funkcji pomocniczej convert_chunk_enchantingplus."""
        mock_converter = MagicMock()
        mock_converter.convert_single_chunk.return_value = ['block1', 'block2']
        mock_converter_class.return_value = mock_converter
        
        result = convert_chunk_enchantingplus('mapa_1710', 10, 20)
        
        assert result == ['block1', 'block2']
        mock_converter.convert_single_chunk.assert_called_once_with(10, 20)
    
    @patch('src.converters.enchantingplus.EPReportGenerator')
    def test_generate_conversion_report(self, mock_generator_class):
        """Test funkcji pomocniczej generate_conversion_report."""
        mock_generator = MagicMock()
        mock_generator.generate_html_report.return_value = '/path/to/report.html'
        mock_generator_class.return_value = mock_generator
        
        path = generate_conversion_report('/output', format='html')
        
        assert path == '/path/to/report.html'


class TestEndToEnd:
    """Testy end-to-end całego przepływu."""
    
    def test_full_conversion_flow_mocked(self):
        """Test pełnego przepływu konwersji z mockowanymi danymi."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Utwórz strukturę świata
            region_dir = Path(tmpdir) / 'region'
            region_dir.mkdir(parents=True)
            (region_dir / 'r.0.0.mca').touch()
            
            # Utwórz batch converter
            converter = EPBatchConverter(
                world_path_1710=tmpdir,
                output_path=f"{tmpdir}/output"
            )
            
            # Sprawdź że output path został utworzony
            assert converter.output_path.exists()
            
            # Test generowania podsumowania
            summary = converter.generate_summary_report()
            assert 'ENCHANTING PLUS' in summary
            assert 'enchanting_table' in summary


def main():
    """Uruchomienie testów z verbose output."""
    pytest.main([__file__, '-v', '--tb=short'])


if __name__ == '__main__':
    main()
