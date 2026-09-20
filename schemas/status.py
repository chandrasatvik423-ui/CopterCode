from pydantic import BaseModel, Field
from enum import Enum
from typing import List

class PipelineState(str, Enum):
    INITIALIZED = "INITIALIZED"
    INPUT_INVALID = "INPUT_INVALID"
    INPUT_INCOMPLETE = "INPUT_INCOMPLETE"
    TOPOLOGY_UNSUPPORTED = "TOPOLOGY_UNSUPPORTED"
    GEOMETRY_INVALID = "GEOMETRY_INVALID"
    COLLISION_DETECTED = "COLLISION_DETECTED"
    DFM_FAILED = "DFM_FAILED"
    STRUCTURAL_SCREENING_FAILED = "STRUCTURAL_SCREENING_FAILED"
    INSUFFICIENT_THRUST = "INSUFFICIENT_THRUST"
    UNVERIFIED_PROVENANCE = "UNVERIFIED_PROVENANCE"
    NO_FEASIBLE_GEOMETRY = "NO_FEASIBLE_GEOMETRY"
    STRUCTURAL_SCREENING_PASSED = "STRUCTURAL_SCREENING_PASSED"

class StatusAuthority(BaseModel):
    state: PipelineState = Field(default=PipelineState.INITIALIZED)
    blocking_reasons: List[str] = Field(default_factory=list)
    generate_flight_candidate_stl: bool = Field(default=False)
    export_filename: str = Field(default="REJECTED_INITIALIZED.stl")

    def fail_closed(self, new_state: PipelineState, reason: str, filename: str):
        """First-failure-wins monotonic enforcement.
        Once a failure state is set it cannot be silently overwritten.
        Subsequent calls append the reason for diagnostics but keep the original state.
        """
        if self.state == PipelineState.INITIALIZED:
            # First failure — set the primary state
            self.state = new_state
            self.export_filename = filename
        # Always record every blocking reason regardless of which failure fired first
        self.blocking_reasons.append(reason)
        self.generate_flight_candidate_stl = False

    def pass_screening(self, filename: str):
        """Only permits PASSED if no blocking reasons exist at all."""
        if not self.blocking_reasons and self.state == PipelineState.INITIALIZED:
            self.state = PipelineState.STRUCTURAL_SCREENING_PASSED
            self.generate_flight_candidate_stl = True
            self.export_filename = filename