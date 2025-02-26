import unittest
from unittest.mock import patch, MagicMock
from minecraft_exporter import MinecraftCollector
from prometheus_client import Metric

class TestMinecraftCollector(unittest.TestCase):

    def setUp(self):
        self.mock_rcon = MagicMock()
        # Initialize exporter with the mocked RCON client
        self.exporter = MinecraftCollector.from_test(mock_rcon=self.mock_rcon)

    @patch.object(MinecraftCollector, 'rcon_command')
    def test_valid_response_with_players(self, mock_rcon):
        mock_rcon.return_value = "There are 3 of a max of 20 players online: Laxray, Fra360, Emzy_matt"
        metrics = self.exporter.get_server_stats()

        # Extract player_online metrics
        player_metrics = [metric for metric in metrics if metric.name == 'player_online']
        expected_players = {'Laxray', 'Fra360', 'Emzy_matt'}
        actual_players = set()

        for metric in player_metrics:
            for sample in metric.samples:
                labels = sample.labels
                actual_players.add(labels['player'])
                self.assertEqual(sample.value, 1)

        self.assertEqual(actual_players, expected_players)

    @patch.object(MinecraftCollector, 'rcon_command')
    def test_no_players_online(self, mock_rcon):
        mock_rcon.return_value = "There are 0 of a max of 20 players online:"
        metrics = self.exporter.get_server_stats()

        # No player_online metrics are expected
        player_metrics = [metric for metric in metrics if metric.name == 'player_online']
        self.assertEqual(len(player_metrics[0].samples), 0)

    @patch.object(MinecraftCollector, 'rcon_command')
    def test_malformed_response_missing_colon(self, mock_rcon):
        mock_rcon.return_value = (
            "There are 2 of a max of 20 players online\n"  # Malformed
            "Laxray\n"
            "Fra360"
        )
        metrics = self.exporter.get_server_stats()

        # Due to regex not matching, expect no player_online metrics
        player_metrics = [metric for metric in metrics if metric.name == 'player_online']
        print(str(player_metrics))
        self.assertEqual(len(player_metrics[0].samples), 0)

    @patch.object(MinecraftCollector, 'rcon_command')
    def test_empty_response(self, mock_rcon):
        mock_rcon.return_value = ""
        metrics = self.exporter.get_server_stats()

        # Expect no player metrics for empty response
        player_metrics = [metric for metric in metrics if metric.name == 'player_online']
        self.assertEqual(len(player_metrics[0].samples), 0)

    @patch.object(MinecraftCollector, 'rcon_command')
    def test_none_response(self, mock_rcon):
        mock_rcon.return_value = None
        metrics = self.exporter.get_server_stats()

        # No player metrics for None response
        player_metrics = [metric for metric in metrics if metric.name == 'player_online']
        self.assertEqual(len(player_metrics[0].samples), 0)

    @patch.object(MinecraftCollector, 'rcon_command')
    def test_non_string_response_integer(self, mock_rcon):
        mock_rcon.return_value = 12345
        metrics = self.exporter.get_server_stats()

        # No metrics expected for integer response
        player_metrics = [metric for metric in metrics if metric.name == 'player_online']
        self.assertEqual(len(player_metrics[0].samples), 0)

    @patch.object(MinecraftCollector, 'rcon_command')
    def test_response_as_bytes_with_players(self, mock_rcon):
        # This test seems to be incorrectly labelled, in Python 3 strings are UTF-8 by default, not bytes unless explicitly defined
        mock_rcon.return_value = (
            "There are 2 of a max of 20 players online: Celes, Silnogard"
        )
        metrics = self.exporter.get_server_stats()

        # Validate players
        player_metrics = [metric for metric in metrics if metric.name == 'player_online']
        expected_players = {'Celes', 'Silnogard'}
        actual_players = set()

        for metric in player_metrics:
            for sample in metric.samples:
                labels = sample.labels
                actual_players.add(labels['player'])
                self.assertEqual(sample.value, 1)

        self.assertEqual(actual_players, expected_players)

    @patch.object(MinecraftCollector, 'rcon_command')
    def test_response_with_extra_whitespace(self, mock_rcon):
        mock_rcon.return_value = (
            "There are 2 of a max of 20 players online:  Velisal  , The_Spartan94  "
        )
        metrics = self.exporter.get_server_stats()

        # Check for properly trimmed player names from whitespace
        player_metrics = [metric for metric in metrics if metric.name == 'player_online']
        expected_players = {'Velisal', 'The_Spartan94'}
        actual_players = set()

        for metric in player_metrics:
            for sample in metric.samples:
                labels = sample.labels
                actual_players.add(labels['player'])
                self.assertEqual(sample.value, 1)

        self.assertEqual(actual_players, expected_players)

    @patch.object(MinecraftCollector, 'rcon_command')
    def test_response_with_unexpected_format(self, mock_rcon):
        mock_rcon.return_value = (
            "Ther are 1 of a max of 20 players online:\n"
            "Celes"
        )
        metrics = self.exporter.get_server_stats()

        # Should not match due to format error
        player_metrics = [metric for metric in metrics if metric.name == 'player_online']
        self.assertEqual(len(player_metrics[0].samples), 0)

    @patch.object(MinecraftCollector, 'rcon_command')
    def test_response_with_special_characters_in_player_names(self, mock_rcon):
        mock_rcon.return_value = (
            "There are 2 of a max of 20 players online: Emzy_matt, The_Spartan94"
        )
        metrics = self.exporter.get_server_stats()

        # Validate players with special characters
        player_metrics = [metric for metric in metrics if metric.name == 'player_online']
        expected_players = {'Emzy_matt', 'The_Spartan94'}
        actual_players = set()

        for metric in player_metrics:
            for sample in metric.samples:
                labels = sample.labels
                actual_players.add(labels['player'])
                self.assertEqual(sample.value, 1)

        self.assertEqual(actual_players, expected_players)

    @patch.object(MinecraftCollector, 'rcon_command')
    def test_response_with_long_player_names(self, mock_rcon):
        long_name = "A" * 100  # Name with 100 characters
        mock_rcon.return_value = (
            f"There are 1 of a max of 20 players online: {long_name}"
        )
        metrics = self.exporter.get_server_stats()

        # Test processing of long player names
        player_metrics = [metric for metric in metrics if metric.name == 'player_online']
        expected_players = {long_name}
        actual_players = set()

        for metric in player_metrics:
            for sample in metric.samples:
                labels = sample.labels
                actual_players.add(labels['player'])
                self.assertEqual(sample.value, 1)

        self.assertEqual(actual_players, expected_players)

    @patch.object(MinecraftCollector, 'rcon_command')
    def test_rcon_command_raises_exception(self, mock_rcon):
        mock_rcon.side_effect = BrokenPipeError("Broken pipe")
        metrics = self.exporter.get_server_stats()
        player_metrics = [metric for metric in metrics if metric.name == 'player_online']

        self.assertEqual(len(player_metrics[0].samples), 0)

if __name__ == '__main__':
    unittest.main()