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

# Profile paragraphs for the About section.
PROFILE = [
    "I am Huynh Phan Gia Bao, an undergraduate researcher in Information Security at the "
    "University of Information Technology (UIT), Vietnam National University Ho Chi Minh City. "
    "My work sits where cryptography meets distributed systems: I study how independent "
    "blockchains can talk to each other without handing trust to a single bridge, relay or operator.",
    "Most of my research tackles concrete weaknesses in cross-chain infrastructure, such as "
    "linkability in hash time-locked contracts, fragile single-relay designs and credentials that "
    "leak more than they prove. I build protocols that combine zero-knowledge proofs, "
    "market-based relaying and formal verification, and I test them as working prototypes, "
    "not only as proofs on paper.",
    "Beyond interoperability, I work on decentralized identity and reputation: soulbound "
    "credentials, reputation-weighted consensus for education networks, and trust models that "
    "adapt to evidence over time. The goal behind all of it is simple to state and hard to reach: "
    "systems that stay trustworthy even when nobody in them has to be trusted.",
]

# Rotating quotes: (text, author, source).
QUOTES = [
    ("The root problem with conventional currency is all the trust that's required to make it work.",
     "Satoshi Nakamoto", "P2P Foundation, 2009"),
    ("Privacy is necessary for an open society in the electronic age.",
     "Eric Hughes", "A Cypherpunk's Manifesto, 1993"),
    ("Whereas most technologies tend to automate workers on the periphery doing menial tasks, "
     "blockchains automate away the center.",
     "Vitalik Buterin", None),
    ("Security is a process, not a product.",
     "Bruce Schneier", None),
    ("Don't trust. Verify.",
     "Bitcoin community maxim", None),
]

# Research areas: (title, blurb, color).
RESEARCH = [
    ("Cross-Chain Interoperability",
     "Trust-minimized bridges, multi-relay markets and atomic swaps that do not leak who traded with whom.",
     "yellow"),
    ("Zero-Knowledge Proofs",
     "Privacy-preserving verification across consortium and public chains, from HTLCs to credentials.",
     "blue"),
    ("Smart Contract Security",
     "Finding and formally ruling out the bugs that turn contracts into open vaults.",
     "red"),
    ("Decentralized Identity & Reputation",
     "Soulbound credentials, evidence-driven trust dynamics and reputation-weighted consensus.",
     "lime"),
]

ADVISOR = dict(
    name="Tran Tuan Dung",
    name_vi="Trần Tuấn Dũng",
    title="M.Sc. · Lecturer",
    unit="Faculty of Computer Networks and Communications · Information Security Lab",
    org="University of Information Technology, VNU-HCM",
    blurb=(
        "My research advisor. Mr. Dung teaches information security at UIT and leads a group of "
        "student researchers working on blockchain security, cross-chain interoperability, "
        "AI security & privacy, IoT and distributed computing, and has mentored UIT students "
        "presenting blockchain research at international venues such as CSoNet and ICISN."
    ),
    interests=["Blockchain Security", "Cross-Chain", "AI Security & Privacy", "IoT", "Distributed Computing"],
    links=[
        ("Google Scholar", "https://scholar.google.com/citations?user=zaJ7ZE4AAAAJ"),
        ("UIT profile", "https://nc.uit.edu.vn/en/giang-vien/tran-tuan-dung"),
    ],
    # Matches the advisor in author lists, to count joint papers.
    author_key="TD Tran",
)
