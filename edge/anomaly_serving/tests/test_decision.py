import math

import pytest
import torch

from anomaly_serving.rad_model.decision import (
    MEAN_TOP_FRACTION,
    PERCENTILE,
    RAW_SCORE,
    compute_score,
    decide,
    normalize_confidence,
    resolve_decision_param,
)


class TestComputeScore:
    def test_raw_score_returns_the_single_worst_pixel(self):
        # Given
        anomaly_map = torch.tensor([[0.1, 0.2], [0.9, 0.3]])

        # When
        actual_score = compute_score(anomaly_map, RAW_SCORE, param=0.0)

        # Then
        assert actual_score == pytest.approx(0.9)

    def test_mean_top_fraction_averages_the_requested_top_slice(self):
        # Given 100 pixels with values 0..99, the top 10% are 90..99 (mean 94.5)
        anomaly_map = torch.arange(100, dtype=torch.float32)

        # When
        actual_score = compute_score(anomaly_map, MEAN_TOP_FRACTION, param=0.10)

        # Then
        assert actual_score == pytest.approx(94.5)

    def test_mean_top_fraction_keeps_at_least_one_pixel_for_tiny_fractions(self):
        # Given a fraction so small that the top-k count rounds down to zero
        anomaly_map = torch.arange(100, dtype=torch.float32)

        # When
        actual_score = compute_score(anomaly_map, MEAN_TOP_FRACTION, param=0.0001)

        # Then the single worst pixel is used rather than an empty mean
        assert actual_score == pytest.approx(99.0)

    def test_percentile_returns_the_requested_quantile(self):
        # Given
        anomaly_map = torch.arange(101, dtype=torch.float32)

        # When
        actual_score = compute_score(anomaly_map, PERCENTILE, param=0.99)

        # Then
        assert actual_score == pytest.approx(99.0)

    def test_percentile_differs_from_mean_top_fraction_on_a_heavy_tail(self):
        # Given a distribution whose extreme tail is far above its 99th percentile
        anomaly_map = torch.cat([torch.zeros(990), torch.full((10,), 100.0)])

        # When
        percentile_score = compute_score(anomaly_map, PERCENTILE, param=0.99)
        mean_top_score = compute_score(anomaly_map, MEAN_TOP_FRACTION, param=0.01)

        # Then the two methods are genuinely distinct, not aliases
        assert mean_top_score == pytest.approx(100.0)
        assert percentile_score < mean_top_score

    def test_score_is_shape_agnostic(self):
        # Given the same pixels arranged as 2D and as a flat vector
        flat = torch.tensor([0.1, 0.4, 0.6, 0.9])
        square = flat.reshape(2, 2)

        # When / Then
        assert compute_score(square, RAW_SCORE, 0.0) == compute_score(flat, RAW_SCORE, 0.0)

    def test_unknown_method_is_rejected(self):
        with pytest.raises(ValueError, match="Unknown decision_method"):
            compute_score(torch.zeros(4), "median", param=0.5)

    def test_empty_map_is_rejected(self):
        with pytest.raises(ValueError, match="empty anomaly map"):
            compute_score(torch.empty(0), RAW_SCORE, param=0.0)

    @pytest.mark.parametrize("param", [0.0, -0.1, 1.5])
    def test_mean_top_fraction_rejects_out_of_range_fractions(self, param):
        with pytest.raises(ValueError, match="fraction in"):
            compute_score(torch.zeros(4), MEAN_TOP_FRACTION, param=param)

    @pytest.mark.parametrize("param", [-0.1, 1.5])
    def test_percentile_rejects_out_of_range_quantiles(self, param):
        with pytest.raises(ValueError, match="quantile in"):
            compute_score(torch.zeros(4), PERCENTILE, param=param)


class TestDecide:
    def test_score_below_threshold_is_ok(self):
        assert decide(0.2, threshold=0.5) == "OK"

    def test_score_above_threshold_is_ko(self):
        assert decide(0.8, threshold=0.5) == "KO"

    def test_score_exactly_at_threshold_is_ko(self):
        assert decide(0.5, threshold=0.5) == "KO"


class TestNormalizeConfidence:
    def test_zero_score_maps_to_zero(self):
        assert normalize_confidence(0.0, threshold=0.4) == pytest.approx(0.0)

    def test_threshold_maps_to_the_midpoint(self):
        # The OK/KO flip lines up with the displayed percentage crossing 50%
        assert normalize_confidence(0.4, threshold=0.4) == pytest.approx(0.5)

    def test_twice_the_threshold_saturates(self):
        assert normalize_confidence(0.8, threshold=0.4) == pytest.approx(1.0)

    def test_scores_beyond_twice_the_threshold_are_clipped(self):
        assert normalize_confidence(99.0, threshold=0.4) == pytest.approx(1.0)

    def test_result_always_within_unit_range(self):
        for score in (-1.0, 0.0, 0.1, 0.5, 1.0, 1e6):
            actual = normalize_confidence(score, threshold=0.3)
            assert 0.0 <= actual <= 1.0
            assert not math.isnan(actual)

    def test_non_positive_threshold_degrades_gracefully(self):
        # A zero threshold makes every non-zero score KO; avoid dividing by zero
        assert normalize_confidence(0.5, threshold=0.0) == pytest.approx(1.0)
        assert normalize_confidence(0.0, threshold=0.0) == pytest.approx(0.0)


class TestResolveDecisionParam:
    def test_explicit_param_is_kept(self):
        assert resolve_decision_param(MEAN_TOP_FRACTION, 0.05) == pytest.approx(0.05)

    def test_mean_top_fraction_defaults_to_one_percent(self):
        assert resolve_decision_param(MEAN_TOP_FRACTION, None) == pytest.approx(0.01)

    def test_percentile_defaults_to_p99(self):
        assert resolve_decision_param(PERCENTILE, None) == pytest.approx(0.99)

    def test_unknown_method_is_rejected(self):
        with pytest.raises(ValueError, match="Unknown decision_method"):
            resolve_decision_param("median", None)
