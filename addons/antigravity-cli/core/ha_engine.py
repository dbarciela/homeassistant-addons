"""Main Home Assistant Engine Facade and High-Speed Natural Language Dispatcher."""

import re

# Re-export all sub-module functions for 100% backwards compatibility
from core.ha_client import (
    ALLOWED_CARD_SERVICES,
    _DOMAIN_STATUS_TRIGGERS,
    build_device_cards,
    describe_calls,
    execute_device_control_intent,
    get_device_status_answer,
    get_ha_states,
    get_last_action_entities,
    get_last_playlist_card,
    get_scheduled_controls_answer,
    ha_call_service_api,
    is_scheduled_controls_query,
    is_status_query,
    resolve_pending_playlist_choice,
    resolve_toggle_service,
    run_named_scene_macro,
    run_script_or_scene_intent,
    toggle_automation_intent,
)
from core.renderers import (
    evaluate_room_env_health,
    generate_dynamic_ai_recommendations,
    get_ai_deep_environment_analysis,
    get_comprehensive_home_summary,
    get_metric_status_comment,
)
from core.sensors import (
    ENV_METRIC_CONFIGS,
    classify_sensor,
    get_anniversary_summary,
    get_automations_summary,
    get_dynamic_rooms,
    get_energy_summary,
    get_openings_summary,
    get_presence_summary,
    get_room_env_matrix,
    get_room_env_summary,
    get_room_full_state,
    get_room_lights_summary,
    get_system_health_summary,
    get_todo_summary,
    match_room,
)
from core.session_manager import (
    clear_pending_confirmation,
    clear_pending_playlist_choice,
    get_last_room_context,
    get_pending_confirmation,
    get_pending_playlist_choice,
    set_last_control_targets,
    set_last_room_context,
)
from core.system_info import (
    get_all_addons_memory,
    get_ha_error_logs,
    get_resource_usage,
    get_supervisor_token,
)

# Words that make a room-less follow-up ("습도는?") resolvable via the
# previous turn's room -- deliberately narrower than the generic "상태/상황/
# 어때" words handled later, which already have a sensible room-less meaning
# (whole-home status) that stale room context must not override.
_METRIC_FOLLOWUP_WORDS = [
    "온도", "기온", "습도", "co2", "이산화탄소", "tvoc", "voc", "유기화합물",
    "초미세", "pm25", "pm2.5", "미세먼지", "pm10", "조도", "밝기", "lux", "lx",
    "기압", "압력", "hpa", "공기질", "공기상태", "공기", "환기",
]

# A fan-speed command like "안방 선풍기 50%로 해줘" carries none of the
# 켜/꺼/... control verbs below -- without this, it skipped the whole control
# branch (same "Fallback: comprehensive home summary" failure mode fixed for
# unrecognized light names, see CHANGELOG beta.86).
_PERCENT_PATTERN = re.compile(r"\d{1,3}\s*(?:%|퍼센트|프로)")

# A climate target-temperature command like "안방 에어컨 26도로 맞춰줘" carries
# none of the 켜/꺼/... control verbs below either -- same reasoning as
# _PERCENT_PATTERN above, mirrored in core.ha_client's _TEMPERATURE_RE.
_TEMPERATURE_PATTERN = re.compile(r"\d{1,2}\s*도")

# Outing/sleep-mode shortcut phrases ("나갈게", "잘 자") ported from the
# antigravity_cli HA-Assist conversation agent's old local macro matching
# (see custom_components/.../conversation.py's _handle_special_macros) --
# that local matcher had zero room-scoping/hidden-device/dangerous-switch
# safety and is being retired in favor of always delegating to this engine,
# so these phrase shortcuts need to exist here or they'd simply stop
# working. Deliberately excludes anything from _AFFIRMATIVE_WORDS/verb
# keywords above so it can't misfire on an unrelated command.
_OUTING_MODE_WORDS = ["나갈게", "외출할게", "외출모드", "외출", "나간다"]
_SLEEP_MODE_WORDS = ["잘자", "취침모드", "수면모드", "자러갈게", "안녕히주무세요"]

# Reply words for a pending dangerous-action confirmation (see
# core.ha_client's turn_off gate on APPLIANCE_SWITCH_KEYWORDS and
# core.session_manager.set_pending_confirmation()). Deliberately short,
# unambiguous words only -- anything else is treated as an unrelated new
# command rather than guessed at as a yes/no. Single-character words (어, 노, ...)
# are matched by exact equality only, never as a prefix: as a prefix they're
# common word-starts ("어디야?", "노래 틀어줘") and would silently execute or
# cancel a pending dangerous action in response to an unrelated message.
_AFFIRMATIVE_WORDS = ["네", "예", "응", "어", "그래", "맞아", "확인", "진행", "좋아", "오케이", "ok", "okay", "yes", "y", "sim", "claro", "confirma", "confirm"]
_NEGATIVE_WORDS = ["아니", "아니요", "노", "취소", "그만", "안돼", "안 돼", "no", "n", "não", "nao", "cancela", "cancel"]


def detect_prompt_language(prompt: str) -> str:
    """Detect prompt language ('pt', 'ko', 'es', 'en'). Defaults to 'en' (English-first baseline)."""
    lower = prompt.lower()
    
    # 1. Portuguese keywords and patterns
    pt_keywords = [
        "olá", "ola", "bom dia", "boa tarde", "boa noite", "tudo bem",
        "como está", "como esta", "obrigado", "obrigada", "por favor",
        "ligar", "liga", "desligar", "desliga", "apagar", "apaga",
        "luz", "luzes", "quarto", "sala", "cozinha", "estores", "cortinas",
        "temperatura", "clima", "ar condicionado", "tomada", "interruptor",
        "ajuda", "comandos", "o que podes", "quem és", "estado da casa",
        "tempo", "climatização", "automação", "automações", "cenas", "sim", "não"
    ]
    if any(w in lower for w in pt_keywords):
        return "pt"

    # 2. Korean Hangul check
    if any('\uac00' <= ch <= '\ud7a3' for ch in prompt):
        return "ko"

    # 3. Spanish keywords
    es_keywords = ["hola", "buenos dias", "buenas tardes", "luces", "habitacion", "gracias", "encender", "apagar", "que puedes hacer"]
    if any(w in lower for w in es_keywords):
        return "es"

    # Default baseline is English (English-first)
    return "en"


def handle_agent_chat(
    prompt: str,
    conversation_id: str = "",
    home_summary: str = "",
    is_direct_llm: bool = False,
    is_mobile: bool = False,
) -> str:
    """Dispatches prompt to Antigravity CLI or autonomously resolves intents with responsive markdown."""
    clean_prompt = prompt.strip()
    lower = clean_prompt.lower()
    no_space = clean_prompt.replace(" ", "")
    lang = detect_prompt_language(clean_prompt)

    states = get_ha_states()

    # 0. Reply to a pending dangerous-action confirmation ("보일러 꺼줘" ->
    # warned instead of executed -> this turn's "응"/"아니"). Checked before
    # anything else so a bare yes/no is never mistaken for its own command.
    # Anything that isn't clearly yes or no (including a brand-new, unrelated
    # command) silently drops the stale pending action instead of blocking
    # it -- only an explicit answer should ever execute or cancel it.
    if conversation_id:
        pending = get_pending_confirmation(conversation_id)
        if pending:
            clear_pending_confirmation(conversation_id)
            if any(w == no_space or (len(w) > 1 and no_space.startswith(w)) for w in _AFFIRMATIVE_WORDS):
                targets = pending.get("targets", [])
                captured = []
                for t in targets:
                    data = {k: v for k, v in t.items() if k not in ("domain", "service")}
                    svc = t["service"]
                    if svc == "__toggle__":
                        # A toggle's confirmation was deferred (see
                        # resolve_control_scope()'s hidden-entity gate) --
                        # resolve the real direction from the entity's state
                        # NOW, not from whatever it was when first parsed.
                        entity = next((s for s in states if s.get("entity_id") == t.get("entity_id")), None)
                        svc = resolve_toggle_service(entity, t["domain"]) if entity else "turn_off"
                    ha_call_service_api(t["domain"], svc, data)
                    captured.append((t["domain"], svc, data))
                if targets:
                    set_last_control_targets(conversation_id, [t.get("entity_id") for t in targets if t.get("entity_id")])
                    desc = describe_calls(captured, states, tense='past')
                    if lang == "pt":
                        return f"✅ Confirmado -- {desc}"
                    elif lang == "ko":
                        return f"✅ 확인했습니다 -- {desc}"
                    return f"✅ Confirmed -- {desc}"
                if lang == "pt":
                    return "A ação solicitada foi executada com sucesso."
                elif lang == "ko":
                    return "요청하신 작업을 실행했습니다."
                return "The requested action has been executed."
            if any(w == no_space or (len(w) > 1 and no_space.startswith(w)) for w in _NEGATIVE_WORDS):
                names = pending.get("names", [])
                if lang == "pt":
                    return f"Cancelado. {', '.join(names)} mantidos no estado atual." if names else "Ação cancelada."
                elif lang == "ko":
                    return f"취소했습니다. {', '.join(names)} 그대로 두겠습니다." if names else "취소했습니다."
                return f"Cancelled. {', '.join(names)} left untouched." if names else "Action cancelled."
            # not a yes/no -- fall through and process this as a new command

    # 0.4 Reply to a pending playlist-pick-list ("OO에 음악 틀어줘" -> a list
    # of recent playlists was just offered, by name, in this turn's text --
    # see core.ha_client._h_media()'s wants_playlist_picker branch). Checked
    # early, like the pending-confirmation reply above, so a name like
    # "Favorite Songs" (which names no room/device keyword at all) doesn't
    # fall through every branch below and land on the generic
    # "파악하지 못했습니다" fallback the way it did before this existed.
    if conversation_id:
        playlist_reply = resolve_pending_playlist_choice(clean_prompt, conversation_id)
        if playlist_reply:
            return playlist_reply

    # 0.5 Scheduled (delayed) command list/count query ("예약 실행 목록
    # 보여줘", "예약 몇 개야?"). Checked before the control-verb branch below
    # because such a question can contain "실행", which that branch would
    # otherwise treat as a bare control command with nothing recognized.
    if is_scheduled_controls_query(clean_prompt, no_space):
        return get_scheduled_controls_answer()

    # 0.6 Outing / sleep mode shortcuts ("나갈게", "잘 자") -- ported from the
    # HA-Assist conversation agent's old local macro matching (see
    # core.ha_client.run_named_scene_macro()'s docstring). Neither phrase
    # carries any of branch 1's control-verb keywords, so this has to be
    # its own early branch or these commands would just fall through to
    # the room-query/weather/etc. checks below and land on the unrelated
    # "Fallback" clarifying question.
    if any(w in no_space for w in _OUTING_MODE_WORDS):
        if states:
            return run_named_scene_macro(states, ["외출"], "외출 모드")
    if any(w in no_space for w in _SLEEP_MODE_WORDS):
        if states:
            return run_named_scene_macro(states, ["취침", "수면"], "취침 모드")

    # 1. Status Question vs. Direct Device / Automation / Script Control
    #
    # A status QUESTION ("안방 스탠드 등 켜져있어?") shares the same "켜"/"꺼"
    # substring as a COMMAND ("켜줘"), so it must be told apart before any
    # control branch runs at all -- is_status_query() is that single choke
    # point, checked here AND again inside each control function as defense
    # in depth. Getting this wrong is what previously turned a plain status
    # question into every bedroom light being switched on.
    if is_status_query(clean_prompt, no_space):
        status_result = get_device_status_answer(clean_prompt, states)
        if status_result:
            return status_result
    elif (
        any(ctrl in no_space for ctrl in ["켜", "꺼", "틀어", "시작", "정지", "중지", "멈춰", "일시정지", "닫아", "열어", "작동", "돌려", "실행", "재생", "토글", "반전"])
        or _PERCENT_PATTERN.search(no_space)
        or _TEMPERATURE_PATTERN.search(no_space)
    ):
        # Automation/script intents are tried BEFORE device control. Both only
        # ever engage on their own explicit trigger words ("자동화"/"오토메이션",
        # "실행"/"돌려"/...), so trying them first is safe -- but device control
        # must NOT go first, because it returns an explicit clarifying message
        # (not a silent "") when a device-type word like "환풍기" matches a
        # branch with no candidates, which would otherwise shadow an
        # automation named e.g. "화장실 환풍기 자동" before
        # toggle_automation_intent ever runs.
        auto_result = toggle_automation_intent(clean_prompt, states)
        if auto_result:
            return auto_result
        script_result = run_script_or_scene_intent(clean_prompt, states)
        if script_result:
            return script_result
        ctrl_result = execute_device_control_intent(clean_prompt, states, conversation_id)
        if ctrl_result:
            return ctrl_result

        # A control verb ("켜"/"꺼"/...) was said but none of the three intents
        # above recognized what to act on -- every domain branch inside
        # execute_device_control_intent() (and toggle_automation_intent /
        # run_script_or_scene_intent) only engages on its own curated keyword
        # list, so an entity whose actual name doesn't contain any of those
        # words (e.g. "안방 다운라이트 꺼" before "라이트"/"램프" were added to
        # the light keywords) falls through here with nothing recognized.
        # Without this early return, execution used to continue past this
        # elif into the room-query/weather/etc. checks below, none of which
        # match a bare control command either, and land on the unrelated
        # "Fallback" comprehensive home summary at the bottom of this
        # function -- silently replacing a failed command with an unrelated
        # status briefing. Ask instead of guessing, same principle as
        # resolve_control_scope()'s room/device ambiguity checks.
        if any(w in lower for w in ["olá", "ola", "liga", "ligar", "apaga", "apagar", "luz", "sala", "quarto", "desliga", "desligar"]):
            return (
                "Não consegui identificar qual o dispositivo a ligar ou desligar. "
                "Pode especificar o nome do dispositivo ou divisão? (ex: 'Luz da sala', 'Luz do quarto')"
            )
        return (
            "I could not determine which device to turn on or off. "
            "Could you specify the device name more clearly? (e.g. 'Living room light', 'Bedroom light')"
        )

    # 2. Specific Room Query (ha_list_floors_areas & sensors)
    rooms = get_dynamic_rooms(states)
    matched_room = match_room(rooms, no_space)
    lower_no_space = no_space.lower()

    if not matched_room and conversation_id:
        # A bare follow-up like "습도는?" with no room named -- reuse the room
        # from the previous turn ("안방 온도는?") instead of falling through
        # to a room-less answer. Only for metric-specific wording; see
        # _METRIC_FOLLOWUP_WORDS.
        if any(w in lower_no_space for w in _METRIC_FOLLOWUP_WORDS):
            remembered_room = get_last_room_context(conversation_id)
            if remembered_room and remembered_room in rooms:
                matched_room = remembered_room

    if matched_room and states:
        if conversation_id:
            set_last_room_context(conversation_id, matched_room)
        env_data = get_room_env_matrix(states)
        r_matrix = env_data["matrix"].get(matched_room, {})

        if any(w in no_space for w in ["온도", "기온"]):
            if "temperature" in r_matrix:
                d = r_matrix["temperature"]
                comment = get_metric_status_comment("temperature", d["value"])
                return f"현재 {matched_room}의 온도는 {d['formatted']}입니다. {comment}"
            return f"현재 {matched_room}의 온도 센서 데이터를 찾지 못했습니다."

        if "습도" in no_space:
            if "humidity" in r_matrix:
                d = r_matrix["humidity"]
                comment = get_metric_status_comment("humidity", d["value"])
                return f"현재 {matched_room}의 습도는 {d['formatted']}입니다. {comment}"
            return f"현재 {matched_room}의 습도 센서 데이터를 찾지 못했습니다."

        if any(w in lower for w in ["co2", "이산화탄소"]):
            if "co2" in r_matrix:
                d = r_matrix["co2"]
                comment = get_metric_status_comment("co2", d["value"])
                return f"현재 {matched_room}의 CO2 농도는 {d['formatted']}입니다. {comment}"
            return f"현재 {matched_room}의 CO2 센서 데이터를 찾지 못했습니다."

        if any(w in lower for w in ["tvoc", "voc", "유기화합물"]):
            if "tvoc" in r_matrix:
                d = r_matrix["tvoc"]
                comment = get_metric_status_comment("tvoc", d["value"], d.get("unit", ""))
                return f"현재 {matched_room}의 TVOC 농도는 {d['formatted']}입니다. {comment}"
            return f"현재 {matched_room}의 TVOC 센서 데이터를 찾지 못했습니다."

        if any(w in lower for w in ["초미세", "pm25", "pm2.5"]):
            if "pm25" in r_matrix:
                d = r_matrix["pm25"]
                comment = get_metric_status_comment("pm25", d["value"])
                return f"현재 {matched_room}의 초미세먼지(PM2.5) 농도는 {d['formatted']}입니다. {comment}"
            return f"현재 {matched_room}의 초미세먼지 센서 데이터를 찾지 못했습니다."

        if any(w in lower for w in ["미세먼지", "pm10"]):
            if "pm10" in r_matrix:
                return f"현재 {matched_room}의 미세먼지(PM10) 농도는 {r_matrix['pm10']['formatted']}입니다."
            elif "pm25" in r_matrix:
                d = r_matrix["pm25"]
                comment = get_metric_status_comment("pm25", d["value"])
                return f"현재 {matched_room}의 초미세먼지(PM2.5) 농도는 {d['formatted']}입니다. {comment}"
            return f"현재 {matched_room}의 미세먼지 센서 데이터를 찾지 못했습니다."

        if any(w in lower for w in ["조도", "밝기", "lux", "lx"]):
            if "illuminance" in r_matrix:
                return f"현재 {matched_room}의 조도는 {r_matrix['illuminance']['formatted']}입니다."
            return f"현재 {matched_room}의 조도 센서 데이터를 찾지 못했습니다."

        if any(w in lower for w in ["기압", "압력", "hpa"]):
            if "pressure" in r_matrix:
                return f"현재 {matched_room}의 기압은 {r_matrix['pressure']['formatted']}입니다."
            return f"현재 {matched_room}의 기압 센서 데이터를 찾지 못했습니다."

        if any(w in lower for w in ["공기질", "공기상태", "공기", "환기"]):
            air_parts = []
            for m in ["co2", "tvoc", "pm25", "pm10"]:
                if m in r_matrix:
                    air_parts.append(f"{ENV_METRIC_CONFIGS[m]['label']} {r_matrix[m]['formatted']}")
            health = evaluate_room_env_health(r_matrix)
            if air_parts:
                return f"🍃 **{matched_room} 실내 공기질 현황**\n- 수치: {' | '.join(air_parts)}\n- 진단: **{health}**"
            return f"현재 {matched_room}의 공기질 센서 데이터를 찾을 수 없습니다."

        if any(w in no_space for w in ["상태", "상황", "기기", "모습", "어때"]):
            has_device_trigger = any(
                any(tw in no_space for tw in words)
                for words, _, _ in _DOMAIN_STATUS_TRIGGERS
            )
            if has_device_trigger:
                dev_status = get_device_status_answer(clean_prompt, states)
                if dev_status:
                    return dev_status
            return get_room_full_state(states, matched_room)

    # 3. Automations & Scripts (ha_config_get_automation)
    if any(w in lower for w in ["자동화", "오토메이션", "automation"]):
        if states:
            return get_automations_summary(states)

    # 4. To-Do & Tasks (ha_get_todo)
    if any(w in lower for w in ["할 일", "할일", "투두", "todo", "쇼핑 목록", "장보기"]):
        if states:
            return get_todo_summary(states)

    # 5. System Health & Diagnostics (ha_get_system_health)
    if any(w in lower for w in ["헬스", "건전성", "진단", "health", "점검", "배터리", "업데이트"]):
        if states:
            return get_system_health_summary(states)

    # 6. Weather & Multi-Dimensional Environment Dashboard
    #
    # Uses the richer get_ai_deep_environment_analysis() (outdoor-vs-indoor
    # comparison, per-room health diagnosis, dynamic AI recommendations) --
    # this used to be the exclusive, standalone "AI Deep Brain" mode's own
    # code path, but since it costs nothing extra (same local heuristics, no
    # real LLM call either way) there was no reason to keep it behind a
    # separate mode selector instead of just always giving the better answer.
    if any(w in lower for w in ["날씨", "기상", "일기예보", "온습도", "대시보드"]):
        if states:
            return get_ai_deep_environment_analysis(states, clean_prompt, is_mobile=is_mobile)

    # 7. Air Quality Specific Intents
    if any(w in lower for w in ["공기질", "실내 공기", "공기 상태", "환기 필요", "환기 어때"]):
        if states:
            return get_room_env_summary(states, "air_quality")

    # 8. System Logs (ha_get_logs)
    if any(w in lower for w in ["에러 로그", "오류 로그", "에러 확인", "오류 확인", "시스템 로그", "최근 에러", "로그 확인"]):
        return get_ha_error_logs()

    # 9. Room-by-room / Multi-Metric Summaries
    if any(w in lower for w in ["방별", "방마다", "공간별", "구역별", "각 방", "각방", "전체 방"]):
        if states:
            if any(w in lower for w in ["온도", "기온"]):
                return get_room_env_summary(states, "temperature")
            if "습도" in lower:
                return get_room_env_summary(states, "humidity")
            if any(w in lower for w in ["co2", "이산화탄소"]):
                return get_room_env_summary(states, "co2")
            if any(w in lower for w in ["tvoc", "voc", "유기화합물"]):
                return get_room_env_summary(states, "tvoc")
            if any(w in lower for w in ["초미세", "pm25", "pm2.5"]):
                return get_room_env_summary(states, "pm25")
            if any(w in lower for w in ["미세먼지", "pm10"]):
                return get_room_env_summary(states, "pm10")
            if any(w in lower for w in ["조도", "밝기"]):
                return get_room_env_summary(states, "illuminance")
            if any(w in lower for w in ["기압", "압력"]):
                return get_room_env_summary(states, "pressure")
            if any(w in lower for w in ["공기", "공기질"]):
                return get_room_env_summary(states, "air_quality")
            if any(w in lower for w in ["등", "조명", "불", "전등", "램프", "라이트"]):
                return get_room_lights_summary(states)

    # 10. Direct Metric Queries without room specified
    if states:
        if any(w in lower for w in ["co2", "이산화탄소"]):
            return get_room_env_summary(states, "co2")
        if any(w in lower for w in ["tvoc", "유기화합물"]):
            return get_room_env_summary(states, "tvoc")
        if any(w in lower for w in ["초미세먼지", "초미세", "pm25", "pm2.5"]):
            return get_room_env_summary(states, "pm25")
        if any(w in lower for w in ["미세먼지", "pm10"]):
            return get_room_env_summary(states, "pm10")
        if any(w in lower for w in ["조도", "밝기"]):
            return get_room_env_summary(states, "illuminance")
        if any(w in lower for w in ["기압", "대기압"]):
            return get_room_env_summary(states, "pressure")

    # 11. Resource Usage
    if any(w in lower for w in ["메모리", "램", "ram", "리소스", "cpu", "사양", "memória", "memoria", "recursos", "memory", "resources", "usage"]):
        if any(w in lower for w in ["애드온", "addon", "앱", "add-on"]):
            return get_all_addons_memory()
        usage = get_resource_usage()
        if lang == "pt":
            return (
                f"📊 Utilização de Recursos:\n"
                f"- Add-on Antigravity CLI: {usage['memory_usage']} MB (CPU {usage['cpu_usage']}%)\n"
                f"- Memória Total do Sistema: {usage['used_memory_gb']} GB / {usage['total_memory_gb']} GB ({usage['memory_percent']}%)"
            )
        elif lang == "ko":
            return (
                f"현재 Antigravity CLI 애드온의 메모리 사용량은 {usage['memory_usage']} MB 이며, "
                f"시스템 전체 메모리는 {usage['used_memory_gb']} GB / {usage['total_memory_gb']} GB ({usage['memory_percent']}%) 사용 중입니다."
            )
        return (
            f"📊 System Resource Status:\n"
            f"- Antigravity CLI Add-on: {usage['memory_usage']} MB (CPU {usage['cpu_usage']}%)\n"
            f"- Total System RAM: {usage['used_memory_gb']} GB / {usage['total_memory_gb']} GB ({usage['memory_percent']}%)"
        )

    # 12. Capability & Feature Introduction Intent
    if (
        any(w in no_space for w in ["뭐할수", "뭘할수", "무엇을할수", "무엇을할줄", "어떤기능", "기능소개", "기능안내", "기능알려", "사용법", "도움말", "help", "할수있는", "할수있어", "할수있니", "할줄아는", "할줄알아", "할줄알니", "뭘할줄", "뭐할줄", "ajuda", "comandos", "commands"])
        or (any(w in clean_prompt for w in ["뭐", "뭘", "무엇", "어떤"]) and any(w in clean_prompt for w in ["할 수", "할수", "가능", "도와", "기능", "역할"]))
        or any(phrase in lower for phrase in ["what can you do", "o que podes fazer", "o que você pode fazer", "como usar", "how to use", "commands", "features", "capabilities"])
    ):
        if lang == "pt":
            return (
                "🤖 **Assistente Inteligente Google Antigravity CLI**\n\n"
                "Sou um assistente de IA para monitorizar e controlar a sua casa inteligente no Home Assistant:\n"
                "- 💡 **Controlo de Dispositivos**: Luzes, interruptores, estores/cortinas, climatização, ventoinhas e multimédia\n"
                "- 🍃 **Qualidade do Ar Interior**: Monitorização de CO2, TVOC, PM2.5, PM10, iluminação e pressão com alertas de ventilação\n"
                "- 🌦️ **Meteorologia & Ambiente**: Matriz ambiental detalhada por divisão e previsão exterior\n"
                "- ⚙️ **Diagnóstico do Sistema**: Consumo de CPU/RAM, estado de saúde do HA, baterias e registos de erro\n"
                "- 🤖 **Automações, Scripts e Cenas**: Consulta de estado, ativação/desativação e execução rápida\n"
                "- 📝 **Listas, Presença & Calendário**: Lista de compras, localização da família e eventos\n"
                "- 🚀 **Dois Modos de Execução**: 1) *Fast Control Mode* (respostas locais ultrarrápidas), 2) *CLI Reasoning Mode* (agente de IA completo via MCP)"
            )
        elif lang == "ko":
            return (
                "🤖 **Google Antigravity CLI 스마트홈 어시스턴트 기능 안내**\n\n"
                "저는 집안의 모든 기기를 제어하고 환경을 모니터링하는 AI 에이전트입니다:\n"
                "- 💡 **스마트홈 기기 제어**: 조명, 커튼, 선풍기/환풍기, 가습기/제습기, 보일러/히터/콘센트, 에어컨, TV/스피커 켜기·끄기\n"
                "- 🍃 **다차원 실내 공기질 모니터링**: CO2, TVOC, PM2.5, PM10, 조도, 기압 정밀 분석 및 환기 AI 조언\n"
                "- 🌦️ **실시간 날씨 및 온습도 분석**: 방별 정밀 환경 매트릭스 및 실외 기상 브리핑\n"
                "- ⚙️ **시스템 모니터링 & 진단**: CPU/RAM 리소스, 시스템 헬스체크, 배터리·업데이트 점검, 에러 로그 점검\n"
                "- 🤖 **자동화·스크립트·씬**: 목록 확인, 켜기/끄기, 스크립트·씬 실행\n"
                "- 📝 **To-Do·재실·기념일**: 할 일/쇼핑 목록, 가족 재실 현황, 다가오는 생일·기념일\n"
                "- 🚪 **보안·에너지**: 문/창문 열림, 카메라 상태, 전력·가스 사용량\n"
                "- 🚀 **2가지 실행 모드 지원**: 1) 고속 제어 모드(즉시 기기 제어·조회 + 환경 분석), 2) CLI 추론 모드(공식 agy 기반 실시간 스트리밍)"
            )
        return (
            "🤖 **Google Antigravity CLI Smart Home Assistant Guide**\n\n"
            "I am an AI agent designed to monitor and control all smart devices in your home:\n"
            "- 💡 **Device Control**: Lights, switches, curtains/blinds, climate/AC, fans, media players\n"
            "- 🍃 **Indoor Air Quality**: CO2, TVOC, PM2.5, PM10, illumination, pressure with ventilation alerts\n"
            "- 🌦️ **Real-time Weather & Environment**: Room environment matrix and outdoor forecast\n"
            "- ⚙️ **System Monitoring & Diagnostics**: CPU/RAM usage, system health, batteries, updates, error logs\n"
            "- 🤖 **Automations, Scripts & Scenes**: Query status, toggle, trigger execution\n"
            "- 📝 **To-Do, Presence & Events**: Shopping lists, family presence tracking, upcoming dates\n"
            "- 🚀 **Dual Execution Modes**: 1) Fast Control Mode (instant local control), 2) CLI Reasoning Mode (full AI agent streaming via MCP)"
        )

    # Word-boundary aware greeting check (prevents substrings like 'coisa' matching 'oi')
    prompt_words = set(re.findall(r"[\w]+", lower))
    greeting_words = {"olá", "ola", "oi", "hello", "hi", "hey", "howdy", "greetings", "안녕", "반가워"}
    greeting_phrases = ["bom dia", "boa tarde", "boa noite", "tudo bem", "who are you", "quem és", "quem és tu", "quem e voce", "quem é você", "누구야", "누구세요"]
    if any(gw in prompt_words for gw in greeting_words) or any(gp in lower for gp in greeting_phrases):
        if lang == "pt":
            return "Olá! Sou o assistente Google Antigravity para a sua Smart Home. Como posso ajudar hoje?"
        elif lang == "ko":
            return "안녕하세요! Google Antigravity CLI 어시스턴트입니다. 무엇을 도와드릴까요?"
        return "Hello! I am your Google Antigravity Smart Home Assistant. How can I help you today?"

    # 13. Doors / Windows / Camera Status
    if any(w in no_space for w in ["문열려", "창문열려", "문열림", "창문열림", "문닫혀", "창문닫혀", "카메라", "cctv", "캠상태"]):
        if states:
            return get_openings_summary(states)

    # 14. Presence / Family Member Location
    #
    # "재실"/"누구있어"/... below only catch phrasings with NO one's name in
    # them ("집에 누가 있어?"). A prompt that names a specific family member
    # ("다은이 집에 있어?", "다은 왔어?") named no keyword from that list at
    # all and fell through to the generic "무슨 말씀인지 파악하지 못했습니다"
    # fallback -- even though get_presence_summary() already has per-name
    # matching built in (see its own prompt handling), nothing ever routed
    # a named-person question to it. Gated on an actual registered
    # person.* friendly_name appearing in the prompt (not a bare "있어",
    # which would otherwise collide with unrelated questions like "다은
    # 생일 있어?" -- branch 16 below) plus a home/away word, so this stays
    # narrow to genuine presence questions.
    person_mentioned = any(
        s.get("entity_id", "").startswith("person.")
        and (s.get("attributes", {}).get("friendly_name") or "") in clean_prompt
        for s in (states or [])
    )
    presence_trigger = any(
        w in no_space for w in [
            "재실", "누구있어", "누가있어", "집에누가", "집에누구", "집에있",
            "어디있어", "어디야",
        ]
    ) or (person_mentioned and any(w in no_space for w in ["집에", "왔어", "귀가", "외출", "나갔"]))
    if presence_trigger:
        if states:
            return get_presence_summary(states, clean_prompt)

    # 15. Energy Usage (current sensor values, not long-term statistics)
    if any(w in no_space for w in ["전력사용", "전력량", "가스사용", "가스검침", "가스량", "에너지사용", "에너지"]):
        if states:
            return get_energy_summary(states)

    # 16. Family Anniversaries / Birthdays
    if any(w in no_space for w in ["기념일", "생일", "제사"]):
        if states:
            return get_anniversary_summary(states)

    # 17. Broad Home Status Intent
    #
    # Deliberately NOT get_ai_deep_environment_analysis() here (unlike branch
    # 6 above) -- that function is environment/weather-focused only (temp,
    # humidity, air quality, outdoor comparison) and has no idea about
    # presence, curtains, active fans, or system resources the way
    # get_comprehensive_home_summary() does. A "우리집 상황 어때?" broad-status
    # question needs that wider coverage, so this keeps the fast dispatcher's
    # own existing summary rather than narrowing it to an env-only report.
    if any(w in lower for w in ["상태", "상황", "현황", "요약", "브리핑", "분위기", "어때", "어떠", "어떻", "집안", "우리집", "모습", "status", "estado", "resumo", "briefing", "summary", "casa"]):
        if home_summary:
            return home_summary
        if states:
            return get_comprehensive_home_summary(states, is_mobile=is_mobile)

    # Fallback -- reaching here means NONE of branches 1-17 recognized anything
    if lang == "pt":
        return (
            "Não consegui identificar o comando com precisão. Pode reformular o seu pedido de controlo ou consulta de estado? "
            "(Exemplos: 'Ligar luz da sala', 'Qual é o estado da casa?', 'Como está o tempo?')"
        )
    elif lang == "ko":
        return (
            "무슨 말씀인지 정확히 파악하지 못했습니다. 스마트홈 기기 제어나 상태 조회 관련해서 "
            "다시 말씀해 주시겠어요? (예: '안방 등 켜줘', '우리집 상황 어때', '오늘 날씨 어때')"
        )
    return (
        "I didn't quite catch that. Could you please rephrase your smart home control or status query? "
        "(e.g. 'Turn on living room lights', 'How is the home status?', 'What is the weather today?')"
    )
