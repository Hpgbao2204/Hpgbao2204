"""Profile content. Edit this file, then run `python3 scripts/build.py`
to regenerate every SVG in assets/ and the README."""

NAME_TOP = "BAO"
NAME_BOTTOM = "HUYNH"
FULL_NAME = "Huynh Phan Gia Bao"
ROLE = "Blockchain Security Researcher"
AFFILIATION = "UIT · VNU-HCM"
LOCATION = "Ho Chi Minh City, VN"

# Rotating tagline under the name in the header.
TAGLINES = [
    "smart contract security",
    "cross-chain interoperability",
    "zero-knowledge proofs",
    "decentralized identity & reputation",
]

MOTTO = "building trust in a trustless world"

# Pseudo-contract shown in the About card: (type, field, value).
ABOUT = [
    ("string", "role", '"Blockchain Security Researcher"'),
    ("string", "base", '"UIT, VNU-HCM - Ho Chi Minh City"'),
    ("uint16", "born", "2005"),
]

# One floating layer each in the About card (keep labels <= 16 chars).
FOCUS = ["Smart Contracts", "Zero-Knowledge", "Cross-Chain", "Identity & Rep"]

LINKS = [
    ("GOOGLE SCHOLAR", "https://scholar.google.com/citations?user=koh0HscAAAAJ", "yellow"),
    ("ORCID", "https://orcid.org/0009-0008-8773-0482", "lime"),
    ("GITHUB", "https://github.com/hpgbao2204", "blue"),
    ("FACEBOOK", "https://www.facebook.com/baolodc2005", "pink"),
]

SCHOLAR = "https://scholar.google.com/citations?user=koh0HscAAAAJ"
CITATIONS = 10  # total on Google Scholar, shown as "10+"

# Me, as written in author lists (highlighted on the cards).
ME = ("B Huynh", "HPG Bao")

# Newest first. kind: journal | conference | article
PUBLICATIONS = [
    dict(
        year=2026, kind="journal",
        title="zk-HTLC: A formally verified defense against linkability attacks in trust-minimized cross-chain networks",
        authors="TD Tran, B Huynh, VH Pham",
        venue="Computer Networks, 112780",
        url=None,
    ),
    dict(
        year=2026, kind="journal",
        title="ChronosRep: Entropy-regularized evidence fusion and stochastic differential trust dynamics for decentralized identity intelligence",
        authors="TD Tran, B Huynh, VH Pham",
        venue="Information Sciences, 123323",
        url="https://doi.org/10.1016/j.ins.2026.123323",
    ),
    dict(
        year=2026, kind="conference",
        title="Verifiable AI Reviewers: Decentralized Skill Matching and Soulbound Reputation for Multi-Agent Peer Review",
        authors="TM Trong, B Huynh, HN Nhi, TT Nguyen, NP Tai, N Minh, TD Tran, et al.",
        venue="Intl. Conf. on Multimedia Analysis and Pattern Recognition (MAPR 2026)",
        url=None,
    ),
    dict(
        year=2025, kind="journal",
        title="Acheron: A market-based multi-relay architecture for adaptive and secure cross-chain communication",
        authors="TD Tran, Q Vu, B Huynh, VH Pham",
        venue="Internet of Things, 101836",
        url="https://doi.org/10.1016/j.iot.2025.101836",
    ),
    dict(
        year=2025, kind="journal",
        title="DAVE-CC: A decentralized, access-controlled, verifiable ecosystem for cross-chain academic credential management",
        authors="TD Tran, HPG Bao, NT Cam, VH Pham",
        venue="Journal of Information Security and Applications 94, 104238",
        url="https://doi.org/10.1016/j.jisa.2025.104238",
    ),
    dict(
        year=2025, kind="article",
        title="ZK-InterChain: Privacy-Preserving Protocol for Cross-Chain Interactions Between Consortium and Public Blockchains",
        authors="TD Tran, TT Kien, B Huynh",
        venue=None,
        url=None,
    ),
    dict(
        year=2025, kind="conference",
        title="Proof-of-Merit: A Reputation-Weighted VRF-PoA Consensus and Governance for Educational Blockchains",
        authors="TD Tran, B Huynh, TM Trong, TT Nguyen, NN BK, VH Pham",
        venue="RIVF Intl. Conf. on Computing and Communication Technologies (IEEE)",
        url="https://doi.org/10.1109/rivf68649.2025.11365043",
    ),
    dict(
        year=2025, kind="conference",
        title="Lotus: A Hybrid Cross-Chain Framework for Privacy-Preserving Digital Identity",
        authors="TD Tran, HPG Bao, TM Trong, NT Cam, VH Pham",
        venue="24th Intl. Symposium on Communications and Information Technologies (ISCIT, IEEE)",
        url="https://doi.org/10.1109/iscit67082.2025.11231625",
    ),
]

# Tech stack rows: (label, color, [items]).
STACK = [
    ("CONTRACTS & ZK", "yellow", ["Solidity", "Rust", "Move", "Circom"]),
    ("CHAINS & INTEROP", "red", ["Ethereum", "Polkadot", "Cosmos", "Solana", "LayerZero"]),
    ("GENERAL", "blue", ["Python", "TypeScript", "JavaScript", "Go", "C/C++", "Ruby", "LaTeX"]),
]

GITHUB_USER = "hpgbao2204"


# ------------------------------------------------------------- website only --
# Used by scripts/build_site.py (the README ignores these).

SITE_URL = "https://hpgbao2204.github.io/Hpgbao2204/"
EMAIL = None  # e.g. "you@example.com" to show a mail button on the site

PHOTO = "img/bao.jpg"  # relative to site/

# Profile paragraphs for the About section.
PROFILE = [
    "I am Huynh Phan Gia Bao, an Information Security undergraduate researcher at the "
    "University of Information Technology (UIT), VNU-HCM. I study how independent blockchains "
    "can interoperate without handing trust to a single bridge, relay or operator.",
    "My work combines zero-knowledge proofs, market-based relaying and formal verification to fix "
    "concrete weaknesses in cross-chain systems, and extends to decentralized identity and "
    "reputation: soulbound credentials, reputation-weighted consensus and evidence-driven trust.",
]

# Rotating quotes: (text, author).
QUOTES = [
    ("The root problem with conventional currency is all the trust that's required to make it work.",
     "Satoshi Nakamoto"),
    ("Privacy is necessary for an open society in the electronic age.",
     "Eric Hughes, A Cypherpunk's Manifesto"),
    ("Blockchains automate away the center.",
     "Vitalik Buterin"),
    ("Security is a process, not a product.",
     "Bruce Schneier"),
    ("Don't trust. Verify.",
     "Bitcoin maxim"),
]

# Research areas: (title, blurb, color).
RESEARCH = [
    ("Cross-Chain Interoperability", "Trust-minimized bridges, multi-relay markets, unlinkable swaps.", "yellow"),
    ("Zero-Knowledge Proofs", "Private verification across consortium and public chains.", "blue"),
    ("Smart Contract Security", "Finding and formally ruling out exploitable bugs.", "red"),
    ("Identity & Reputation", "Soulbound credentials and evidence-driven trust.", "lime"),
]

LAB = dict(
    name="Blockchainist Research Group",
    url="https://blockchainist.id.vn/",
    tagline="Advancing blockchain research for trustworthy digital systems.",
    org="School of Computer Networks and Communications, UIT",
)

ADVISOR = dict(
    name="Tran Tuan Dung",
    name_vi="Trần Tuấn Dũng",
    photo="img/advisor.jpg",  # relative to site/
    title="M.Sc. · Lecturer · PI of Blockchainist",
    org="School of Computer Networks and Communications, UIT · VNU-HCM",
    blurb=(
        "My research advisor. His research spans blockchain and smart contracts, network security, "
        "IoT and edge computing with digital twins, and AI for security and privacy."
    ),
    interests=["Blockchain & Smart Contracts", "Network Security", "IoT & Digital Twins", "AI Security & Privacy"],
    email="dungtrt@uit.edu.vn",
    links=[
        ("Google Scholar", "https://scholar.google.com/citations?user=zaJ7ZE4AAAAJ"),
        ("UIT profile", "https://nc.uit.edu.vn/en/giang-vien/tran-tuan-dung"),
    ],
    # Matches the advisor in author lists, to count joint papers.
    author_key="TD Tran",
)
