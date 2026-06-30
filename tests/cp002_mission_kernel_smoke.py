from platform_domain.mission import (
    Mission,
    MissionContext,
    MissionHealth,
    MissionStage,
    MissionStatus,
)


def test_mission_can_be_created():
    mission = Mission(
        id="mission-001",
        title="Build Viabil",
        objective="Create a real estate feasibility system.",
    )

    assert mission.id == "mission-001"
    assert mission.status == MissionStatus.DRAFT
    assert mission.stage == MissionStage.DRAFT


def test_mission_summary_contract():
    mission = Mission(
        id="mission-002",
        title="Brand Foundation",
        objective="Define COS positioning.",
    )

    summary = mission.summary()

    assert summary.id == mission.id
    assert summary.title == mission.title
    assert summary.objective == mission.objective
    assert summary.status == MissionStatus.DRAFT
    assert summary.stage == MissionStage.DRAFT


def test_mission_stage_advancement_sets_active_status():
    mission = Mission(
        id="mission-003",
        title="Mission Kernel",
        objective="Introduce Mission as domain entity.",
    )

    mission.advance_to(MissionStage.DISCOVERY)

    assert mission.stage == MissionStage.DISCOVERY
    assert mission.status == MissionStatus.ACTIVE


def test_mission_context_is_available():
    context = MissionContext(
        domain="real_estate",
        workspace_id="workspace-001",
        owner_id="owner-001",
        tags=["viabil", "feasibility"],
    )

    mission = Mission(
        id="mission-004",
        title="Real Estate Feasibility",
        objective="Evaluate a project.",
        context=context,
    )

    assert mission.context.domain == "real_estate"
    assert "viabil" in mission.context.tags


def test_mission_health_validates_bounds():
    health = MissionHealth(progress=0.5, confidence=0.8, open_risks=2)

    assert health.progress == 0.5
    assert health.confidence == 0.8
    assert health.open_risks == 2
