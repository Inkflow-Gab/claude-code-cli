"""Tests for the messaging slash commands (/stats, /stop, /clear).

These cover the reply-scoped versus standalone branches, the confirmation
decision in ``StopOutcome.requires_confirmation``, and numeric-first message
deletion ordering.
"""

from typing import Any

import pytest

from free_claude_code.messaging.command_context import (
    ReplyClearResult,
    StopOutcome,
)
from free_claude_code.messaging.command_dispatcher import (
    dispatch_command,
    parse_command_base,
)
from free_claude_code.messaging.commands import (
    handle_clear_command,
    handle_stats_command,
    handle_stop_command,
)
from free_claude_code.messaging.models import IncomingMessage, MessageScope
from free_claude_code.messaging.transcript import RenderCtx

SCOPE = MessageScope(platform="telegram", chat_id="42")


class FakeOutbound:
    """Record outbound sends and deletes for assertions."""

    def __init__(self, *, delete_error: Exception | None = None) -> None:
        self.sent: list[dict[str, Any]] = []
        self.deleted: list[dict[str, Any]] = []
        self.edited: list[dict[str, Any]] = []
        self._delete_error = delete_error
        self._next_id = 100

    async def queue_send_message(
        self,
        chat_id: str,
        text: str,
        reply_to: str | None = None,
        parse_mode: str | None = None,
        fire_and_forget: bool = True,
        message_thread_id: str | None = None,
    ) -> str:
        self._next_id += 1
        self.sent.append(
            {
                "chat_id": chat_id,
                "text": text,
                "reply_to": reply_to,
                "parse_mode": parse_mode,
                "fire_and_forget": fire_and_forget,
                "message_thread_id": message_thread_id,
            }
        )
        return str(self._next_id)

    async def queue_edit_message(
        self,
        chat_id: str,
        message_id: str,
        text: str,
        parse_mode: str | None = None,
        fire_and_forget: bool = True,
    ) -> None:
        self.edited.append({"chat_id": chat_id, "message_id": message_id})

    async def queue_delete_messages(
        self,
        chat_id: str,
        message_ids: list[str],
        fire_and_forget: bool = True,
    ) -> None:
        if self._delete_error is not None:
            raise self._delete_error
        self.deleted.append(
            {"chat_id": chat_id, "message_ids": list(message_ids)}
        )

    def fire_and_forget(self, task: Any) -> None: ...


class FakeCliManager:
    def get_stats(self) -> dict:
        return {"active_sessions": 3}


class FakeContext:
    """Minimal ``MessagingCommandContext`` implementation."""

    def __init__(
        self,
        *,
        stop_all: StopOutcome | None = None,
        stop_reply_result: StopOutcome | None = None,
        clear_reply_result: ReplyClearResult | None = None,
        clear_chat_result: frozenset[str] = frozenset(),
        tree_count: int = 5,
        outbound: FakeOutbound | None = None,
    ) -> None:
        self.outbound = outbound or FakeOutbound()
        self.cli_manager = FakeCliManager()
        self._stop_all = stop_all or StopOutcome(0, frozenset(), False)
        self._stop_reply = stop_reply_result or StopOutcome(0, frozenset(), False)
        self._clear_reply = clear_reply_result
        self._clear_chat = clear_chat_result
        self._tree_count = tree_count
        self.forgotten: list[set[str]] = []
        self.recorded: list[tuple[str, str, str | None, str]] = []
        self.stop_all_calls = 0
        self.stop_reply_calls: list[tuple[MessageScope, str]] = []
        self.clear_reply_calls: list[tuple[MessageScope, str]] = []

    def format_status(
        self, emoji: str, label: str, suffix: str | None = None
    ) -> str:
        return f"{emoji} {label}" + (f" {suffix}" if suffix else "")

    def get_render_ctx(self) -> RenderCtx:
        return RenderCtx(
            bold=lambda t: f"**{t}**",
            code_inline=lambda t: f"`{t}`",
            escape_code=lambda t: t,
            escape_text=lambda t: t,
            render_markdown=lambda t: t,
        )

    async def stop_all_tasks(self) -> StopOutcome:
        self.stop_all_calls += 1
        return self._stop_all

    async def stop_reply(self, scope: MessageScope, reply_id: str) -> StopOutcome:
        self.stop_reply_calls.append((scope, reply_id))
        return self._stop_reply

    def get_tree_count(self) -> int:
        return self._tree_count

    async def clear_reply(
        self, scope: MessageScope, reply_id: str
    ) -> ReplyClearResult | None:
        self.clear_reply_calls.append((scope, reply_id))
        return self._clear_reply

    async def clear_chat(self, platform: str, chat_id: str) -> frozenset[str]:
        return self._clear_chat

    async def forget_tracked_message_ids(
        self, platform: str, chat_id: str, message_ids: set[str]
    ) -> None:
        self.forgotten.append(set(message_ids))

    async def record_outgoing_message(
        self, platform: str, chat_id: str, msg_id: str | None, kind: str
    ) -> bool:
        self.recorded.append((platform, chat_id, msg_id, kind))
        return True


def message(
    text: str = "/stop",
    *,
    reply_to: str | None = None,
    message_id: str = "10",
    message_thread_id: str | None = None,
) -> IncomingMessage:
    return IncomingMessage(
        text=text,
        chat_id="42",
        user_id="7",
        message_id=message_id,
        platform="telegram",
        reply_to_message_id=reply_to,
        message_thread_id=message_thread_id,
    )


def cancelled(count: int, *, scope: MessageScope = SCOPE, fallback: bool = False):
    """A stop outcome that cancelled ``count`` tasks with terminal feedback."""

    return StopOutcome(
        cancelled_count=count,
        status_feedback_scopes=frozenset({scope}),
        fallback_required=fallback,
    )


class TestParseCommandBase:
    def test_plain_command(self):
        assert parse_command_base("/stats") == "/stats"

    def test_strips_bot_mention(self):
        assert parse_command_base("/stats@my_bot arg") == "/stats"

    def test_empty_and_none(self):
        assert parse_command_base(None) == ""
        assert parse_command_base("") == ""
        assert parse_command_base("   ") == ""


class TestDispatch:
    @pytest.mark.asyncio
    async def test_known_command_is_handled(self):
        ctx = FakeContext()
        assert await dispatch_command(ctx, message("/stats"), "/stats") is True

    @pytest.mark.asyncio
    async def test_unknown_command_is_not_handled(self):
        ctx = FakeContext()
        assert await dispatch_command(ctx, message("/nope"), "/nope") is False
        assert ctx.outbound.sent == []


class TestStats:
    @pytest.mark.asyncio
    async def test_reports_sessions_and_trees(self):
        ctx = FakeContext(tree_count=4)
        await handle_stats_command(ctx, message("/stats"))

        assert len(ctx.outbound.sent) == 1
        text = ctx.outbound.sent[0]["text"]
        assert "Stats" in text
        assert "3" in text
        assert "4" in text
        assert ctx.recorded[0][3] == "command"

    @pytest.mark.asyncio
    async def test_uses_a_waiting_send(self):
        ctx = FakeContext()
        await handle_stats_command(ctx, message("/stats"))
        assert ctx.outbound.sent[0]["fire_and_forget"] is False


class TestStop:
    @pytest.mark.asyncio
    async def test_standalone_stops_everything(self):
        # Complete terminal feedback means no redundant summary line.
        ctx = FakeContext(stop_all=cancelled(3))
        await handle_stop_command(ctx, message("/stop"))

        assert ctx.stop_all_calls == 1
        assert ctx.stop_reply_calls == []
        assert ctx.outbound.sent == []

    @pytest.mark.asyncio
    async def test_standalone_summarizes_partial_feedback(self):
        ctx = FakeContext(stop_all=cancelled(3, fallback=True))
        await handle_stop_command(ctx, message("/stop"))

        assert ctx.stop_all_calls == 1
        assert "3" in ctx.outbound.sent[0]["text"]
        assert "pending or active" in ctx.outbound.sent[0]["text"]

    @pytest.mark.asyncio
    async def test_standalone_reports_nothing_to_stop(self):
        ctx = FakeContext(stop_all=StopOutcome(0, frozenset(), False))
        await handle_stop_command(ctx, message("/stop"))

        assert "Nothing to stop" in ctx.outbound.sent[0]["text"]

    @pytest.mark.asyncio
    async def test_standalone_skips_message_when_feedback_is_complete(self):
        # Cancelled work that already has terminal status needs no extra line.
        ctx = FakeContext(stop_all=cancelled(2))
        await handle_stop_command(ctx, message("/stop"))
        assert ctx.outbound.sent == []

    @pytest.mark.asyncio
    async def test_standalone_sends_when_fallback_required(self):
        ctx = FakeContext(stop_all=cancelled(2, fallback=True))
        await handle_stop_command(ctx, message("/stop"))
        assert "2" in ctx.outbound.sent[0]["text"]

    @pytest.mark.asyncio
    async def test_reply_scopes_to_one_task(self):
        ctx = FakeContext(stop_reply_result=cancelled(1))
        await handle_stop_command(ctx, message("/stop", reply_to="55"))

        assert ctx.stop_reply_calls == [(SCOPE, "55")]
        assert ctx.stop_all_calls == 0

    @pytest.mark.asyncio
    async def test_reply_uses_singular_noun(self):
        ctx = FakeContext(stop_reply_result=cancelled(1, fallback=True))
        await handle_stop_command(ctx, message("/stop", reply_to="55"))
        assert "1 request" in ctx.outbound.sent[0]["text"]

    @pytest.mark.asyncio
    async def test_reply_uses_plural_noun(self):
        ctx = FakeContext(stop_reply_result=cancelled(4, fallback=True))
        await handle_stop_command(ctx, message("/stop", reply_to="55"))
        assert "4 requests" in ctx.outbound.sent[0]["text"]

    @pytest.mark.asyncio
    async def test_reply_reports_nothing_matched(self):
        ctx = FakeContext(stop_reply_result=StopOutcome(0, frozenset(), False))
        await handle_stop_command(ctx, message("/stop", reply_to="55"))

        assert "Nothing to stop for that message" in ctx.outbound.sent[0]["text"]
        assert ctx.stop_all_calls == 0


class TestClear:
    @pytest.mark.asyncio
    async def test_reply_deletes_only_that_subtree(self):
        ctx = FakeContext(
            clear_reply_result=ReplyClearResult(
                delete_message_ids=frozenset({"55", "56"}),
                tree_matched=True,
            )
        )
        await handle_clear_command(ctx, message("/clear", reply_to="55"))

        assert ctx.clear_reply_calls == [(SCOPE, "55")]
        deleted = ctx.outbound.deleted[0]["message_ids"]
        # The invoking command message is included and forgotten.
        assert set(deleted) == {"55", "56", "10"}
        assert ctx.forgotten == [{"55", "56", "10"}]

    @pytest.mark.asyncio
    async def test_reply_without_match_reports_nothing_to_clear(self):
        ctx = FakeContext(clear_reply_result=None)
        await handle_clear_command(ctx, message("/clear", reply_to="55"))

        assert "Nothing to clear for that message" in ctx.outbound.sent[0]["text"]
        assert ctx.outbound.deleted == []

    @pytest.mark.asyncio
    async def test_standalone_clears_whole_chat(self):
        ctx = FakeContext(clear_chat_result=frozenset({"1", "2", "3"}))
        await handle_clear_command(ctx, message("/clear"))

        assert set(ctx.outbound.deleted[0]["message_ids"]) == {"1", "2", "3", "10"}

    @pytest.mark.asyncio
    async def test_delete_order_is_numeric_descending(self):
        ctx = FakeContext(clear_chat_result=frozenset({"2", "100", "9"}))
        await handle_clear_command(ctx, message("/clear"))

        ids = ctx.outbound.deleted[0]["message_ids"]
        numeric = [i for i in ids if i.isdigit()]
        assert numeric == ["100", "10", "9", "2"]

    @pytest.mark.asyncio
    async def test_non_numeric_ids_sort_last(self):
        ctx = FakeContext(clear_chat_result=frozenset({"abc", "5"}))
        await handle_clear_command(ctx, message("/clear"))

        # "10" is the invoking command message, so numeric IDs sort descending
        # ahead of the non-numeric "abc".
        ids = ctx.outbound.deleted[0]["message_ids"]
        assert ids == ["10", "5", "abc"]

    @pytest.mark.asyncio
    async def test_delete_failure_does_not_raise(self):
        ctx = FakeContext(
            clear_chat_result=frozenset({"1"}),
            outbound=FakeOutbound(delete_error=OSError("no permission")),
        )
        await handle_clear_command(ctx, message("/clear"))

    @pytest.mark.asyncio
    async def test_empty_chat_deletes_nothing(self):
        ctx = FakeContext(clear_chat_result=frozenset())
        await handle_clear_command(ctx, message("/clear"))

        # The command message itself still needs removing.
        assert ctx.outbound.deleted[0]["message_ids"] == ["10"]


class TestRequiresConfirmation:
    def test_zero_cancellations_always_need_confirmation(self):
        outcome = StopOutcome(0, frozenset({SCOPE}), False)
        assert outcome.requires_confirmation(SCOPE) is True

    def test_complete_feedback_skips_confirmation(self):
        outcome = StopOutcome(2, frozenset({SCOPE}), False)
        assert outcome.requires_confirmation(SCOPE) is False

    def test_fallback_flag_forces_confirmation(self):
        outcome = StopOutcome(2, frozenset({SCOPE}), True)
        assert outcome.requires_confirmation(SCOPE) is True

    def test_other_scope_forces_confirmation(self):
        other = MessageScope(platform="telegram", chat_id="99")
        outcome = StopOutcome(2, frozenset({SCOPE}), False)
        assert outcome.requires_confirmation(other) is True
