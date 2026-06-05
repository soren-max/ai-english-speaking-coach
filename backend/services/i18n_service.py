"""I18nService — Multi-language support for international users.

Provides Chinese hints and translations for key interview concepts.
Interview remains in English; hints help Chinese-speaking users understand
expectations and improve their responses.
"""

from typing import Dict, List, Optional

# ── Interview terminology (EN → ZH) ──

TERMS: Dict[str, str] = {
    "interview": "面试",
    "self-introduction": "自我介绍",
    "behavioral question": "行为面试题",
    "technical question": "技术面试题",
    "system design": "系统设计",
    "algorithm": "算法",
    "data structure": "数据结构",
    "STAR method": "STAR法则",
    "Situation": "情境",
    "Task": "任务",
    "Action": "行动",
    "Result": "结果",
    "strength": "优势",
    "weakness": "劣势",
    "leadership principle": "领导力准则",
    "trade-off": "权衡",
    "scalability": "可扩展性",
    "latency": "延迟",
    "throughput": "吞吐量",
    "consistency": "一致性",
    "availability": "可用性",
    "feedback": "反馈",
    "improvement": "改进建议",
    "fluency": "流利度",
    "grammar": "语法",
    "vocabulary": "词汇量",
    "communication": "沟通能力",
}

# ── Stage hints (ZH) ──

STAGE_HINTS: Dict[int, Dict[str, str]] = {
    1: {
        "title": "Stage 1: 自我介绍",
        "hint": "用 2-3 分钟介绍你的背景、技术栈和最有成就感的项目。",
        "tip": "重点突出与目标岗位相关的经验，不要背诵简历。",
    },
    2: {
        "title": "Stage 2: 项目经验",
        "hint": "选择一个最能体现你技术深度的项目详细讲解。",
        "tip": "使用 STAR 法则组织回答：情境→任务→行动→结果。",
    },
    3: {
        "title": "Stage 3: 技术深挖",
        "hint": "面试官会深入追问技术细节，评估你的真实水平。",
        "tip": "如果不确定，可以说 'I would approach it by...' 展示思考过程。",
    },
    4: {
        "title": "Stage 4: 系统设计",
        "hint": "设计一个大规模系统，考察架构能力和工程思维。",
        "tip": "先说需求估算，再画高層架構，最后深入细节。",
    },
    5: {
        "title": "Stage 5: 行为面试",
        "hint": "考察软技能：团队合作、冲突处理、领导力。",
        "tip": "用具体例子回答，说明你做了什么和学到了什么。",
    },
}

# ── Common phrases (EN → ZH) ──

PHRASES: Dict[str, str] = {
    "Tell me about yourself": "请介绍一下你自己",
    "Why do you want this job": "你为什么想要这份工作",
    "What is your greatest strength": "你最大的优势是什么",
    "What is your biggest weakness": "你最大的劣势是什么",
    "Describe a challenge you faced": "描述你遇到过的挑战",
    "Where do you see yourself in 5 years": "你未来五年的规划是什么",
    "Why should we hire you": "为什么我们应该录用你",
    "Do you have any questions": "你有什么问题要问我们吗",
}

# ── Company-specific hints (ZH) ──

COMPANY_TIPS: Dict[str, Dict[str, str]] = {
    "Google": {
        "focus": "算法和系统设计并重",
        "tip": "Google 看重解题思路和代码质量，面试时要主动沟通思考过程。",
    },
    "Amazon": {
        "focus": "领导力准则（Leadership Principles）",
        "tip": "Amazon 面试 80% 是行为面试，所有回答都要体现领导力准则。",
    },
    "Tencent": {
        "focus": "产品思维 + 技术深度",
        "tip": "腾讯面试重视产品感和落地能力，技术问题常结合具体业务场景。",
    },
    "Microsoft": {
        "focus": "算法 + 系统设计",
        "tip": "微软面试注重解决问题的结构化思维，多轮技术面+AA面。",
    },
    "Meta": {
        "focus": "系统设计 + 算法",
        "tip": "Meta 面试看重工程速度和质量，系统设计题比重很高。",
    },
}


def translate_term(term: str) -> Optional[str]:
    """Translate an interview term to Chinese."""
    return TERMS.get(term.lower())


def get_stage_hint(stage: int, lang: str = "zh") -> Optional[Dict[str, str]]:
    """Get hints for an interview stage in the requested language."""
    if lang == "zh":
        return STAGE_HINTS.get(stage)
    return None


def translate_phrase(phrase: str) -> Optional[str]:
    """Translate a common interview phrase to Chinese."""
    for en, zh in PHRASES.items():
        if en.lower() in phrase.lower():
            return zh
    return None


def get_company_tip(company: str) -> Optional[Dict[str, str]]:
    """Get interview tips for a specific company."""
    return COMPANY_TIPS.get(company)


def list_supported_companies() -> List[str]:
    """List companies with available interview tips."""
    return list(COMPANY_TIPS.keys())


def hint_for_question(question: str) -> Optional[str]:
    """Generate a Chinese hint for any interview question.

    Uses keyword matching to provide relevant tips.
    """
    q = question.lower()

    if "design" in q:
        return "系统设计题：先澄清需求 → 估算流量 → 设计核心组件 → 讨论权衡"
    if any(w in q for w in ["algorithm", "implement", "code", "write"]):
        return "算法题：先明确输入输出 → 讨论复杂度 → 写代码 → 测试边界条件"
    if any(w in q for w in ["introduce", "yourself", "background"]):
        return "自我介绍：2分钟内说完，重点是与岗位相关的经验"
    if any(w in q for w in ["project", "built", "developed"]):
        return "项目介绍：用 STAR 法则，重点说你个人的技术贡献"
    if any(w in q for w in ["why", "motivation", "interest"]):
        return "动机题：结合公司业务和个人职业规划来回答"
    if any(w in q for w in ["weakness", "strength"]):
        return "优缺点题：优点要具体，缺点要说正在改进"
    if any(w in q for w in ["conflict", "challenge", "fail", "mistake"]):
        return "行为题：用 STAR 法则，重点说你从中学到了什么"
    if any(w in q for w in ["team", "collaboration", "lead"]):
        return "团队题：用具体例子说明你在团队中的角色和贡献"

    return None
