"""Tests for domain routing policy."""

from langchain_core.messages import AIMessage, HumanMessage

from jayce.domain.routing import RoutingPolicy
from jayce.domain.state import State


class TestRoutingPolicyDirect:
    """Tests for messages that should route to direct_llm."""

    def test_healthcheck_oi(self) -> None:
        state = State(messages=[HumanMessage("oi")])
        assert RoutingPolicy.should_route_direct(state) is True
        assert RoutingPolicy.route(state) == "direct_llm"

    def test_healthcheck_ping(self) -> None:
        state = State(messages=[HumanMessage("ping")])
        assert RoutingPolicy.should_route_direct(state) is True

    def test_healthcheck_ok(self) -> None:
        state = State(messages=[HumanMessage("ok")])
        assert RoutingPolicy.should_route_direct(state) is True

    def test_healthcheck_strips_whitespace(self) -> None:
        state = State(messages=[HumanMessage("  OI  ")])
        assert RoutingPolicy.should_route_direct(state) is True

    def test_healthcheck_tudo_bem(self) -> None:
        state = State(messages=[HumanMessage("tudo bem")])
        assert RoutingPolicy.should_route_direct(state) is True


class TestRoutingPolicyTools:
    """Tests for messages that should route to call_llm."""

    def test_normal_question(self) -> None:
        state = State(messages=[HumanMessage("pesquise sobre python")])
        assert RoutingPolicy.should_route_direct(state) is False
        assert RoutingPolicy.route(state) == "call_llm"

    def test_empty_messages(self) -> None:
        state = State(messages=[])
        assert RoutingPolicy.should_route_direct(state) is False

    def test_last_message_not_human(self) -> None:
        state = State(messages=[AIMessage(content="response")])
        assert RoutingPolicy.should_route_direct(state) is False

    def test_list_content(self) -> None:
        state = State(messages=[HumanMessage(content=["part1", "part2"])])
        assert RoutingPolicy.should_route_direct(state) is False
