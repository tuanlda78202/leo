from typing import Any

from opik.evaluation.metrics import base_metric, score_result


class SummaryHeuristic(base_metric.BaseMetric):
    """
    A metric that evaluates whether an LLM's output has appropriate length and density.

    This metric uses an heuristic to determine if the output length is appropriate for the given instruction.
    It returns a normalized score between 0 and 1, where:
    - 0.0 (Poor): Output is either too short and incomplete, or too long with unnecessary information
    - 0.5 (Good): Output has decent length balance but still slightly too short or too long
    - 1.0 (Excellent): Output length is appropriate, answering the question concisely without being verbose
    """

    def __init__(
        self,
        name: str = "summary_heuristic",
        min_length: int = 128,
        max_length: int = 1024,
    ) -> None:
        self.name = name
        self.min_length = min_length
        self.max_length = max_length

    def score(
        self, input: str, output: str, **ignored_kwargs: Any
    ) -> score_result.ScoreResult:
        """
        Score the output of an LLM.

        Args:
            input: The input prompt given to the LLM.
            output: The output of an LLM to score.
            **ignored_kwargs: Any additional keyword arguments.

        Returns:
            ScoreResult: The computed score with explanation.
        """

        length_score = self._compute_length_score(output)

        reason = f"Output length: {len(output)} chars. "
        if length_score == 1.0:
            reason += "Length is within ideal range."
        elif length_score >= 0.5:
            reason += "Length is slightly outside ideal range."
        else:
            reason += "Length is significantly outside ideal range."

        return score_result.ScoreResult(
            name=self.name,
            value=length_score,
            reason=reason,
        )

    def _compute_length_score(self, text: str) -> float:
        """
        Compute a score based on text length relative to min and max boundaries.

        Args:
            text: The text to evaluate.

        Returns:
            float: A score between 0 and 1, where:
                - 0.0: Text length is significantly outside the boundaries
                - 0.5: Text length is slightly outside the boundaries
                - 1.0: Text length is within the ideal range
        """
        length = len(text)

        # If length is within bounds, return perfect score
        if self.min_length <= length <= self.max_length:
            return 1.0

        if length < self.min_length:
            deviation = (self.min_length - length) / self.min_length
        else:
            deviation = (length - self.max_length) / self.max_length

        # Convert deviation to a score between 0 and 1
        # deviation <= 0.5 -> score between 0.5 and 1.0
        # deviation > 0.5 -> score between 0.0 and 0.5
        score = max(0.0, 1.0 - deviation)

        return score
